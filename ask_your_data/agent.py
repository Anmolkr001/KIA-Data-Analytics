"""
Core LangChain Query Agent for Ask Your Data.
Implements the full 5-step agent flow:
1. Plan: Break down questions into steps
2. Query: Generate and run sandboxed pandas code
3. Self-Check: Validate, diagnose, and retry (up to 3 attempts)
4. Chart: Create interactive Plotly specifications
5. Business Summary: 2-3 plain-language sentences + 1 actionable recommendation
"""

import json
import re
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ask_your_data.config import SYSTEM_PROMPT, get_llm
from ask_your_data.data_loader import load_dataset, format_schema_for_prompt
from ask_your_data.memory import ConversationMemory
from ask_your_data.logger import log_query_interaction
from ask_your_data.tools import (
    describe_schema,
    run_pandas_query,
    make_chart,
    get_latest_query_df,
    get_latest_chart_spec,
    set_latest_query_df,
    set_latest_chart_spec,
    DEALERSHIP_PALETTE,
)
from ask_your_data.sandbox import SandboxedPandasExecutor, ExecutionResult


@dataclass
class AgentResponse:
    """Structured response from the Ask Your Data agent."""
    question: str
    plan: str
    code: str
    attempts: int
    success: bool
    df_result: Optional[pd.DataFrame] = None
    chart_spec: Optional[Dict[str, Any]] = None
    summary: str = ""
    recommendation: str = ""
    assumptions: str = ""
    error: Optional[str] = None
    latency_ms: float = 0.0

    def how_i_got_this(self) -> str:
        """Markdown details for the expandable transparency section."""
        lines = [
            f"### Planning Steps\n{self.plan}\n",
            f"### Generated Python/Pandas Code\n```python\n{self.code.strip()}\n```\n",
            f"**Execution Status:** {'[Success]' if self.success else '[Failed]'} (Attempts: {self.attempts})\n"
        ]
        if self.assumptions:
            lines.append(f"**Assumptions Made:** {self.assumptions}\n")
        return "\n".join(lines)


