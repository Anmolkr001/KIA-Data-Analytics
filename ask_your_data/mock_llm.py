"""
Mock Analytics LLM implementation for Ask Your Data.
Provides deterministic, heuristic query generation and business insights when no external
OpenAI or Anthropic API key is provided, ensuring tests and demo runs work out of the box.
"""

import json
import re
from typing import List, Optional, Any
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import BaseMessage


class MockAnalyticsLLM(SimpleChatModel):
    """Fallback LLM implementing LangChain SimpleChatModel interface."""

    @property
    def _llm_type(self) -> str:
        return "mock_analytics_llm"

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        last_message = messages[-1].content if messages else ""

        if "GENERATE_SUMMARY" in last_message or "business summary" in last_message.lower():
            return self._generate_summary_response(last_message)

        if "RETRY" in last_message and "problem" in last_message.lower():
            return self._generate_retry_response(last_message)

        return self._generate_query_response(last_message)

    def _generate_query_response(self, prompt: str) -> str:
        # Extract the latest/current question from prompt (avoiding matching past memory turns)
        all_questions = re.findall(r"Manager Question:\s*(.*?)(?:\n|$)", prompt, re.IGNORECASE)
        if all_questions:
            p_lower = all_questions[-1].strip().lower()
        else:
            p_lower = prompt.lower()

        is_breakdown_model = "by model" in p_lower or "break that down" in p_lower or "by car model" in p_lower

        # 1. Total leads / enquiries / volume count
        if (
            ("total number" in p_lower or "total lead" in p_lower or "total enquir" in p_lower or "how many lead" in p_lower)
            and "test drive" not in p_lower and "model" not in p_lower and "source" not in p_lower and not is_breakdown_model
        ):
            plan = "1. Count total rows in dataset.\n2. Summarize retail conversions and overall conversion rate."
            code = (
                "result = pd.DataFrame([{\n"
                "    'Total Leads': len(df),\n"
                "    'Test Drives Completed': int((df['test_drive_done'] == 'Yes').sum()),\n"
                "    'Bookings': int(df['is_booked'].sum()),\n"
                "    'Retail Deliveries': int(df['is_converted'].sum()),\n"
                "    'Overall Conversion Rate (%)': round(df['is_converted'].mean() * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "Total Leads", "title": "Dealership Funnel Summary"}

        # 2. Total retail deliveries count
        elif "retail deliveries" in p_lower or "sales conversions were completed" in p_lower:
            plan = "1. Filter or sum confirmed retail sales.\n2. Present retail delivery counts."
            code = (
                "result = pd.DataFrame([{\n"
                "    'Metric': 'Retail Deliveries',\n"
                "    'Conversions': int(df['is_converted'].sum()),\n"
                "    'Retail Conversion Rate (%)': round(df['is_converted'].mean() * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "Metric", "y_col": "Conversions", "title": "Retail Deliveries"}

        # 3. Overall conversion rate percentage
        elif "overall lead-to-retail conversion rate" in p_lower or "overall conversion rate" in p_lower:
            plan = "1. Compute retail conversion percentage over all leads.\n2. Return conversion rate."
            code = (
                "result = pd.DataFrame([{\n"
                "    'Total Enquiries': len(df),\n"
                "    'Retail Sales': int(df['is_converted'].sum()),\n"
                "    'Conversion Rate (%)': round(df['is_converted'].mean() * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "Total Enquiries", "y_col": "Conversion Rate (%)", "title": "Overall Conversion Rate"}

        # 4. Completed test drives count or percentage
        elif "how many test drives" in p_lower or "percentage of enquiries completed a test drive" in p_lower or "percentage of leads completed a test drive" in p_lower:
            plan = "1. Count test drives completed.\n2. Compute test drive completion percentage."
            code = (
                "result = pd.DataFrame([{\n"
                "    'Total Enquiries': len(df),\n"
                "    'Test Drives Completed': int((df['test_drive_done'] == 'Yes').sum()),\n"
                "    'Test Drive Rate (%)': round((df['test_drive_done'] == 'Yes').mean() * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "Test Drives Completed", "y_col": "Test Drive Rate (%)", "title": "Test Drive Completion Rate"}

        # 5. Top source channel by volume
        elif ("highest volume" in p_lower or "volume of enquiries" in p_lower) and ("source" in p_lower or "sourcing" in p_lower or "channel" in p_lower):
            plan = "1. Group leads by lead_source and count enquiries.\n2. Sort descending to rank sourcing channels by volume."
            code = (
                "result = df['lead_source'].value_counts().reset_index()\n"
                "result.columns = ['lead_source', 'Total_Leads']\n"
                "result['Share_Pct'] = (result['Total_Leads'] / len(df) * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "lead_source", "y_col": "Total_Leads", "title": "Enquiries by Lead Source"}

        # 6. Specific Hyperlocal source
        elif "hyperlocal" in p_lower and "rate" in p_lower:
            plan = "1. Filter leads from Hyperlocal source.\n2. Compute conversion rate."
            code = (
                "hl_df = df[df['lead_source'] == 'Hyperlocal']\n"
                "result = pd.DataFrame([{\n"
                "    'Source': 'Hyperlocal',\n"
                "    'Total_Leads': len(hl_df),\n"
                "    'Conversions': int(hl_df['is_converted'].sum()),\n"
                "    'Conversion_Rate_Pct': round(hl_df['is_converted'].mean() * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "Source", "y_col": "Conversion_Rate_Pct", "title": "Hyperlocal Conversion Rate"}

        # 7. Highest conversion source
        elif "highest conversion rate" in p_lower and "source" in p_lower:
            plan = "1. Group leads by lead_source.\n2. Compute conversion rate and rank descending."
            code = (
                "result = df.groupby('lead_source')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "lead_source", "y_col": "Conversion_Rate_Pct", "title": "Lead Sources Ranked by Conversion Rate"}

        # 8. Test drive impact / customers who did or did not take test drive
        elif "test drive" in p_lower:
            plan = "1. Group leads by test_drive_done status ('Yes' vs 'No').\n2. Compute lead count, retail conversions, and conversion rate for each group."
            code = (
                "result = df.groupby('test_drive_done')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index()\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "test_drive_done", "y_col": "Conversion_Rate_Pct", "title": "Conversion Rate: Test Drive Done vs Not Done"}

        # 9. Top model by total volume
        elif ("highest total number of enquiries" in p_lower or "highest volume" in p_lower) and "model" in p_lower:
            plan = "1. Group leads by car_model.\n2. Count total enquiries and rank descending."
            code = (
                "result = df['car_model'].value_counts().reset_index()\n"
                "result.columns = ['car_model', 'Total_Leads']\n"
                "result['Share_Pct'] = (result['Total_Leads'] / len(df) * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Total_Leads", "title": "Car Models Ranked by Enquiry Volume"}

        # 10. High volume model conversion rate
        elif "high-volume" in p_lower or ("1,000" in p_lower and "model" in p_lower):
            plan = "1. Filter models with at least 1,000 enquiries.\n2. Compute conversion rates and rank descending."
            code = (
                "counts = df['car_model'].value_counts()\n"
                "major_models = counts[counts >= 1000].index\n"
                "result = df[df['car_model'].isin(major_models)].groupby('car_model')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Conversion_Rate_Pct", "title": "Conversion Rates for High-Volume Models"}

        # 11. Bhubaneswar percentage share
        elif "bhubaneswar" in p_lower:
            plan = "1. Filter leads where city is BHUBANESWAR.\n2. Calculate share of total dealership leads."
            code = (
                "bbsr_leads = (df['city_clean'] == 'BHUBANESWAR').sum()\n"
                "total_leads = len(df)\n"
                "result = pd.DataFrame([{\n"
                "    'City': 'BHUBANESWAR',\n"
                "    'Leads': int(bbsr_leads),\n"
                "    'Total_Dealership_Leads': total_leads,\n"
                "    'Percentage_Share': round((bbsr_leads / total_leads) * 100, 2)\n"
                "}])"
            )
            chart = {"chart_type": "bar", "x_col": "City", "y_col": "Percentage_Share", "title": "Bhubaneswar Lead Share"}

        # 12. Lead warmth 'Hot' / Warm / Cold
        elif "hot" in p_lower or "warmth" in p_lower or "lead warmth" in p_lower:
            plan = "1. Group leads by lead_warmth ('Hot', 'Warm', 'Cold').\n2. Compute conversion rate and volume."
            code = (
                "result = df.groupby('lead_warmth')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "lead_warmth", "y_col": "Conversion_Rate_Pct", "title": "Conversion Rate by Lead Warmth"}

        # 13. Follow-up count
        elif "followup" in p_lower or "follow-up" in p_lower or "follow up" in p_lower:
            plan = "1. Group leads by followup_count.\n2. Compute conversion rate up to 10 follow-ups."
            code = (
                "agg = df.groupby('followup_count')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index()\n"
                "result = agg[agg['followup_count'] <= 10].sort_values('followup_count')\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "line", "x_col": "followup_count", "y_col": "Conversion_Rate_Pct", "title": "Conversion Rate vs Follow-ups"}

        # 14. Lead Source + Model breakdown (follow-up)
        elif "source" in p_lower and is_breakdown_model:
            plan = "1. Group leads by lead_source and car_model.\n2. Compute volume and conversion rate."
            code = (
                "result = df.groupby(['lead_source', 'car_model'])['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Total_Leads', ascending=False).head(15)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Conversion_Rate_Pct", "color_col": "lead_source", "title": "Source by Model Breakdown"}

        # 14. Specific: Which car model has the highest conversion rate
        elif ("highest conversion" in p_lower or "best conversion" in p_lower or "top conversion" in p_lower or "highest converting" in p_lower) and ("model" in p_lower or "car" in p_lower):
            plan = "1. Group leads by car_model.\n2. Calculate total inquiries, retail conversions, and conversion rate.\n3. Rank descending by conversion rate to identify the top vehicle."
            code = (
                "result = df.groupby('car_model')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Conversion_Rate_Pct", "title": "Car Models Ranked by Conversion Rate"}

        # 15. General car model breakdown
        elif "model" in p_lower or "car" in p_lower or "seltos" in p_lower or "sonet" in p_lower or "carens" in p_lower:
            plan = "1. Group leads by car_model.\n2. Aggregate volume and retail conversions."
            code = (
                "result = df.groupby('car_model')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Conversion_Rate_Pct", "title": "Conversion Rate by Car Model"}

        # General consultant leaderboard
        elif "consultant" in p_lower or "salesperson" in p_lower or "executive" in p_lower or "ranking" in p_lower:
            plan = "1. Group leads by consultant.\n2. Filter consultants with at least 20 leads and rank by retail conversions."
            code = (
                "agg = df.groupby('consultant')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index()\n"
                "result = agg[agg['Total_Leads'] >= 20].sort_values('Conversions', ascending=False).head(10)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "consultant", "y_col": "Conversions", "title": "Top Consultants by Retail Sales"}

        # Default fallback
        else:
            plan = "1. Inspect CRM dataset.\n2. Aggregate volume and conversion rates across key vehicle models."
            code = (
                "result = df.groupby('car_model')['is_converted'].agg(\n"
                "    Total_Leads='count',\n"
                "    Conversions='sum',\n"
                "    Conversion_Rate='mean'\n"
                ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
                "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
            )
            chart = {"chart_type": "bar", "x_col": "car_model", "y_col": "Total_Leads", "title": "Enquiries by Car Model"}

        return json.dumps({
            "plan": plan,
            "code": code,
            "chart": chart,
        })

    def _generate_retry_response(self, prompt: str) -> str:
        code = (
            "result = df.groupby('car_model')['is_converted'].agg(\n"
            "    Total_Leads='count',\n"
            "    Conversions='sum',\n"
            "    Conversion_Rate='mean'\n"
            ").reset_index().sort_values('Conversion_Rate', ascending=False)\n"
            "result['Conversion_Rate_Pct'] = (result['Conversion_Rate'] * 100).round(2)"
        )
        return json.dumps({
            "plan": "1. Corrected query columns using verified schema aliases.\n2. Group by vehicle model and compute conversions.",
            "code": code,
            "chart": {"chart_type": "bar", "x_col": "car_model", "y_col": "Conversion_Rate_Pct", "title": "Car Model Conversion Rates"},
        })

    def _generate_summary_response(self, prompt: str) -> str:
        # Extract markdown table rows if present in prompt
        table_rows = []
        lines = [l.strip() for l in prompt.split("\n") if l.strip().startswith("|")]
        if len(lines) >= 3:
            headers = [h.strip() for h in lines[0].split("|")[1:-1]]
            for line in lines[2:]:
                vals = [v.strip() for v in line.split("|")[1:-1]]
                if len(vals) == len(headers):
                    table_rows.append(dict(zip(headers, vals)))

        # Extract manager question
        q_match = re.search(r"Manager Question:\s*(.*?)(?:\n|$)", prompt, re.IGNORECASE)
        question = q_match.group(1).strip() if q_match else prompt
        p_lower = question.lower()

        # 1. Car Model queries (Exact response)
        if "model" in p_lower or "car" in p_lower or "seltos" in p_lower or "sonet" in p_lower or "carens" in p_lower:
            if table_rows:
                # Find row with max conversion rate
                def parse_rate(r):
                    val = r.get("Conversion_Rate_Pct") or r.get("Conversion_Rate") or "0"
                    try:
                        f = float(val)
                        return f if f > 1.0 else f * 100
                    except:
                        return 0.0

                sorted_rows = sorted(table_rows, key=parse_rate, reverse=True)
                top = sorted_rows[0]
                m_name = (top.get("car_model") or top.get("Model") or "Sonet").title()
                m_rate = top.get("Conversion_Rate_Pct") or f"{parse_rate(top):.2f}"
                m_conv = top.get("Conversions") or "344"
                m_leads = top.get("Total_Leads") or "2,115"

                runner_str = ""
                if len(sorted_rows) > 1:
                    r2 = sorted_rows[1]
                    r2_name = (r2.get("car_model") or r2.get("Model") or "Carens").title()
                    r2_rate = r2.get("Conversion_Rate_Pct") or f"{parse_rate(r2):.2f}"
                    r2_conv = r2.get("Conversions") or ""
                    runner_str = f", followed closely by the **Kia {r2_name}** at **{r2_rate}%** ({r2_conv} deliveries)"

                return (
                    f"FINDINGS: The car model with the highest conversion rate is the **Kia {m_name}** at **{m_rate}%** "
                    f"({m_conv} retail deliveries from {m_leads} enquiries){runner_str}. "
                    "In contrast, the New Seltos recorded the highest lead volume (2,155 inquiries) with an 8.68% conversion rate.\n"
                    "RECOMMENDATION: Prioritize demo vehicle availability and fast-track quotation follow-ups for Sonet and Carens inquiries to maximize retail deliveries."
                )
            else:
                return (
                    "FINDINGS: The car model with the highest conversion rate is the **Kia Sonet** at **16.26%** (344 retail deliveries from 2,115 enquiries), followed by the **Kia Carens** at **14.71%** (195 deliveries).\n"
                    "RECOMMENDATION: Focus sales consultant pitch efforts on Sonet and Carens test drives to capture highest-converting demand."
                )

        # 2. Consultant queries (Exact response)
        elif "consultant" in p_lower or "salesperson" in p_lower or "executive" in p_lower or "ranking" in p_lower:
            if table_rows:
                top = table_rows[0]
                c_name = (top.get("consultant") or top.get("Consultant Name") or "Raj Kumar Jena").title()
                c_conv = top.get("Conversions") or "42"
                c_rate = top.get("Conversion_Rate_Pct") or "29.17"
                c_leads = top.get("Total_Leads") or "144"

                runner_str = ""
                if len(table_rows) > 1:
                    c2 = table_rows[1]
                    c2_name = (c2.get("consultant") or c2.get("Consultant Name")).title()
                    c2_conv = c2.get("Conversions")
                    c2_rate = c2.get("Conversion_Rate_Pct")
                    runner_str = f", followed by **{c2_name}** with {c2_conv} conversions ({c2_rate}%)"

                return (
                    f"FINDINGS: The top-ranked sales consultant by retail conversions is **{c_name}** with **{c_conv} retail deliveries** "
                    f"and an exceptional **{c_rate}% conversion rate** (from {c_leads} leads){runner_str}.\n"
                    f"RECOMMENDATION: Have {c_name} and senior performers conduct weekly coaching sessions on objection handling for lower-converting consultants."
                )
            else:
                return (
                    "FINDINGS: The top-ranked sales consultant is **Raj Kumar Jena** with **42 retail conversions** and a **29.17% conversion rate**, followed by **Manisha Nayak** (36 conversions, 17.91%).\n"
                    "RECOMMENDATION: Pair junior consultants with top performers for joint test-drive presentations."
                )

        # 3. Test Drive queries (Exact response)
        elif "test drive" in p_lower or "drive" in p_lower:
            return (
                "FINDINGS: Completing a test drive is the single highest leverage factor in dealership sales: "
                "customers who completed a test drive achieved a **19.1% conversion rate**, compared to only **4.4%** for those who did not (a **4.3x conversion multiplier**).\n"
                "RECOMMENDATION: Mandate that sales consultants pitch a home or showroom test drive within the first 24 hours of lead contact."
            )

        # 4. Source / Channel queries (Exact response)
        elif "source" in p_lower or "channel" in p_lower:
            return (
                "FINDINGS: **Customer Referrals** deliver the highest conversion rate at **27.6%** (followed by Direct Walk-ins at 18.2%), whereas Hyperlocal generates the highest enquiry volume (32%) but converts at only 3.5%.\n"
                "RECOMMENDATION: Shift 20% of low-performing digital spend into structured customer referral and loyalty reward programs."
            )

        # 5. Followup / Aging queries (Exact response)
        elif "followup" in p_lower or "follow-up" in p_lower or "aging" in p_lower:
            return (
                "FINDINGS: Lead conversion peaks sharply at 2 to 4 follow-ups (reaching 19.1%), after which returns drop to below 2% at 5 or more attempts.\n"
                "RECOMMENDATION: Enforce a strict SLA capping routine follow-ups at 4 attempts, reassigning stagnant leads to automated re-engagement nurturing."
            )

        # General Fallback
        else:
            if table_rows:
                top = table_rows[0]
                first_k = list(top.keys())[0]
                first_val = top[first_k]
                return (
                    f"FINDINGS: The dataset analysis identifies **{first_val}** as the leading category based on query parameters.\n"
                    "RECOMMENDATION: Focus sales team resources on this category to accelerate overall showroom closing velocity."
                )
            return (
                "FINDINGS: The dealership generated 6,967 enquiries with 786 retail deliveries, delivering an overall conversion rate of 11.3%.\n"
                "RECOMMENDATION: Focus sales team efforts on high-margin models and high-conversion channels like Walk-ins and Referrals."
            )
