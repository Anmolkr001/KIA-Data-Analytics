"""
Ask Your Data — Natural-Language Analytics Assistant for Car Dealership CRM
Built with Streamlit, LangChain, and Plotly.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Setup python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ask_your_data.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_MODEL_NAME,
    ANTHROPIC_MODEL_NAME,
)
from ask_your_data.data_loader import load_dataset, describe_schema
from ask_your_data.agent import AskYourDataAgent, AgentResponse
from ask_your_data.memory import ConversationMemory
from ask_your_data.logger import read_recent_logs

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Design System
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ask Your Data | Kia Dealership CRM Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for modern executive automotive aesthetic
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Top banner */
    .hero-banner {
        background: linear-gradient(135deg, #0B2545 0%, #133C55 50%, #134074 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #BEE9E8;
        margin-top: 6px;
        font-weight: 400;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .kpi-label {
        font-size: 12px;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .kpi-subtext {
        font-size: 12px;
        color: #10B981;
        margin-top: 2px;
        font-weight: 500;
    }

    /* Business summary card */
    .summary-card {
        background: #F8FAFC;
        border-left: 4px solid #0B5394;
        border-radius: 0 8px 8px 0;
        padding: 16px 20px;
        margin-top: 14px;
        margin-bottom: 14px;
    }
    .summary-title {
        font-weight: 600;
        color: #0B5394;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .recommendation-card {
        background: #ECFDF5;
        border-left: 4px solid #10B981;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 14px;
    }
    .recommendation-title {
        font-weight: 600;
        color: #065F46;
        font-size: 13px;
        margin-bottom: 2px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-success { background: #DCFCE7; color: #166534; }
    .badge-info { background: #E0F2FE; color: #075985; }
    .badge-warning { background: #FEF3C7; color: #92400E; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Cached Data & Agent State
# -----------------------------------------------------------------------------
@st.cache_resource
def get_cached_dataset() -> pd.DataFrame:
    return load_dataset()


def get_agent_instance(provider: Optional[str] = None) -> AskYourDataAgent:
    if "agent" not in st.session_state or st.session_state.get("agent_provider") != provider:
        memory = st.session_state.get("conversation_memory", ConversationMemory())
        st.session_state.agent = AskYourDataAgent(provider=provider, memory=memory)
        st.session_state.agent_provider = provider
    return st.session_state.agent


# Load data
df = get_cached_dataset()

# Initialize session messages
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory()
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# -----------------------------------------------------------------------------
# Sidebar: Configuration, Statistics & Starter Questions
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/4/47/Kia_logo.svg",
        width=110,
    )
    st.title("Ask Your Data")
    st.caption("Dealership Natural Language CRM Assistant")

    st.markdown("---")
    st.subheader("⚙️ LLM Provider")

    provider_options = ["openai", "anthropic", "offline_mock"]
    default_idx = 0 if LLM_PROVIDER == "openai" else (1 if LLM_PROVIDER == "anthropic" else 2)

    selected_provider = st.selectbox(
        "Provider",
        options=provider_options,
        index=default_idx,
        help="Select configured LangChain provider or offline heuristic engine",
    )

    # API Key status
    has_openai = bool(OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"))
    has_anthropic = bool(ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("your_"))

    if selected_provider == "openai":
        status_color = "🟢" if has_openai else "🟡"
        st.caption(f"{status_color} OpenAI Key: {'Configured' if has_openai else 'Missing (using Mock)'}")
        st.caption(f"Model: `{OPENAI_MODEL_NAME}`")
    elif selected_provider == "anthropic":
        status_color = "🟢" if has_anthropic else "🟡"
        st.caption(f"{status_color} Anthropic Key: {'Configured' if has_anthropic else 'Missing (using Mock)'}")
        st.caption(f"Model: `{ANTHROPIC_MODEL_NAME}`")
    else:
        st.caption("🔵 Running Deterministic Offline Engine (No API key required)")

    st.markdown("---")
    st.subheader("💡 Manager Starter Questions")
    st.caption("Click any question to ask the agent:")

    starter_questions = [
        "What is our overall lead-to-sale conversion rate?",
        "How does completing a test drive impact conversion?",
        "Which lead sources have the highest conversion rate?",
        "Compare conversion rates across car models.",
        "Show top 5 sales consultants by retail deliveries.",
        "How does number of follow-ups impact conversion?",
        "What percentage of leads are from Bhubaneswar?",
    ]

    for q in starter_questions:
        if st.button(f"👉 {q}", key=f"starter_{hash(q)}", use_container_width=True):
            st.session_state.pending_question = q

    st.markdown("---")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_memory.clear()
            st.rerun()
    with col_sb2:
        st.caption(f"Leads: **{len(df):,}**")

# -----------------------------------------------------------------------------
# Main Hero Banner & KPI Summary Cards
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1 class="hero-title">🚗 Kia Dealership Lead Intelligence</h1>
        <div class="hero-subtitle">
            Natural-language sales analytics, conversion bottleneck diagnosis, and predictive lead scoring.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dealership Funnel Metric Cards
total_leads = len(df)
td_completed = int((df["test_drive_done"] == "Yes").sum())
td_rate = (td_completed / total_leads * 100) if total_leads else 0.0

bookings = int(df["is_booked"].sum())
booking_rate = (bookings / total_leads * 100) if total_leads else 0.0

retails = int(df["is_converted"].sum())
retail_rate = (retails / total_leads * 100) if total_leads else 0.0

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.metric(label="Total Enquiries", value=f"{total_leads:,}", delta="CRM Active")
with kpi_cols[1]:
    st.metric(label="Completed Test Drives", value=f"{td_rate:.1f}%", delta=f"{td_completed:,} leads")
with kpi_cols[2]:
    st.metric(label="Total Bookings", value=f"{booking_rate:.1f}%", delta=f"{bookings:,} bookings")
with kpi_cols[3]:
    st.metric(label="Retail Deliveries", value=f"{retail_rate:.1f}%", delta=f"{retails:,} sales")

# -----------------------------------------------------------------------------
# Navigation Tabs
# -----------------------------------------------------------------------------
tab_chat, tab_scoring, tab_explorer = st.tabs([
    "💬 Ask Your Data (Agent)",
    "🎯 Score a Lead (Predictor)",
    "📊 CRM Schema & Data Explorer",
])

# =============================================================================
# TAB 1: Conversational Query Agent
# =============================================================================
with tab_chat:
    st.markdown("#### Ask Any Question About Dealership Enquiries, Models, or Consultants")

    # Render previous messages from history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                resp: AgentResponse = msg["response"]
                
                # Findings Callout
                if resp.summary:
                    st.markdown(
                        f"""
                        <div class="summary-card">
                            <div class="summary-title">📈 Key Analytical Findings</div>
                            <div>{resp.summary}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Recommendation Callout
                if resp.recommendation:
                    st.markdown(
                        f"""
                        <div class="recommendation-card">
                            <div class="recommendation-title">🎯 Actionable Recommendation for Sales Managers</div>
                            <div>{resp.recommendation}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Plotly Chart
                if resp.chart_spec:
                    try:
                        fig = go.Figure(resp.chart_spec)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Chart render notice: {e}")

                # Tabular Data Preview
                if resp.df_result is not None and not resp.df_result.empty:
                    with st.expander("📋 View Data Table", expanded=False):
                        st.dataframe(resp.df_result, use_container_width=True)
                        csv_data = resp.df_result.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv_data,
                            file_name=f"query_result_{int(resp.latency_ms)}.csv",
                            mime="text/csv",
                        )

                # Expandable Transparency: "How I got this"
                with st.expander("🔍 How I got this (Planning & Generated Code)", expanded=False):
                    st.markdown(resp.how_i_got_this())
                    st.caption(f"⚡ Latency: {resp.latency_ms:.1f}ms | Attempts: {resp.attempts}")

    # Handle pending starter question or new input
    prompt_input = st.chat_input("Ask a question (e.g. 'What is our conversion rate by car model?')")
    active_prompt = st.session_state.pending_question or prompt_input

    if active_prompt:
        st.session_state.pending_question = None

        # Display user message
        with st.chat_message("user"):
            st.write(active_prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": active_prompt,
        })

        # Run Agent
        with st.chat_message("assistant"):
            agent = get_agent_instance(provider=selected_provider)
            with st.spinner("Analyzing CRM schema and computing query..."):
                response = agent.ask(active_prompt)

            # 1. Findings
            if response.summary:
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <div class="summary-title">📈 Key Analytical Findings</div>
                        <div>{response.summary}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # 2. Recommendation
            if response.recommendation:
                st.markdown(
                    f"""
                    <div class="recommendation-card">
                        <div class="recommendation-title">🎯 Actionable Recommendation for Sales Managers</div>
                        <div>{response.recommendation}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # 3. Chart
            if response.chart_spec:
                try:
                    fig = go.Figure(response.chart_spec)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart render notice: {e}")

            # 4. Tabular Data Preview
            if response.df_result is not None and not response.df_result.empty:
                with st.expander("📋 View Data Table", expanded=False):
                    st.dataframe(response.df_result, use_container_width=True)
                    csv_data = response.df_result.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"query_result_{int(response.latency_ms)}.csv",
                        mime="text/csv",
                    )

            # 5. Expandable "How I got this"
            with st.expander("🔍 How I got this (Planning & Generated Code)", expanded=False):
                st.markdown(response.how_i_got_this())
                st.caption(f"⚡ Latency: {response.latency_ms:.1f}ms | Attempts: {response.attempts}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": response.summary,
                "response": response,
            })

