"""
Data loading, dynamic schema inspection, and SQLite mirroring for Ask Your Data.
Adapts to the real schema without assuming fixed column names.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np

from ask_your_data.config import DATA_PATH, ROOT_DIR

_DF_CACHE: Optional[pd.DataFrame] = None
_SQLITE_PATH: Path = ROOT_DIR / "data" / "leads.db"


def resolve_source_file() -> Path:
    """Finds available CRM file in data/ or root."""
    candidates = [
        DATA_PATH,
        ROOT_DIR / "data" / "master_clean.csv",
        ROOT_DIR / "enq (1).xlsx",
        ROOT_DIR / "raw_enq.xlsx",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"Could not locate dataset. Checked: {[str(c) for c in candidates]}"
    )


def load_raw_dataset(source_path: Path) -> pd.DataFrame:
    """Reads raw Excel or CSV into pandas."""
    if source_path.suffix.lower() in [".xlsx", ".xls"]:
        xls = pd.ExcelFile(source_path)
        frames = [pd.read_excel(source_path, sheet_name=s) for s in xls.sheet_names]
        df = pd.concat(frames, ignore_index=True)
    else:
        df = pd.read_csv(source_path, low_memory=False)
    return df


def enrich_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inspects columns dynamically and adds standardized dealership analysis helper
    columns while strictly preserving all original columns and values.
    """
    df = df.copy()

    # Identify date columns
    date_candidates = [
        "Enquiry Date", "Test Drive Date", "Booking Date",
        "Retail date", "Delivery Date", "Lost Date"
    ]
    for col in date_candidates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 1. Lead Conversion (Retail Purchase)
    # Retail date not null OR Enquiry Status == 'Retail'
    is_retail = pd.Series(False, index=df.index)
    if "Retail date" in df.columns:
        is_retail = is_retail | df["Retail date"].notnull()
    if "Enquiry Status" in df.columns:
        is_retail = is_retail | (df["Enquiry Status"].astype(str).str.strip().str.title() == "Retail")

    df["is_converted"] = is_retail.astype(int)
    df["converted"] = np.where(is_retail, "Yes", "No")

    # 2. Test Drive Done
    is_td = pd.Series(False, index=df.index)
    if "Test Drive Date" in df.columns:
        is_td = is_td | df["Test Drive Date"].notnull()
    if "TD Status" in df.columns:
        is_td = is_td | (df["TD Status"].astype(str).str.strip().str.title() == "Done")
    if "No. of test drive given" in df.columns:
        td_count = pd.to_numeric(df["No. of test drive given"], errors="coerce").fillna(0)
        is_td = is_td | (td_count > 0)

    df["is_test_drive"] = is_td.astype(int)
    df["test_drive_done"] = np.where(is_td, "Yes", "No")

    # 3. Booking Done
    is_booked = pd.Series(False, index=df.index)
    if "Booking Date" in df.columns:
        is_booked = is_booked | df["Booking Date"].notnull()
    if "Booking No" in df.columns:
        is_booked = is_booked | df["Booking No"].notnull()
    if "Enquiry Status" in df.columns:
        is_booked = is_booked | df["Enquiry Status"].astype(str).str.strip().str.title().isin(["Booking", "Retail"])

    df["is_booked"] = is_booked.astype(int)
    df["booked"] = np.where(is_booked, "Yes", "No")

    # 4. Standard aliases for intuitive natural language access
    if "Enquiry Date" in df.columns:
        df["lead_date"] = df["Enquiry Date"]
        df["lead_month"] = df["Enquiry Date"].dt.strftime("%Y-%m")
    if "Model" in df.columns:
        df["car_model"] = df["Model"].fillna("UNKNOWN").astype(str).str.strip()
    if "Source" in df.columns:
        df["lead_source"] = df["Source"].fillna("UNKNOWN").astype(str).str.strip()
    if "Type" in df.columns:
        df["lead_warmth"] = df["Type"].fillna("UNKNOWN").astype(str).str.strip()
    if "Consultant Name" in df.columns:
        df["consultant"] = df["Consultant Name"].fillna("UNKNOWN").astype(str).str.strip()
    if "City" in df.columns:
        df["city_clean"] = df["City"].fillna("UNKNOWN").astype(str).str.strip()
    if "Followup Count" in df.columns:
        df["followup_count"] = pd.to_numeric(df["Followup Count"], errors="coerce").fillna(0).astype(int)

    return df


