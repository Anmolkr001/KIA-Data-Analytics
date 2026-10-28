"""
KIA Enquiry Analytics — FastAPI Backend
Serves aggregated and paginated enquiry data from master_clean.csv
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ask_your_data.agent import AskYourDataAgent
from ask_your_data.config import LLM_PROVIDER, OPENAI_MODEL_NAME, ANTHROPIC_MODEL_NAME

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="KIA Enquiry Analytics API",
    description="REST API for customer sales enquiry analytics dashboard with LangChain AI Chat",
    version="1.0.0",
)

# CORS — allow Vite dev servers on any localhost port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "master_clean.csv")

_df_cache: Optional[pd.DataFrame] = None


def _load_data() -> pd.DataFrame:
    """Load and cache the master dataset. Parses dates on first load."""
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    if not os.path.exists(DATA_PATH):
        raise HTTPException(
            status_code=503,
            detail=f"Data file not found at {DATA_PATH}. Run the data pipeline first.",
        )

    try:
        df = pd.read_csv(DATA_PATH, low_memory=False)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read data file: {exc}",
        )

    # Parse the Enquiry Date column to datetime
    df["Enquiry Date"] = pd.to_datetime(df["Enquiry Date"], errors="coerce")

    # Ensure Customer Type has a clean default
    df["Customer Type"] = (
        df["Customer Type"]
        .fillna("Individual")
        .astype(str)
        .str.strip()
        .str.title()
    )

    # Drop rows with no enquiry date (unusable for time-series)
    df = df.dropna(subset=["Enquiry Date"]).reset_index(drop=True)

    _df_cache = df
    return _df_cache


@app.on_event("startup")
async def startup_load():
    """Pre-load data into memory on server startup."""
    _load_data()


# ---------------------------------------------------------------------------
# Endpoint: Health Check
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health():
    df = _load_data()
    return {
        "status": "healthy",
        "records_loaded": len(df),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Endpoint: Enquiry Trend Over Time
# ---------------------------------------------------------------------------


@app.get("/api/enquiries/trend")
async def enquiry_trend(
    group_by: str = Query("day", pattern="^(day|week)$"),
):
    """
    Returns enquiry counts grouped by day or ISO week.

    Query params:
        group_by  — 'day' (default) or 'week'
    """
    df = _load_data()

    if group_by == "week":
        # Group by ISO year-week
        df_copy = df.copy()
        df_copy["period"] = df_copy["Enquiry Date"].dt.strftime("%G-W%V")
        grouped = (
            df_copy.groupby("period")
            .size()
            .reset_index(name="count")
            .sort_values("period")
        )
    else:
        # Group by calendar date
        df_copy = df.copy()
        df_copy["period"] = df_copy["Enquiry Date"].dt.strftime("%Y-%m-%d")
        grouped = (
            df_copy.groupby("period")
            .size()
            .reset_index(name="count")
            .sort_values("period")
        )

    return {
        "group_by": group_by,
        "total_records": int(grouped["count"].sum()),
        "data": grouped.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# Endpoint: Customer Type Breakdown
# ---------------------------------------------------------------------------


@app.get("/api/enquiries/customer-type")
async def customer_type_breakdown():
    """
    Returns the count and percentage of enquiries by Customer Type
    (Individual vs. Corporate).
    """
    df = _load_data()
    total = len(df)

    counts = df["Customer Type"].value_counts().to_dict()

    breakdown = []
    for ctype, count in counts.items():
        breakdown.append(
            {
                "type": ctype,
                "count": int(count),
                "percentage": round((count / total) * 100, 2) if total > 0 else 0,
            }
        )

    # Sort by count descending
    breakdown.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total": total,
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# Endpoint: KPI Summary
# ---------------------------------------------------------------------------


@app.get("/api/enquiries/kpis")
async def kpi_summary():
    """
    Returns high-level KPI metrics for the dashboard cards:
    - Total enquiries
    - Peak enquiry day (day with most enquiries)
    - Dominant customer type
    - Date range
    """
    df = _load_data()
    total = len(df)

    # Peak enquiry day
    daily_counts = df["Enquiry Date"].dt.date.value_counts()
    if not daily_counts.empty:
        peak_day = daily_counts.idxmax()
        peak_day_count = int(daily_counts.max())
        peak_day_str = peak_day.strftime("%Y-%m-%d")
    else:
        peak_day_str = "N/A"
        peak_day_count = 0

    # Dominant customer type
    type_counts = df["Customer Type"].value_counts()
    if not type_counts.empty:
        dominant_type = type_counts.idxmax()
        dominant_type_count = int(type_counts.max())
        dominant_type_pct = round((dominant_type_count / total) * 100, 1)
    else:
        dominant_type = "N/A"
        dominant_type_count = 0
        dominant_type_pct = 0

    # Date range
    min_date = df["Enquiry Date"].min()
    max_date = df["Enquiry Date"].max()

    return {
        "total_enquiries": total,
        "peak_enquiry_day": {
            "date": peak_day_str,
            "count": peak_day_count,
        },
        "dominant_customer_type": {
            "type": dominant_type,
            "count": dominant_type_count,
            "percentage": dominant_type_pct,
        },
        "date_range": {
            "start": min_date.strftime("%Y-%m-%d") if pd.notna(min_date) else "N/A",
            "end": max_date.strftime("%Y-%m-%d") if pd.notna(max_date) else "N/A",
        },
    }


# ---------------------------------------------------------------------------
# Endpoint: Paginated Raw Data
# ---------------------------------------------------------------------------

# Columns to expose in the raw data table (subset of the full dataset)
TABLE_COLUMNS = [
    "S NO",
    "Enquiry Date",
    "Anonymized Customer ID",
    "Customer Type",
    "Model",
    "Variant",
    "Enquiry Status",
    "Source",
    "City",
    "State",
    "Consultant Name",
]


@app.get("/api/enquiries/data")
async def enquiries_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str = Query("", description="Search by customer ID or model"),
    customer_type: str = Query("", description="Filter by Customer Type"),
    sort_by: str = Query("", description="Column to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
):
    """
    Returns paginated, searchable, filterable, and sortable raw enquiry data.

    Query params:
        page          — Page number (1-indexed)
        page_size     — Rows per page (max 100)
        search        — Search string (matches customer ID, model, city)
        customer_type — Filter: 'Individual', 'Corporate', or '' for all
        sort_by       — Column name to sort by
        sort_order    — 'asc' or 'desc'
    """
    df = _load_data()

    # Select only the columns we expose
    available_cols = [c for c in TABLE_COLUMNS if c in df.columns]
    view = df[available_cols].copy()

    # Format enquiry date as string for JSON
    if "Enquiry Date" in view.columns:
        view["Enquiry Date"] = view["Enquiry Date"].dt.strftime("%Y-%m-%d %H:%M")

    # --- Filtering ---
    if customer_type:
        view = view[
            view["Customer Type"].str.lower() == customer_type.strip().lower()
        ]

    # --- Search ---
    if search:
        search_lower = search.strip().lower()
        mask = pd.Series([False] * len(view), index=view.index)
        for col in ["Anonymized Customer ID", "Model", "City", "Consultant Name"]:
            if col in view.columns:
                mask = mask | view[col].fillna("").astype(str).str.lower().str.contains(
                    search_lower, na=False
                )
        view = view[mask]

    # --- Sorting ---
    if sort_by and sort_by in view.columns:
        ascending = sort_order == "asc"
        view = view.sort_values(by=sort_by, ascending=ascending, na_position="last")

    # --- Pagination ---
    total_records = len(view)
    total_pages = max(1, (total_records + page_size - 1) // page_size)
    page = min(page, total_pages)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_data = view.iloc[start_idx:end_idx]

    # Replace NaN with None for clean JSON
    page_data = page_data.where(pd.notna(page_data), None)

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": page_data.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# Alias Endpoints (matches user spec naming)
# ---------------------------------------------------------------------------


@app.get("/api/summary")
async def summary():
    """
    Returns total enquiries and a breakdown of Individual vs. Corporate clients.
    This is the combined summary endpoint matching the project specification.
    """
    df = _load_data()
    total = len(df)

    counts = df["Customer Type"].value_counts().to_dict()
    individual_count = int(counts.get("Individual", 0))
    corporate_count = int(counts.get("Corporate", 0))

    return {
        "total_enquiries": total,
        "individual": {
            "count": individual_count,
            "percentage": round((individual_count / total) * 100, 2) if total > 0 else 0,
        },
        "corporate": {
            "count": corporate_count,
            "percentage": round((corporate_count / total) * 100, 2) if total > 0 else 0,
        },
    }


@app.get("/api/trend")
async def trend_alias(
    group_by: str = Query("day", pattern="^(day|week)$"),
):
    """
    Alias for /api/enquiries/trend — returns time-series data grouped by date.
    """
    return await enquiry_trend(group_by=group_by)


@app.get("/api/enquiries")
async def enquiries_alias(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str = Query("", description="Search by customer ID or model"),
    customer_type: str = Query("", description="Filter by Customer Type"),
    sort_by: str = Query("", description="Column to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
):
    """
    Alias for /api/enquiries/data — returns raw data with pagination, sorting,
    and search capabilities.
    """
    return await enquiries_data(
        page=page,
        page_size=page_size,
        search=search,
        customer_type=customer_type,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ---------------------------------------------------------------------------
# LangChain & LLM Chat Assistant Endpoints
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query about car dealership CRM data")
    provider: Optional[str] = Field(default=None, description="openai, anthropic, groq, or mock")
    api_key: Optional[str] = Field(default=None, description="Optional runtime API key")


_agent_instances: Dict[str, AskYourDataAgent] = {}


def _get_agent(provider: Optional[str] = None, api_key: Optional[str] = None) -> AskYourDataAgent:
    chosen_provider = (provider or os.getenv("LLM_PROVIDER", "openai")).strip().lower()

    if api_key:
        if chosen_provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif chosen_provider == "groq":
            os.environ["GROQ_API_KEY"] = api_key
        else:
            os.environ["OPENAI_API_KEY"] = api_key

    cache_key = f"{chosen_provider}_{bool(api_key)}"
    if cache_key not in _agent_instances:
        _agent_instances[cache_key] = AskYourDataAgent(provider=chosen_provider)
    return _agent_instances[cache_key]


@app.get("/api/chat/status")
async def chat_status():
    """Returns the current LLM configuration and agent readiness status."""
    current_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip()) and not os.getenv("OPENAI_API_KEY", "").startswith("your_")
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY", "").strip()) and not os.getenv("ANTHROPIC_API_KEY", "").startswith("your_")
    has_groq = bool(os.getenv("GROQ_API_KEY", "").strip()) and not os.getenv("GROQ_API_KEY", "").startswith("your_")

    active_model = "MockAnalyticsLLM (Built-in Dealership Engine)"
    if current_provider == "openai" and has_openai:
        active_model = f"OpenAI {OPENAI_MODEL_NAME}"
    elif current_provider == "anthropic" and has_anthropic:
        active_model = f"Anthropic {ANTHROPIC_MODEL_NAME}"
    elif current_provider == "groq" and has_groq:
        active_model = f"Groq {os.getenv('GROQ_MODEL_NAME', 'llama-3.3-70b-versatile')}"

    return {
        "status": "ready",
        "provider": current_provider,
        "active_model": active_model,
        "available_providers": [
            {"id": "openai", "name": "OpenAI (GPT-4o)", "has_key": has_openai},
            {"id": "anthropic", "name": "Anthropic (Claude 3.5 Sonnet)", "has_key": has_anthropic},
            {"id": "groq", "name": "Groq (Llama 3.3 70B)", "has_key": has_groq},
            {"id": "mock", "name": "Built-in Analytics Engine (Offline/Ready)", "has_key": True},
        ],
        "features": [
            "LangChain 5-step agent flow (Plan, Sandboxed Query, Self-check, Chart, Summary)",
            "Automated retry loop with error diagnosis",
            "Plotly interactive chart generation",
            "Multi-turn conversation memory"
        ]
    }


@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Executes natural language analytics queries on the car dealership CRM data using LangChain.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        agent = _get_agent(provider=payload.provider, api_key=payload.api_key)
        response = agent.ask(payload.message)

        return {
            "success": response.success,
            "question": response.question,
            "summary": response.summary,
            "recommendation": response.recommendation,
            "plan": response.plan,
            "code": response.code,
            "chart_spec": response.chart_spec,
            "assumptions": response.assumptions,
            "how_i_got_this": response.how_i_got_this(),
            "latency_ms": response.latency_ms,
            "attempts": response.attempts,
            "error": response.error,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(exc)}")

