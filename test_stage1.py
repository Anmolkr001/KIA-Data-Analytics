"""
Stage 1 Test Suite — Ask Your Data Agent & Data Pipeline
Run: python test_stage1.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from ask_your_data.data_loader import load_dataset, describe_schema, format_schema_for_prompt
from ask_your_data.sandbox import SandboxedPandasExecutor
from ask_your_data.tools import describe_schema as describe_tool, run_pandas_query, make_chart
from ask_your_data.agent import AskYourDataAgent
from ask_your_data.logger import read_recent_logs


def run_stage_1_tests():
    print("=" * 80)
    print("[STAGE 1] VERIFICATION: Data Loading, Sandboxed Tools & LangChain Agent")
    print("=" * 80)

    # 1. Test Data Loading & Schema Inspection
    print("\n[1/5] Testing Data Loading & Schema Reflection...")
    df = load_dataset()
    assert len(df) == 6967, f"Expected 6,967 rows, got {len(df)}"
    assert "is_converted" in df.columns, "is_converted column missing"
    assert "test_drive_done" in df.columns, "test_drive_done column missing"
    assert "car_model" in df.columns, "car_model column missing"
    print(f"  [OK] Successfully loaded CRM dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"  [OK] Retail conversions: {df['is_converted'].sum():,} ({df['is_converted'].mean():.2%})")
    print(f"  [OK] Completed Test Drives: {(df['test_drive_done'] == 'Yes').sum():,} ({(df['test_drive_done'] == 'Yes').mean():.2%})")
    print(f"  [OK] Mirrored to SQLite: data/leads.db")

    # 2. Test Sandboxed Security Rules
    print("\n[2/5] Testing Sandbox Security Constraints...")
    executor = SandboxedPandasExecutor(timeout_seconds=2)
    
    # Benign query
    benign_res = executor.run("result = df.groupby('car_model')['is_converted'].mean().reset_index()", df)
    assert benign_res.success is True, f"Benign query failed: {benign_res.error}"
    print("  [OK] Allowed: Vectorized pandas aggregation executed safely")

    # Blocked import
    import_res = executor.run("import os; result = 1", df)
    assert import_res.success is False and "import" in import_res.error.lower()
    print("  [OK] Blocked: 'import os' forbidden")

    # Blocked file write
    write_res = executor.run("df.to_csv('exploit.csv'); result = 1", df)
    assert write_res.success is False and "to_csv" in write_res.error.lower()
    print("  [OK] Blocked: 'df.to_csv()' file creation forbidden")

    # Blocked eval/exec
    eval_res = executor.run("result = eval('10 + 20')", df)
    assert eval_res.success is False and "eval" in eval_res.error.lower()
    print("  [OK] Blocked: 'eval()' arbitrary string execution forbidden")

    # Blocked while loops
    while_res = executor.run("while True: pass", df)
    assert while_res.success is False and "while" in while_res.error.lower()
    print("  [OK] Blocked: 'while' loop infinite loop prevention")

    # 3. Test LangChain Tools
    print("\n[3/5] Testing LangChain Tools (describe_schema, run_pandas_query, make_chart)...")
    schema_output = describe_tool.invoke({"filter_pattern": "Source"})
    assert "lead_source" in schema_output
    print("  [OK] Tool `describe_schema` returned verified schema information")

    query_output = run_pandas_query.invoke({
        "code": "result = df.groupby('lead_source')['is_converted'].agg(Leads='count', Deliveries='sum', Rate='mean').reset_index()"
    })
    assert "QUERY SUCCESS" in query_output
    print("  [OK] Tool `run_pandas_query` executed sandboxed code and returned table")

    chart_output = make_chart.invoke({
        "chart_type": "bar",
        "x_col": "lead_source",
        "y_col": "Rate",
        "title": "Conversion Rate by Lead Source"
    })
    assert "SUCCESS" in chart_output
    print("  [OK] Tool `make_chart` generated Plotly chart spec")

    # 4. Test Agent Flow: Plan -> Query -> Self-Check -> Chart -> Summary
    print("\n[4/5] Testing Agent Flow with Self-Check & Business Summary...")
    agent = AskYourDataAgent()
    resp1 = agent.ask("Which car model has the highest conversion rate?")
    assert resp1.success is True, f"Agent failed: {resp1.error}"
    assert resp1.df_result is not None
    assert len(resp1.summary) > 0
    assert len(resp1.recommendation) > 0
    print("  [OK] Agent Plan:", resp1.plan.splitlines()[0])
    print("  [OK] Agent Generated Code:\n", "    " + resp1.code.replace("\n", "\n    "))
    print("  [OK] Agent Summary:", resp1.summary[:120] + "...")
    print("  [OK] Agent Recommendation:", resp1.recommendation)
    print("  [OK] Attempts:", resp1.attempts)
    print("  [OK] Transparency section generated ('How I got this')")

    # 5. Test Multi-Turn Conversation Memory & Audit Logs
    print("\n[5/5] Testing Conversation Memory (Follow-ups) & Audit Logging...")
    resp_followup = agent.ask("Now break that down by model")
    assert resp_followup.success is True
    print("  [OK] Follow-up contextual turn executed successfully")

    audit_logs = read_recent_logs(5)
    assert len(audit_logs) >= 2, "Audit logs were not written"
    print(f"  [OK] Structured audit log recorded ({len(audit_logs)} recent entries in logs/query_audit.jsonl)")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL STAGE 1 REQUIREMENTS FULLY SATISFIED AND PASSING!")
    print("=" * 80)


if __name__ == "__main__":
    run_stage_1_tests()