def mirror_to_sqlite(df: pd.DataFrame, sqlite_path: Path = _SQLITE_PATH) -> None:
    """Mirrors the pandas dataframe into a local SQLite table 'leads'."""
    try:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        # Convert Timestamp columns to ISO string for SQLite compatibility
        df_sql = df.copy()
        for col in df_sql.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
            df_sql[col] = df_sql[col].dt.strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(sqlite_path) as conn:
            df_sql.to_sql("leads", conn, if_exists="replace", index=False)
        print(f"[Info] Mirrored {len(df)} records into SQLite: {sqlite_path}")
    except Exception as e:
        print(f"[Warning] SQLite mirroring error: {e}")


def load_dataset(force_reload: bool = False) -> pd.DataFrame:
    """Loads and caches the cleaned dataset, mirroring it to SQLite on first load."""
    global _DF_CACHE
    if _DF_CACHE is not None and not force_reload:
        return _DF_CACHE

    source_path = resolve_source_file()
    print(f"[Info] Loading dataset from: {source_path}")
    raw_df = load_raw_dataset(source_path)
    enriched_df = enrich_schema(raw_df)

    # Mirror to SQLite in background
    mirror_to_sqlite(enriched_df)

    _DF_CACHE = enriched_df
    return _DF_CACHE


def get_sqlite_connection() -> sqlite3.Connection:
    """Returns a connection to the mirrored SQLite database."""
    if not _SQLITE_PATH.exists():
        load_dataset()
    return sqlite3.connect(_SQLITE_PATH)


def describe_schema(
    filter_pattern: Optional[str] = None,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Returns a comprehensive dictionary describing the real schema:
    columns, dtypes, non-null counts, unique count, and sample values.
    """
    if df is None:
        df = load_dataset()

    schema_info = []
    for col in df.columns:
        if filter_pattern and filter_pattern.lower() not in col.lower():
            continue

        non_null_count = int(df[col].notnull().sum())
        null_count = int(df[col].isnull().sum())
        unique_count = int(df[col].nunique())
        
        # Grab up to 3 non-null representative samples
        sample_vals = df[col].dropna().unique()[:3].tolist()
        sample_formatted = [str(v) for v in sample_vals]

        schema_info.append({
            "column": col,
            "dtype": str(df[col].dtype),
            "non_null": non_null_count,
            "null_count": null_count,
            "unique_count": unique_count,
            "samples": sample_formatted,
        })

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": schema_info,
    }


def format_schema_for_prompt(
    filter_pattern: Optional[str] = None,
    df: Optional[pd.DataFrame] = None
) -> str:
    """Formats the schema into a concise, readable string for LLM prompts."""
    schema = describe_schema(filter_pattern=filter_pattern, df=df)
    lines = [
        f"Dataset Shape: {schema['total_rows']} rows x {schema['total_columns']} columns\n",
        "Key Columns & Real Schema (Column Name | Data Type | Non-Null | Unique | Sample Values):",
        "-" * 80
    ]

    for col in schema["columns"]:
        samples = ", ".join(col["samples"][:3])
        lines.append(
            f"- `{col['column']}` ({col['dtype']}): {col['unique_count']} unique values. Samples: [{samples}]"
        )

    lines.extend([
        "-" * 80,
        "Business Semantics Guide:",
        "• Conversion (Retail): `converted` ('Yes'/'No') or `is_converted` (1/0), or `Retail date.notnull()`",
        "• Test Drive Done: `test_drive_done` ('Yes'/'No') or `is_test_drive` (1/0), or `TD Status == 'Done'`",
        "• Booking Done: `booked` ('Yes'/'No') or `is_booked` (1/0), or `Booking Date.notnull()`",
        "• Vehicle Model: `car_model` or `Model` (e.g. 'SONET', 'NEW SELTOS', 'CARENS')",
        "• Enquiry Source: `lead_source` or `Source` (e.g. 'Hyperlocal', 'Walkin', 'Referral')",
        "• Lead Warmth: `lead_warmth` or `Type` ('Hot', 'Warm', 'Cold')",
        "• Sales Consultant: `consultant` or `Consultant Name`",
        "• City / Location: `city_clean` or `City` (e.g. 'BHUBANESWAR', 'CUTTACK')",
        "• Enquiry Date: `lead_date` or `Enquiry Date`"
    ])
    return "\n".join(lines)