class AskYourDataAgent:
    """Natural Language Analytics Agent for Car Dealership CRM Data."""

    def __init__(
        self,
        provider: Optional[str] = None,
        memory: Optional[ConversationMemory] = None,
    ):
        self.llm = get_llm(provider)
        self.memory = memory or ConversationMemory()
        self.executor = SandboxedPandasExecutor()
        self.df = load_dataset()

    def _extract_json_or_code(self, response_text: str) -> Dict[str, Any]:
        """Extracts JSON block or parses plan and python code from LLM text."""
        # Try finding markdown json block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except Exception:
                pass

        # Try parsing bare JSON
        try:
            return json.loads(response_text.strip())
        except Exception:
            pass

        # Fallback: extract python code block
        code_match = re.search(r"```python\s*(.*?)\s*```", response_text, re.DOTALL)
        code = code_match.group(1) if code_match else response_text

        # Extract plan if mentioned
        plan_match = re.search(r"(?:Plan|Steps):\s*(.*?)(?:```|$)", response_text, re.DOTALL | re.IGNORECASE)
        plan = plan_match.group(1).strip() if plan_match else "1. Inspect schema.\n2. Filter and aggregate data."

        return {
            "plan": plan,
            "code": code.strip(),
            "chart": {"chart_type": "bar"},
        }

    def _check_result_plausibility(self, exec_result: ExecutionResult) -> Tuple[bool, str]:
        """
        Self-check step: Evaluates whether the query output is valid,
        non-empty, and mathematically plausible.
        """
        if not exec_result.success:
            return False, f"Query failed with error: {exec_result.error}"

        df_res = exec_result.df_result
        if df_res is None or df_res.empty:
            return False, "Query executed but returned 0 rows (empty dataset). Please check column filters and casing."

        # Check for implausible negative values in count or rate columns
        for col in df_res.select_dtypes(include=["number"]).columns:
            col_clean = col.lower()
            is_rate_col = (
                ("rate" in col_clean or "pct" in col_clean or "percentage" in col_clean or "%" in col_clean)
                and not ("count" in col_clean or col_clean == "conversions" or col_clean.endswith("_count"))
            )
            if is_rate_col:
                # Rates between 0 and 100 or 0 and 1
                if (df_res[col] < 0).any():
                    return False, f"Negative conversion rate found in column '{col}', which is mathematically impossible."
                if (df_res[col] > 100).any():
                    return False, f"Conversion rate exceeds 100% in column '{col}'."

            if "count" in col_clean or "leads" in col_clean or "deliveries" in col_clean or col_clean == "conversions":
                if (df_res[col] < 0).any():
                    return False, f"Negative counts detected in column '{col}'."

        return True, "Result passed self-check validation."

    def ask(self, question: str) -> AgentResponse:
        """
        Executes the full agent workflow:
        Plan -> Query -> Self-Check (up to 3 retries) -> Chart -> Business Summary.
        """
        start_time = time.time()
        schema_prompt = format_schema_for_prompt(df=self.df)
        memory_context = self.memory.get_context_for_prompt()

        attempts = 0
        max_attempts = 3
        last_error = ""
        current_code = ""
        current_plan = ""
        chart_info: Dict[str, Any] = {}
        exec_result: Optional[ExecutionResult] = None

        # -------------------------------------------------------------
        # Step a & b: Plan + Query with Self-Check Retry Loop (Step c)
        # -------------------------------------------------------------
        while attempts < max_attempts:
            attempts += 1

            if attempts == 1:
                # First attempt
                user_prompt = (
                    f"Dataset Schema and Business Semantics:\n{schema_prompt}\n\n"
                    f"{memory_context}\n\n"
                    f"Manager Question: {question}\n\n"
                    "INSTRUCTIONS:\n"
                    "1. First write a clear 2-3 step Plan to answer the question.\n"
                    "2. Generate Python/pandas code that operates on 'df' and assigns the final DataFrame or summary to 'result'.\n"
                    "3. Suggest an appropriate chart type ('bar', 'line', 'pie', 'donut') and specify x_col and y_col.\n"
                    "4. If the question is ambiguous, specify your assumption explicitly.\n"
                    "Format your response strictly as valid JSON with keys: "
                    "'plan', 'code', 'chart', 'assumptions'."
                )
            else:
                # Retry prompt with self-correction feedback
                user_prompt = (
                    f"RETRY ATTEMPT {attempts} of {max_attempts}.\n"
                    f"The previous query encountered an issue:\n"
                    f"Problem: {last_error}\n\n"
                    f"Previous Code Attempted:\n```python\n{current_code}\n```\n\n"
                    f"Dataset Schema Reference:\n{schema_prompt}\n\n"
                    f"Manager Question: {question}\n\n"
                    "Please diagnose why the previous query failed or returned an empty/implausible result, "
                    "correct the column names or filtering logic, and return revised JSON with keys: "
                    "'plan', 'code', 'chart', 'assumptions'."
                )

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]

            llm_response = self.llm.invoke(messages)
            parsed = self._extract_json_or_code(llm_response.content)

            current_plan = parsed.get("plan", "1. Query CRM dataset.\n2. Summarize key conversion metrics.")
            current_code = parsed.get("code", "")
            chart_info = parsed.get("chart", {})
            assumptions = parsed.get("assumptions", "")

            # Execute code in restricted sandbox
            exec_result = self.executor.run(current_code, self.df)

            # Self-check validity
            is_valid, diag_message = self._check_result_plausibility(exec_result)
            if is_valid:
                # Success! Break out of retry loop
                break
            else:
                last_error = diag_message

        # Store latest result in tool cache
        if exec_result and exec_result.df_result is not None:
            set_latest_query_df(exec_result.df_result, current_code)

        # -------------------------------------------------------------
        # Step d: Choose an appropriate Plotly chart
        # -------------------------------------------------------------
        chart_spec: Optional[Dict[str, Any]] = None
        if exec_result and exec_result.success and exec_result.df_result is not None and not exec_result.df_result.empty:
            df_res = exec_result.df_result
            ctype = chart_info.get("chart_type", "bar")
            x_col = chart_info.get("x_col", df_res.columns[0] if len(df_res.columns) > 0 else None)
            y_col = chart_info.get("y_col", df_res.columns[1] if len(df_res.columns) > 1 else None)
            color_col = chart_info.get("color_col")
            title = chart_info.get("title", f"{question} — Chart")
            orientation = chart_info.get("orientation", "v")

            # Fallback smart heuristics if keys are missing
            if x_col not in df_res.columns and len(df_res.columns) > 0:
                x_col = df_res.columns[0]
            if y_col and y_col not in df_res.columns:
                num_cols = df_res.select_dtypes(include=["number"]).columns.tolist()
                y_col = num_cols[0] if num_cols else None

            # Generate chart via make_chart tool
            make_chart.invoke({
                "chart_type": ctype,
                "x_col": str(x_col),
                "y_col": str(y_col) if y_col else None,
                "color_col": str(color_col) if color_col else None,
                "title": title,
                "orientation": orientation,
            })
            chart_spec = get_latest_chart_spec()

        # -------------------------------------------------------------
        # Step e: Write Business Summary (2-3 sentences + 1 recommendation)
        # -------------------------------------------------------------
        summary_text = ""
        rec_text = ""
        if exec_result and exec_result.success and exec_result.df_result is not None:
            preview_table = exec_result.df_result.head(10).to_markdown(index=False)
            summary_prompt = (
                f"Manager Question: {question}\n\n"
                f"Query Result Data:\n{preview_table}\n\n"
                "INSTRUCTIONS for Business Summary:\n"
                "1. CRITICAL: In your very first sentence under FINDINGS, directly and explicitly answer the user's question with the exact name, percentage, or number from the Query Result Data (e.g. 'The car model with the highest conversion rate is the Kia Sonet at 16.26% (344 conversions)...'). Do NOT provide a generic overall dealership count unless explicitly asked.\n"
                "2. Provide 1-2 additional sentences with supporting comparisons or key context from the table.\n"
                "3. End with exactly ONE concrete, actionable business recommendation for dealership managers under RECOMMENDATION.\n"
                "4. Strictly use the real numbers from the Query Result Data table; never invent numbers.\n"
                "Format strictly with two headings:\n"
                "FINDINGS: <Direct answer + supporting context>\n"
                "RECOMMENDATION: <1 actionable recommendation>"
            )

            summary_messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=summary_prompt),
            ]
            summary_resp = self.llm.invoke(summary_messages).content

            # Parse findings and recommendation
            findings_match = re.search(r"FINDINGS:\s*(.*?)(?:RECOMMENDATION:|$)", summary_resp, re.DOTALL | re.IGNORECASE)
            rec_match = re.search(r"RECOMMENDATION:\s*(.*?)$", summary_resp, re.DOTALL | re.IGNORECASE)

            summary_text = findings_match.group(1).strip() if findings_match else summary_resp.strip()
            rec_text = rec_match.group(1).strip() if rec_match else "Focus follow-up resources on high-converting lead segments."
        else:
            summary_text = f"The query could not be completed successfully. Reason: {last_error}"
            rec_text = "Verify the input question and CRM column names, or specify simpler filtering criteria."

        latency_ms = (time.time() - start_time) * 1000

        # Log interaction for audit trail
        log_query_interaction(
            question=question,
            plan=current_plan,
            generated_code=current_code,
            outcome="SUCCESS" if (exec_result and exec_result.success) else "FAILED",
            success=(exec_result.success if exec_result else False),
            retries=attempts - 1,
            latency_ms=latency_ms,
            summary=summary_text,
            chart_type=chart_info.get("chart_type"),
            error=last_error if (not exec_result or not exec_result.success) else None,
        )

        # Update conversation memory
        preview_str = exec_result.df_result.head(5).to_string(index=False) if (exec_result and exec_result.df_result is not None) else ""
        self.memory.add_turn(
            question=question,
            plan=current_plan,
            code=current_code,
            result_preview=preview_str,
            business_summary=summary_text,
            recommendation=rec_text,
            chart_spec=chart_spec,
        )

        return AgentResponse(
            question=question,
            plan=current_plan,
            code=current_code,
            attempts=attempts,
            success=(exec_result.success if exec_result else False),
            df_result=(exec_result.df_result if exec_result else None),
            chart_spec=chart_spec,
            summary=summary_text,
            recommendation=rec_text,
            assumptions=assumptions,
            error=last_error if (not exec_result or not exec_result.success) else None,
            latency_ms=latency_ms,
        )