# =============================================================================
# TAB 2: Lead Scoring Predictor
# =============================================================================
with tab_scoring:
    st.markdown("#### 🎯 Predict Lead Conversion Probability")
    st.caption("Input prospect details to calculate conversion likelihood and recommended next steps.")

    with st.form("lead_scoring_form"):
        col_form1, col_form2 = st.columns(2)

        with col_form1:
            input_model = st.selectbox(
                "Kia Car Model",
                options=["SONET", "NEW SELTOS", "CARENS", "CARENS CLAVIS EV", "SELTOS", "SYROS", "CARNIVAL", "EV6"],
            )
            input_source = st.selectbox(
                "Enquiry Sourcing Channel",
                options=["Walkin", "Referral", "Hyperlocal", "Field", "Online/CRM", "Telephone"],
            )
            input_warmth = st.selectbox(
                "Lead Warmth Stage",
                options=["Hot", "Warm", "Cold"],
            )
            input_cust_type = st.selectbox(
                "Customer Type",
                options=["Individual", "Corporate"],
            )

        with col_form2:
            input_td = st.radio(
                "Test Drive Completed?",
                options=["Yes", "No"],
                horizontal=True,
            )
            input_followups = st.slider(
                "Follow-up Touchpoints Done",
                min_value=0,
                max_value=12,
                value=2,
            )
            input_city = st.selectbox(
                "Customer City / Location",
                options=["BHUBANESWAR", "CUTTACK", "BERHAMPUR", "ANGUL", "PURI", "BALASORE", "SAMBALPUR", "OTHER"],
            )
            input_exchange = st.radio(
                "Interested in Vehicle Exchange?",
                options=["No", "Yes"],
                horizontal=True,
            )

        submit_score = st.form_submit_button("🚀 Score Prospect via ML Engine", use_container_width=True)

    if submit_score:
        lead_input = {
            "car_model": input_model,
            "lead_source": input_source,
            "lead_warmth": input_warmth,
            "customer_type": input_cust_type,
            "test_drive_done": input_td,
            "city": input_city,
            "exchange_interest": input_exchange,
            "fuel_type": "Gasoline",
            "followup_count": input_followups,
            "aging_days": 10,
            "quotation_count": 0.0,
        }

        # Try FastAPI endpoint first, fall back to direct predictor
        prediction_result = None
        try:
            import urllib.request
            req = urllib.request.Request(
                "http://127.0.0.1:8000/predict",
                data=json.dumps(lead_input).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp_api:
                prediction_result = json.loads(resp_api.read().decode("utf-8"))
        except Exception:
            # Direct in-process ML fallback
            from ask_your_data.lead_scoring.predictor import predict_lead_conversion
            prediction_result = predict_lead_conversion(lead_input)

        prob_pct = prediction_result["conversion_percentage"]
        tier = prediction_result["priority_tier"]
        badge = prediction_result["badge"]
        rec = prediction_result["recommendation"]
        shap_factors = prediction_result["top_shap_factors"]

        st.markdown("---")
        score_cols = st.columns([1, 2])

        with score_cols[0]:
            st.metric(
                label="Predicted Conversion Likelihood",
                value=f"{prob_pct:.1f}%",
                delta=tier,
            )
            st.progress(min(prob_pct / 100.0, 1.0))

        with score_cols[1]:
            if tier == "HIGH":
                st.success(f"{badge}\n\n**Action Plan:** {rec}")
            elif tier == "MEDIUM":
                st.info(f"{badge}\n\n**Action Plan:** {rec}")
            else:
                st.warning(f"{badge}\n\n**Action Plan:** {rec}")

        st.markdown("##### 🔬 Top SHAP Drivers for this Prospect:")
        factor_cols = st.columns(len(shap_factors[:4]))
        for i, f in enumerate(shap_factors[:4]):
            with factor_cols[i]:
                impact_val = f["shap_value"]
                color_arrow = "🟢 +" if impact_val > 0 else "🔴 "
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px;">
                        <div style="font-size:11px; color:#64748B; font-weight:600;">{f['feature']}</div>
                        <div style="font-size:14px; font-weight:700; margin-top:2px;">{color_arrow}{abs(impact_val):.2f}</div>
                        <div style="font-size:10px; color:#475569; margin-top:2px;">{f['impact_direction']} impact</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# =============================================================================
# TAB 3: Schema & Data Explorer
# =============================================================================
with tab_explorer:
    st.markdown("#### 📋 Real CRM Schema & Data Overview")
    schema_info = describe_schema()

    col_sc1, col_sc2 = st.columns([1, 2])
    with col_sc1:
        st.metric("Total Records", f"{schema_info['total_rows']:,}")
        st.metric("Total Columns", schema_info["total_columns"])
        st.metric("SQLite Mirror", "Active (data/leads.db)")

    with col_sc2:
        filter_col = st.text_input("Filter Columns by Name", placeholder="e.g. Model, Date, Test Drive...")

    # Display schema table
    columns_data = schema_info["columns"]
    if filter_col:
        columns_data = [c for c in columns_data if filter_col.lower() in c["column"].lower()]

    schema_table_df = pd.DataFrame([
        {
            "Column Name": c["column"],
            "Data Type": c["dtype"],
            "Non-Null Count": c["non_null"],
            "Unique Values": c["unique_count"],
            "Sample Values": ", ".join(c["samples"][:3]),
        }
        for c in columns_data
    ])
    st.dataframe(schema_table_df, use_container_width=True, height=350)

    # Raw sample data preview
    with st.expander("👀 Inspect Sample Dataset Rows (Top 25)", expanded=False):
        st.dataframe(df.head(25), use_container_width=True)

    # Recent query audit logs
    with st.expander("📜 Recent Query Audit Logs (Transparency & Security)", expanded=False):
        recent_logs = read_recent_logs(20)
        if recent_logs:
            st.dataframe(pd.DataFrame(recent_logs), use_container_width=True)
        else:
            st.caption("No audit logs recorded yet.")
