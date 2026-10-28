"""
KIA Dashboard Export — Aggregates all analysis CSV/JSON outputs
into a single master dashboard_metrics.json for the React frontend.
"""

import json
import os
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path("d:/KIA/data/analysis_results")
JSON_DIR = RESULTS_DIR / "json"


def safe_json(obj):
    """Handle numpy/pandas types for JSON serialisation."""
    import numpy as np

    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    return obj


def load_json(filename):
    """Load a JSON file from JSON_DIR, return {} on failure."""
    path = JSON_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_csv(filename, max_rows=None):
    """Load a CSV from RESULTS_DIR, return list of dicts."""
    path = RESULTS_DIR / filename
    if not path.exists():
        return []
    df = pd.read_csv(path)
    if max_rows:
        df = df.head(max_rows)
    records = df.where(df.notna(), None).to_dict(orient="records")
    return [{k: safe_json(v) for k, v in row.items()} for row in records]


def generate_master_dashboard():
    """
    Aggregate all per-module JSON files into a single master JSON
    that the frontend dashboard can consume in one request.
    """
    print("--- Generating master dashboard_metrics.json ---")

    master = {
        "executive_summary": load_json("executive_summary.json"),
        "geographic": load_json("geographic_dashboard.json"),
        "product_demand": load_json("product_demand_dashboard.json"),
        "customer_segmentation": load_json("customer_segmentation_dashboard.json"),
        "exchange_funnel": load_json("exchange_funnel_dashboard.json"),
        "pricing": load_json("pricing_dashboard.json"),
        "lost_leads": load_json("lost_leads_dashboard.json"),
        "campaign_digital": load_json("campaign_digital_dashboard.json"),
        "lead_velocity": load_json("lead_velocity_dashboard.json"),
        # Legacy / core tables
        "funnel_summary": load_csv("funnel_summary.csv"),
        "source_performance": load_csv("source_performance.csv"),
        "lead_type_performance": load_csv("lead_type_performance.csv"),
        "model_performance": load_csv("model_performance.csv"),
        "consultant_performance": load_csv("consultant_performance.csv", max_rows=30),
        "td_impact": load_csv("td_impact.csv"),
        "monthly_trends": load_csv("monthly_trends.csv"),
        "followup_bucket_performance": load_csv("followup_bucket_performance.csv"),
        "aging_bucket_performance": load_csv("aging_bucket_performance.csv"),
    }

    output_path = JSON_DIR / "dashboard_metrics.json"
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=2, default=safe_json)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Saved master dashboard: {output_path} ({size_mb:.2f} MB)")
    return master


if __name__ == "__main__":
    generate_master_dashboard()
