import json
import os
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------

BASE_DIR = Path("d:/KIA")
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "analysis_results"
PLOTS_DIR = RESULTS_DIR / "plots"
JSON_DIR = RESULTS_DIR / "json"

EXCEL_CANDIDATES = [
    BASE_DIR / "enq (1).xlsx",
    BASE_DIR / "raw_enq.xlsx",
    DATA_DIR / "master_clean.csv",
]

MIN_LOCATION_VOLUME = 20

# Consistent colour palette across all charts
PALETTE = {
    "primary": "#0B5394",
    "secondary": "#E45756",
    "accent": "#54A24B",
    "info": "#72B7B2",
    "warning": "#EECA3B",
    "neutral": "#B0BEC5",
    "gradient": ["#0B5394", "#1976D2", "#42A5F5", "#90CAF9", "#BBDEFB"],
    "categorical": ["#0B5394", "#E45756", "#54A24B", "#EECA3B", "#72B7B2",
                     "#AF7AA1", "#FF9DA7", "#9C755F", "#BAB0AC", "#4C78A8"],
}

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------


def resolve_data_source():
    for path in EXCEL_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No CRM data found. Place 'enq (1).xlsx' in the project root."
    )


def load_data():
    source = resolve_data_source()
    print(f"--- Loading data from {source} ---")

    if source.suffix.lower() in {".xlsx", ".xls"}:
        xls = pd.ExcelFile(source)
        frames = [pd.read_excel(source, sheet_name=name) for name in xls.sheet_names]
        df = pd.concat(frames, ignore_index=True)
    else:
        df = pd.read_csv(source)

    date_cols = [
        "Enquiry Date",
        "Test Drive Date",
        "Booking Date",
        "Retail date",
        "Lost Date",
        "Delivery Date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    numeric_cols = [
        "Quoted Price",
        "Expected Price",
        "Final Buying Price",
        "MOB Quotation Email Count",
        "DMS Quotation Email Count",
        "enquiry aging days",
        "Followup Count",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Total Quotation Email Count" not in df.columns:
        mob = df.get("MOB Quotation Email Count", pd.Series(0, index=df.index)).fillna(0)
        dms = df.get("DMS Quotation Email Count", pd.Series(0, index=df.index)).fillna(0)
        df["Total Quotation Email Count"] = mob + dms

    print(f"Total Rows: {len(df)}")
    return df


# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------


def safe_rate(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def safe_json(obj):
    """Make an object JSON-serialisable (handle numpy/pandas types)."""
    if obj is None:
        return None
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj) if not np.isnan(obj) else None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, pd.Series):
        return obj.tolist()
    if isinstance(obj, (dict, list, str, int, float)):
        return obj
    try:
        if pd.isna(obj):
            return None
    except (ValueError, TypeError):
        pass
    # Fallback: convert to string to prevent circular reference
    return str(obj)


def df_to_json_records(df):
    """Convert a DataFrame to a list of dicts with JSON-safe values."""
    records = df.where(df.notna(), None).to_dict(orient="records")
    cleaned = []
    for row in records:
        cleaned.append({k: safe_json(v) for k, v in row.items()})
    return cleaned


def save_json(data, filename):
    """Write a dict/list to a JSON file in JSON_DIR."""
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    path = JSON_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=safe_json)
    print(f"Saved JSON: {path}")


def prepare_funnel_flags(df):
    df = df.copy()
    df["Is_Enquiry"] = True
    df["Is_TD"] = (
        df["Test Drive Date"].notnull()
        | (df.get("TD Status", pd.Series(dtype=object)) == "Done")
        | (df.get("No. of test drive given", pd.Series(0, index=df.index)).fillna(0) > 0)
    )
    df["Is_Booking"] = df["Booking Date"].notnull()
    df["Is_Retail"] = df["Retail date"].notnull() | (
        df.get("Enquiry Status", pd.Series(dtype=object)) == "Retail"
    )
    df["Is_Lost"] = (
        df.get("lost reason", pd.Series(dtype=object)).notnull()
        | df.get("lost due to", pd.Series(dtype=object)).notnull()
        | df.get("Enquiry Status", pd.Series(dtype=object))
        .astype(str)
        .str.contains("Cancel", na=False)
    )

    conditions = [
        df["Is_Retail"],
        df["Is_Booking"] & ~df["Is_Retail"],
        df["Is_Lost"],
    ]
    choices = ["Retailed", "Booked (Active)", "Lost"]
    df["Outcome"] = np.select(conditions, choices, default="Active")

    df["Sales_Cycle_Days"] = np.where(
        df["Is_Retail"] & df["Enquiry Date"].notnull() & df["Retail date"].notnull(),
        (df["Retail date"] - df["Enquiry Date"]).dt.days,
        np.where(
            df["Is_Lost"] & df["Enquiry Date"].notnull() & df["Lost Date"].notnull(),
            (df["Lost Date"] - df["Enquiry Date"]).dt.days,
            np.where(
                df["Is_Booking"] & df["Enquiry Date"].notnull() & df["Booking Date"].notnull(),
                (df["Booking Date"] - df["Enquiry Date"]).dt.days,
                df.get("enquiry aging days", pd.Series(dtype=float)),
            ),
        ),
    )
    return df


def save_plot(fig, filename):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved plot: {path}")


def performance_table(df, group_cols, min_volume=0):
    grouped = df.groupby(group_cols, dropna=False).agg(
        Enquiries=("Is_Enquiry", "sum"),
        Test_Drives=("Is_TD", "sum"),
        Bookings=("Is_Booking", "sum"),
        Retails=("Is_Retail", "sum"),
        Avg_Sales_Cycle_Days=("Sales_Cycle_Days", "mean"),
    ).reset_index()

    grouped["TD_Rate"] = grouped["Test_Drives"] / grouped["Enquiries"]
    grouped["Booking_Rate"] = grouped["Bookings"] / grouped["Enquiries"]
    grouped["Retail_Rate"] = grouped["Retails"] / grouped["Enquiries"]
    if min_volume:
        grouped = grouped[grouped["Enquiries"] >= min_volume]
    return grouped.sort_values(by="Retails", ascending=False)


# ---------------------------------------------------------------------------
# Module 1: Geographic & Regional Conversion
# ---------------------------------------------------------------------------


def analyze_geographic(df):
    print("\n--- Module 1: Geographic & Regional Conversion ---")

    # --- Core performance tables ---
    city_perf = performance_table(
        df, ["City", "State", "Pin No.", "Location"], min_volume=MIN_LOCATION_VOLUME
    )
    city_perf.to_csv(RESULTS_DIR / "geographic_city_performance.csv", index=False)

    state_perf = performance_table(df, ["State"], min_volume=MIN_LOCATION_VOLUME)
    state_perf.to_csv(RESULTS_DIR / "geographic_state_performance.csv", index=False)

    # Simple city-level aggregation (without pin/location for cleaner ranking)
    city_simple = performance_table(df, ["City"], min_volume=MIN_LOCATION_VOLUME)

    ranked = city_simple.sort_values("Retail_Rate", ascending=False)
    top5 = ranked.head(5)
    bottom5 = ranked.tail(5).sort_values("Retail_Rate")
    top5.to_csv(RESULTS_DIR / "geographic_top5_cities.csv", index=False)
    bottom5.to_csv(RESULTS_DIR / "geographic_bottom5_cities.csv", index=False)

    # --- Chart 1: Top 15 cities by lead volume ---
    chart_df = city_simple.sort_values("Enquiries", ascending=False).head(15)
    fig, ax1 = plt.subplots(figsize=(14, 6))
    bars = ax1.bar(
        range(len(chart_df)), chart_df["Enquiries"].values,
        color=PALETTE["primary"], alpha=0.85, label="Enquiries", zorder=2,
    )
    ax1.set_ylabel("Lead Volume", fontsize=12)
    ax1.set_title("Top 15 Cities — Lead Volume & Conversion Rate", fontsize=14, fontweight="bold")
    ax1.set_xticks(range(len(chart_df)))
    ax1.set_xticklabels(chart_df["City"].values, rotation=45, ha="right", fontsize=9)

    ax2 = ax1.twinx()
    ax2.plot(
        range(len(chart_df)), chart_df["Retail_Rate"].values * 100,
        color=PALETTE["secondary"], marker="o", linewidth=2, markersize=7,
        label="Retail Rate %", zorder=3,
    )
    ax2.set_ylabel("Retail Rate (%)", fontsize=12, color=PALETTE["secondary"])
    ax2.tick_params(axis="y", colors=PALETTE["secondary"])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    ax1.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, "geographic_lead_volume.png")

    # --- Chart 2: State-level horizontal bar ---
    state_chart = state_perf.sort_values("Enquiries", ascending=True)
    fig, ax = plt.subplots(figsize=(10, max(4, len(state_chart) * 0.5)))
    colors = [PALETTE["primary"] if v > state_chart["Retail_Rate"].median()
              else PALETTE["neutral"] for v in state_chart["Retail_Rate"].values]
    ax.barh(state_chart["State"].astype(str), state_chart["Enquiries"], color=colors, edgecolor="white")
    for i, (enq, rate) in enumerate(zip(state_chart["Enquiries"], state_chart["Retail_Rate"])):
        ax.text(enq + 5, i, f"{rate:.1%}", va="center", fontsize=9, color=PALETTE["secondary"])
    ax.set_xlabel("Lead Volume")
    ax.set_title("State-Level Lead Distribution (label = Retail Rate)", fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, "geographic_state_bar.png")

    # --- Chart 3: City bubble chart (top 20) ---
    bubble_df = city_simple.head(20).copy()
    bubble_df = bubble_df[bubble_df["Retails"] > 0]
    if len(bubble_df) > 2:
        fig, ax = plt.subplots(figsize=(12, 7))
        scatter = ax.scatter(
            bubble_df["Enquiries"], bubble_df["Retail_Rate"] * 100,
            s=bubble_df["Retails"] * 15, alpha=0.65,
            c=bubble_df["Retail_Rate"], cmap="RdYlGn", edgecolors="white", linewidth=0.8,
        )
        for _, row in bubble_df.iterrows():
            ax.annotate(
                row["City"], (row["Enquiries"], row["Retail_Rate"] * 100),
                fontsize=7, ha="center", va="bottom",
            )
        ax.set_xlabel("Lead Volume (Enquiries)", fontsize=11)
        ax.set_ylabel("Retail Conversion Rate (%)", fontsize=11)
        ax.set_title("City Performance Bubble Chart (size = Retails)", fontsize=13, fontweight="bold")
        plt.colorbar(scatter, ax=ax, label="Retail Rate")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "geographic_city_bubble.png")

    # --- Chart 4: Heatmap ---
    heatmap_df = city_simple.head(20).set_index("City")[["Enquiries", "Retail_Rate"]]
    fig, ax = plt.subplots(figsize=(8, 10))
    sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax, linewidths=0.5)
    ax.set_title("Regional Lead Distribution & Conversion Heatmap", fontsize=13, fontweight="bold")
    save_plot(fig, "geographic_conversion_heatmap.png")

    # --- JSON export ---
    geo_json = {
        "top5_cities": df_to_json_records(top5),
        "bottom5_cities": df_to_json_records(bottom5),
        "state_performance": df_to_json_records(state_perf),
        "city_performance": df_to_json_records(city_simple.head(30)),
        "total_cities": int(city_simple["City"].nunique()),
        "total_states": int(state_perf["State"].nunique()),
    }
    save_json(geo_json, "geographic_dashboard.json")

    print("Top 5 cities by conversion:")
    print(top5[["City", "Enquiries", "Retails", "Retail_Rate"]].to_string(index=False))
    return city_perf


# ---------------------------------------------------------------------------
# Module 2: Product & Variant Demand
# ---------------------------------------------------------------------------


def analyze_product_variant(df):
    print("\n--- Module 2: Product & Variant Demand ---")

    fuel_perf = performance_table(df, ["Fuel type"], min_volume=0)
    fuel_perf.to_csv(RESULTS_DIR / "fuel_type_performance.csv", index=False)

    color_perf = (
        df.groupby("Color", dropna=False)
        .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
    )
    color_perf["Retail_Rate"] = color_perf["Retails"] / color_perf["Enquiries"]
    color_perf = color_perf.sort_values("Enquiries", ascending=False)
    color_perf.to_csv(RESULTS_DIR / "color_preference.csv", index=False)

    variant_perf = performance_table(df, ["Model", "Variant", "Fuel type", "Color"], min_volume=0)
    variant_perf.to_csv(RESULTS_DIR / "variant_fuel_color_performance.csv", index=False)

    model_fuel = performance_table(df, ["Model", "Fuel type"], min_volume=0)
    model_fuel.to_csv(RESULTS_DIR / "model_fuel_crosstab.csv", index=False)

    # --- Chart 1: Fuel type volume & conversion (dual axis) ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fuel_sorted = fuel_perf.sort_values("Enquiries", ascending=False)
    sns.barplot(data=fuel_sorted, x="Fuel type", y="Enquiries", hue="Fuel type",
                palette=PALETTE["categorical"][:len(fuel_sorted)], legend=False, ax=axes[0])
    axes[0].set_title("Lead Volume by Fuel Type", fontsize=12, fontweight="bold")
    for p in axes[0].patches:
        axes[0].annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=10, fontweight="bold")

    sns.barplot(data=fuel_sorted, x="Fuel type", y="Retail_Rate", hue="Fuel type",
                palette=PALETTE["categorical"][:len(fuel_sorted)], legend=False, ax=axes[1])
    axes[1].set_title("Retail Conversion Rate by Fuel Type", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Retail Rate")
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_height():.1%}", (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=10, fontweight="bold")
    fig.tight_layout()
    save_plot(fig, "fuel_type_volume_conversion.png")

    # --- Chart 2: Model × Fuel Type heatmap ---
    crosstab = model_fuel.pivot_table(index="Model", columns="Fuel type",
                                       values="Retail_Rate", aggfunc="first")
    if crosstab.shape[0] > 1 and crosstab.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.heatmap(crosstab, annot=True, fmt=".2%", cmap="RdYlGn", ax=ax,
                    linewidths=0.5, vmin=0)
        ax.set_title("Retail Conversion Rate: Model × Fuel Type", fontsize=13, fontweight="bold")
        fig.tight_layout()
        save_plot(fig, "model_fuel_heatmap.png")

    # --- Chart 3: Stacked bar — variant demand by model (top 5 models) ---
    top_models = df["Model"].value_counts().head(5).index.tolist()
    model_var = (
        df[df["Model"].isin(top_models)]
        .groupby(["Model", "Variant"], dropna=False)
        .agg(Enquiries=("Is_Enquiry", "sum"))
        .reset_index()
        .sort_values(["Model", "Enquiries"], ascending=[True, False])
    )
    # Keep top 5 variants per model
    model_var = model_var.groupby("Model").head(5)
    if len(model_var) > 2:
        fig, ax = plt.subplots(figsize=(14, 6))
        pivot = model_var.pivot_table(index="Model", columns="Variant", values="Enquiries", fill_value=0)
        pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20", edgecolor="white")
        ax.set_title("Top Variant Demand by Model (Top 5 Variants Each)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Lead Volume")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=7)
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        save_plot(fig, "variant_demand_stacked.png")

    # --- Chart 4: Color preference ---
    top_colors = color_perf.head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(top_colors["Color"].astype(str), top_colors["Enquiries"],
                  color=PALETTE["primary"], alpha=0.85)
    ax.set_title("Top 10 Color Preferences by Lead Volume", fontsize=13, fontweight="bold")
    ax.set_ylabel("Lead Volume")
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    for bar, rate in zip(bars, top_colors["Retail_Rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"{rate:.1%}", ha="center", fontsize=8, color=PALETTE["secondary"])
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, "color_preference.png")

    # --- Chart 5: Color × Model matrix ---
    color_model = (
        df.groupby(["Model", "Color"], dropna=False)
        .agg(Enquiries=("Is_Enquiry", "sum"))
        .reset_index()
    )
    cm_pivot = color_model.pivot_table(index="Color", columns="Model", values="Enquiries", fill_value=0)
    cm_pivot = cm_pivot.loc[cm_pivot.sum(axis=1).nlargest(10).index]
    cm_pivot = cm_pivot.astype(int)
    if cm_pivot.shape[0] > 1 and cm_pivot.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.heatmap(cm_pivot, annot=True, fmt="d", cmap="Blues", ax=ax, linewidths=0.5)
        ax.set_title("Color × Model Preference Matrix (Lead Count)", fontsize=13, fontweight="bold")
        fig.tight_layout()
        save_plot(fig, "color_model_heatmap.png")

    # --- JSON export ---
    product_json = {
        "fuel_type_performance": df_to_json_records(fuel_perf),
        "color_preference": df_to_json_records(color_perf.head(15)),
        "model_fuel_crosstab": df_to_json_records(model_fuel),
        "top_variant_demand": df_to_json_records(model_var) if len(model_var) > 0 else [],
    }
    save_json(product_json, "product_demand_dashboard.json")
    return fuel_perf


# ---------------------------------------------------------------------------
# Module 3: Customer Segmentation
# ---------------------------------------------------------------------------


def analyze_customer_segmentation(df):
    print("\n--- Module 3: Customer Segmentation ---")

    segment_perf = performance_table(df, ["Customer Type"], min_volume=0)
    segment_perf.to_csv(RESULTS_DIR / "customer_segment_performance.csv", index=False)

    corporate_perf = performance_table(
        df[df["Customer Type"].astype(str).str.upper() == "CORPORATE"],
        ["corporate Name", "Corporate Category"],
        min_volume=5,
    )
    corporate_perf.to_csv(RESULTS_DIR / "corporate_account_performance.csv", index=False)

    category_perf = performance_table(df, ["Corporate Category"], min_volume=0)
    category_perf.to_csv(RESULTS_DIR / "corporate_category_performance.csv", index=False)

    # Sales cycle comparison
    cycle_by_segment = (
        df.groupby("Customer Type")
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Avg_Sales_Cycle_All=("Sales_Cycle_Days", "mean"),
            Avg_Sales_Cycle_Retailed=(
                "Sales_Cycle_Days",
                lambda s: s[df.loc[s.index, "Is_Retail"]].mean(),
            ),
            Median_Sales_Cycle_Retailed=(
                "Sales_Cycle_Days",
                lambda s: s[df.loc[s.index, "Is_Retail"]].median(),
            ),
        )
        .reset_index()
    )
    cycle_by_segment.to_csv(RESULTS_DIR / "customer_sales_cycle.csv", index=False)

    # Monthly trend by customer type
    monthly_seg = (
        df.groupby(["Enquiry Month", "Customer Type"])
        .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
    )
    monthly_seg["Retail_Rate"] = monthly_seg["Retails"] / monthly_seg["Enquiries"]
    monthly_seg.to_csv(RESULTS_DIR / "customer_monthly_trend.csv", index=False)

    # --- Chart 1: Segment comparison (grouped bar) ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    plot_df = segment_perf.melt(
        id_vars=["Customer Type"],
        value_vars=["Enquiries", "Retails"],
        var_name="Metric", value_name="Count",
    )
    sns.barplot(data=plot_df, x="Customer Type", y="Count", hue="Metric",
                palette=[PALETTE["primary"], PALETTE["accent"]], ax=axes[0])
    axes[0].set_title("Lead Volume & Retails by Segment", fontsize=12, fontweight="bold")
    for p in axes[0].patches:
        axes[0].annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=9)

    # Conversion rate comparison
    sns.barplot(data=segment_perf, x="Customer Type", y="Retail_Rate", hue="Customer Type",
                palette=[PALETTE["primary"], PALETTE["secondary"]], legend=False, ax=axes[1])
    axes[1].set_title("Retail Conversion Rate by Segment", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Retail Rate")
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_height():.1%}", (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=10, fontweight="bold")
    fig.tight_layout()
    save_plot(fig, "customer_segment_volume.png")

    # --- Chart 2: Sales cycle box plot (retailed leads only) ---
    retailed = df[df["Is_Retail"] & df["Sales_Cycle_Days"].notna()].copy()
    if len(retailed) > 10:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=retailed, x="Customer Type", y="Sales_Cycle_Days",
                    palette=[PALETTE["primary"], PALETTE["secondary"]], ax=ax,
                    showfliers=False)
        ax.set_title("Sales Cycle Duration (Retailed Leads)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Days to Retail")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "customer_sales_cycle_boxplot.png")

    # --- Chart 3: Corporate category ranking ---
    corp_cat = category_perf[category_perf["Corporate Category"].astype(str).str.upper() != "INDIVIDUAL"]
    if len(corp_cat) > 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        corp_cat_sorted = corp_cat.sort_values("Enquiries", ascending=True)
        ax.barh(corp_cat_sorted["Corporate Category"].astype(str), corp_cat_sorted["Enquiries"],
                color=PALETTE["info"])
        ax.set_title("Corporate Category Lead Volume", fontsize=13, fontweight="bold")
        ax.set_xlabel("Lead Volume")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "corporate_category_ranking.png")

    # --- Chart 4: Monthly trend by segment ---
    if len(monthly_seg) > 2:
        fig, ax = plt.subplots(figsize=(12, 5))
        for seg_type in monthly_seg["Customer Type"].unique():
            seg_data = monthly_seg[monthly_seg["Customer Type"] == seg_type].sort_values("Enquiry Month")
            ax.plot(seg_data["Enquiry Month"], seg_data["Enquiries"], marker="o", label=seg_type, linewidth=2)
            ax.fill_between(seg_data["Enquiry Month"], seg_data["Enquiries"], alpha=0.1)
        ax.set_title("Monthly Lead Volume by Customer Type", fontsize=13, fontweight="bold")
        ax.set_ylabel("Enquiries")
        ax.legend()
        ax.grid(alpha=0.3)
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        save_plot(fig, "customer_monthly_trend.png")

    # --- JSON export ---
    seg_json = {
        "segment_performance": df_to_json_records(segment_perf),
        "corporate_accounts": df_to_json_records(corporate_perf.head(20)),
        "category_performance": df_to_json_records(category_perf),
        "sales_cycle": df_to_json_records(cycle_by_segment),
        "monthly_trend": df_to_json_records(monthly_seg),
    }
    save_json(seg_json, "customer_segmentation_dashboard.json")
    return segment_perf


# ---------------------------------------------------------------------------
# Module 4: Trade-In / Exchange Funnel
# ---------------------------------------------------------------------------


def analyze_exchange_funnel(df):
    print("\n--- Module 4: Trade-In / Exchange Funnel ---")

    present_col = "Present Car(Y/N)"
    exchange_col = "Interested in Exchange(Y/N)"

    exchange_df = df.copy()
    exchange_df["Has_Present_Car"] = exchange_df[present_col].eq("Y")
    exchange_df["Interested_In_Exchange"] = exchange_df[exchange_col].eq("Y")
    exchange_df["Evaluation_Done"] = exchange_df.get(
        "Old Car Evaluation Done", pd.Series(dtype=object)
    ).astype(str).str.upper().eq("Y")
    exchange_df["Exchange_Completed"] = exchange_df.get(
        "Exchange Done", pd.Series(dtype=object)
    ).astype(str).str.upper().eq("Y")

    # Build funnel — note Exchange Done and Exchange Channel are empty in the dataset
    exchange_done_count = int(exchange_df["Exchange_Completed"].sum())
    has_exchange_data = exchange_done_count > 0

    funnel_stages = [
        ("Total Enquiries", len(exchange_df)),
        ("Has Present Car", int(exchange_df["Has_Present_Car"].sum())),
        ("Interested in Exchange", int(exchange_df["Interested_In_Exchange"].sum())),
        ("Old Car Evaluation Done", int(exchange_df["Evaluation_Done"].sum())),
    ]
    if has_exchange_data:
        funnel_stages.append(("Exchange Completed", exchange_done_count))
    funnel_stages.append(("Retailed", int(exchange_df["Is_Retail"].sum())))

    funnel_counts = pd.DataFrame(funnel_stages, columns=["Stage", "Count"])
    funnel_counts["Stage_Rate_of_Enquiry"] = funnel_counts["Count"] / len(exchange_df)
    funnel_counts.to_csv(RESULTS_DIR / "exchange_funnel.csv", index=False)

    # Conversion impact: exchange interest vs no interest
    impact = (
        exchange_df.groupby("Interested_In_Exchange")
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Bookings=("Is_Booking", "sum"),
            Retails=("Is_Retail", "sum"),
        )
        .reset_index()
    )
    impact["Interested_In_Exchange"] = impact["Interested_In_Exchange"].map(
        {True: "Interested (Y)", False: "Not Interested (N/Blank)"}
    )
    impact["Booking_Rate"] = impact["Bookings"] / impact["Enquiries"]
    impact["Retail_Rate"] = impact["Retails"] / impact["Enquiries"]
    impact.to_csv(RESULTS_DIR / "exchange_conversion_impact.csv", index=False)

    # OEM brand analysis
    oem_perf = performance_table(
        exchange_df[exchange_df["Interested_In_Exchange"]],
        ["OEM Maker", "OEM Model"],
        min_volume=10,
    )
    oem_perf.to_csv(RESULTS_DIR / "exchange_oem_model_performance.csv", index=False)

    oem_brand = (
        exchange_df[exchange_df["Has_Present_Car"]]
        .groupby("OEM Maker", dropna=True)
        .agg(Count=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
        .sort_values("Count", ascending=False)
    )
    oem_brand["Retail_Rate"] = oem_brand["Retails"] / oem_brand["Count"]
    oem_brand.to_csv(RESULTS_DIR / "exchange_oem_brand_summary.csv", index=False)

    # Exchange channel (note: may be empty)
    channel_col = exchange_df.get("Exchange Channel", pd.Series(dtype=object))
    if channel_col.notna().sum() > 0:
        channel_perf = performance_table(exchange_df, ["Exchange Channel"], min_volume=0)
        channel_perf.to_csv(RESULTS_DIR / "exchange_channel_performance.csv", index=False)

    # Present car holder conversion analysis
    present_car_conv = (
        exchange_df.groupby("Has_Present_Car")
        .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
    )
    present_car_conv["Retail_Rate"] = present_car_conv["Retails"] / present_car_conv["Enquiries"]
    present_car_conv["Has_Present_Car"] = present_car_conv["Has_Present_Car"].map(
        {True: "Has Present Car", False: "No Present Car"}
    )
    present_car_conv.to_csv(RESULTS_DIR / "present_car_conversion.csv", index=False)

    # --- Chart 1: Exchange funnel ---
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE["gradient"][min(i, len(PALETTE["gradient"]) - 1)]
              for i in range(len(funnel_counts))]
    colors[-1] = PALETTE["accent"]  # Retailed stage in green
    bars = ax.bar(range(len(funnel_counts)), funnel_counts["Count"], color=colors, edgecolor="white")
    ax.set_xticks(range(len(funnel_counts)))
    ax.set_xticklabels(funnel_counts["Stage"], rotation=25, ha="right", fontsize=9)
    ax.set_title("Trade-In / Exchange Funnel", fontsize=14, fontweight="bold")
    ax.set_ylabel("Count")
    for bar, val in zip(bars, funnel_counts["Count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 15,
                f"{int(val)}", ha="center", fontsize=10, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    if not has_exchange_data:
        ax.annotate("Note: 'Exchange Done' column is empty in CRM data",
                     xy=(0.5, 0.95), xycoords="axes fraction", ha="center",
                     fontsize=9, color="gray", style="italic")
    fig.tight_layout()
    save_plot(fig, "exchange_funnel.png")

    # --- Chart 2: Exchange interest impact on conversion ---
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(impact))
    bars = ax.bar(x, impact["Retail_Rate"] * 100, color=[PALETTE["accent"], PALETTE["neutral"]],
                  edgecolor="white", width=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(impact["Interested_In_Exchange"])
    ax.set_title("Retail Conversion: Exchange Interest vs No Interest", fontsize=13, fontweight="bold")
    ax.set_ylabel("Retail Rate (%)")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{bar.get_height():.1f}%", ha="center", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, "exchange_conversion_impact.png")

    # --- Chart 3: OEM brand market share pie ---
    top_oem = oem_brand.head(10)
    if len(top_oem) > 2:
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            top_oem["Count"], labels=top_oem["OEM Maker"],
            autopct="%1.1f%%", colors=PALETTE["categorical"][:len(top_oem)],
            pctdistance=0.8, startangle=140,
        )
        ax.set_title("Top Traded-In Brands (Present Car Holders)", fontsize=13, fontweight="bold")
        for text in autotexts:
            text.set_fontsize(8)
        fig.tight_layout()
        save_plot(fig, "exchange_oem_pie.png")

    # --- JSON export ---
    exchange_json = {
        "funnel": df_to_json_records(funnel_counts),
        "conversion_impact": df_to_json_records(impact),
        "oem_brands": df_to_json_records(oem_brand.head(15)),
        "present_car_conversion": df_to_json_records(present_car_conv),
        "data_quality_notes": {
            "exchange_done_populated": has_exchange_data,
            "exchange_channel_populated": bool(channel_col.notna().sum() > 0),
        },
    }
    save_json(exchange_json, "exchange_funnel_dashboard.json")
    return impact


# ---------------------------------------------------------------------------
# Module 5: Pricing & Negotiation Gap
# ---------------------------------------------------------------------------


def analyze_pricing_negotiation(df):
    print("\n--- Module 5: Pricing & Negotiation Gap ---")

    won = df[df["Is_Retail"]].copy()
    for col in ["Quoted Price", "Expected Price", "Final Buying Price"]:
        won[col] = pd.to_numeric(won.get(col, 0), errors="coerce")

    # Check data quality for Final Buying Price
    final_nonzero = (won["Final Buying Price"] > 0).sum()
    has_final_price = final_nonzero > 10

    if has_final_price:
        valid = won[(won["Quoted Price"] > 0) & (won["Final Buying Price"] > 0)].copy()
        valid["Negotiation_Gap"] = valid["Quoted Price"] - valid["Final Buying Price"]
        valid["Discount_Pct"] = (valid["Negotiation_Gap"] / valid["Quoted Price"]) * 100
        gap_label = "Negotiation Gap (Quoted − Final)"
        note = "Computed on won deals with non-zero Quoted and Final prices."
    else:
        # Fallback: use Quoted - Expected as "Customer Expectation Gap"
        valid = won[(won["Quoted Price"] > 0) & (won["Expected Price"] > 0)].copy()
        valid["Negotiation_Gap"] = valid["Quoted Price"] - valid["Expected Price"]
        valid["Discount_Pct"] = (valid["Negotiation_Gap"] / valid["Quoted Price"]) * 100
        gap_label = "Customer Expectation Gap (Quoted − Expected)"
        note = (
            "WARNING: Final Buying Price is entirely zero in this CRM export. "
            "Gap is computed as Quoted Price − Expected Price (customer expectation gap). "
            f"Only {final_nonzero} records have a non-zero Final Buying Price."
        )

    summary = pd.DataFrame({
        "Metric": [
            "Won Deals (Retail)",
            "Deals with Quoted Price > 0",
            "Deals with Expected Price > 0",
            "Deals with Final Price > 0",
            "Valid deals for gap calculation",
            f"Avg {gap_label}",
            f"Median {gap_label}",
            "Avg Discount % (Quoted basis)",
            "Avg Expected Price (non-zero)",
            "Avg Quoted Price (non-zero)",
        ],
        "Value": [
            len(won),
            (won["Quoted Price"] > 0).sum(),
            (won["Expected Price"] > 0).sum(),
            final_nonzero,
            len(valid),
            valid["Negotiation_Gap"].mean() if len(valid) else None,
            valid["Negotiation_Gap"].median() if len(valid) else None,
            valid["Discount_Pct"].mean() if len(valid) else None,
            won["Expected Price"].replace(0, np.nan).mean(),
            won["Quoted Price"].replace(0, np.nan).mean(),
        ],
    })
    summary["Notes"] = note
    summary.to_csv(RESULTS_DIR / "pricing_negotiation_summary.csv", index=False)

    # Gap by model
    model_gap = (
        valid.groupby("Model")
        .agg(
            Won_Deals=("Is_Retail", "sum"),
            Avg_Gap=("Negotiation_Gap", "mean"),
            Median_Gap=("Negotiation_Gap", "median"),
            Avg_Discount_Pct=("Discount_Pct", "mean"),
            Avg_Quoted=("Quoted Price", "mean"),
            Avg_Expected=("Expected Price", "mean"),
        )
        .reset_index()
        .sort_values("Avg_Gap", ascending=False)
    )
    model_gap.to_csv(RESULTS_DIR / "pricing_gap_by_model.csv", index=False)

    # Price buckets
    bucket_df = won.copy()
    bucket_df["Quoted_Bucket"] = pd.cut(
        bucket_df["Quoted Price"].replace(0, np.nan),
        bins=[0, 8_00_000, 12_00_000, 16_00_000, 25_00_000, np.inf],
        labels=["<8L", "8-12L", "12-16L", "16-25L", "25L+"],
    )
    bucket_perf = (
        bucket_df.groupby("Quoted_Bucket", observed=False)
        .agg(
            Won_Deals=("Is_Retail", "sum"),
            Avg_Quoted=("Quoted Price", "mean"),
            Avg_Expected=("Expected Price", "mean"),
            Avg_Final=("Final Buying Price", "mean"),
        )
        .reset_index()
    )
    bucket_perf.to_csv(RESULTS_DIR / "pricing_bucket_summary.csv", index=False)

    # --- Chart 1: Gap distribution ---
    if len(valid) > 5 and valid["Negotiation_Gap"].notna().any():
        fig, ax = plt.subplots(figsize=(10, 5))
        gap_data = valid["Negotiation_Gap"].dropna()
        # Filter extreme outliers for readability
        q1, q99 = gap_data.quantile(0.01), gap_data.quantile(0.99)
        gap_clipped = gap_data[(gap_data >= q1) & (gap_data <= q99)]
        sns.histplot(gap_clipped, kde=True, ax=ax, color=PALETTE["primary"], alpha=0.7, bins=30)
        ax.axvline(gap_data.mean(), color=PALETTE["secondary"], linestyle="--", linewidth=2,
                   label=f"Mean: ₹{gap_data.mean():,.0f}")
        ax.axvline(gap_data.median(), color=PALETTE["accent"], linestyle="--", linewidth=2,
                   label=f"Median: ₹{gap_data.median():,.0f}")
        ax.legend(fontsize=10)
        ax.set_title(f"{gap_label} Distribution", fontsize=13, fontweight="bold")
        ax.set_xlabel("INR Gap Amount")
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "negotiation_gap_distribution.png")

    # --- Chart 2: Gap by model ---
    if len(model_gap) > 1:
        fig, ax = plt.subplots(figsize=(12, 5))
        mg = model_gap.sort_values("Avg_Gap", ascending=True)
        ax.barh(mg["Model"].astype(str), mg["Avg_Gap"], color=PALETTE["primary"], edgecolor="white")
        for i, (gap, pct) in enumerate(zip(mg["Avg_Gap"], mg["Avg_Discount_Pct"])):
            ax.text(gap + 500, i, f"₹{gap:,.0f} ({pct:.1f}%)", va="center", fontsize=9)
        ax.set_title(f"Average {gap_label} by Model", fontsize=13, fontweight="bold")
        ax.set_xlabel("INR Gap Amount")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "pricing_gap_by_model.png")

    # --- Chart 3: Quoted vs Expected scatter ---
    scatter_df = valid[(valid["Quoted Price"] > 0) & (valid["Expected Price"] > 0)]
    if len(scatter_df) > 10:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(scatter_df["Quoted Price"] / 100000, scatter_df["Expected Price"] / 100000,
                   alpha=0.4, s=30, c=PALETTE["primary"], edgecolors="white", linewidth=0.5)
        lims = [0, max(scatter_df["Quoted Price"].max(), scatter_df["Expected Price"].max()) / 100000 * 1.05]
        ax.plot(lims, lims, "--", color="gray", alpha=0.5, label="Parity Line (No Gap)")
        ax.set_xlabel("Quoted Price (₹ Lakhs)", fontsize=11)
        ax.set_ylabel("Expected Price (₹ Lakhs)", fontsize=11)
        ax.set_title("Quoted vs Expected Price (Won Deals)", fontsize=13, fontweight="bold")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "pricing_scatter.png")

    # --- JSON export ---
    pricing_json = {
        "summary": df_to_json_records(summary),
        "gap_by_model": df_to_json_records(model_gap),
        "bucket_summary": df_to_json_records(bucket_perf),
        "data_quality": {
            "has_final_price": has_final_price,
            "gap_metric_used": gap_label,
            "note": note,
        },
    }
    save_json(pricing_json, "pricing_dashboard.json")
    return summary


# ---------------------------------------------------------------------------
# Module 6: Lost Lead Root-Cause Analysis
# ---------------------------------------------------------------------------


def pareto_chart(series, title, filename, annotate_80=True):
    """Create a Pareto chart with optional 80% threshold line."""
    counts = series.value_counts(dropna=True).reset_index()
    counts.columns = ["Category", "Count"]
    counts["Share_Pct"] = counts["Count"] / counts["Count"].sum() * 100
    counts["Cumulative_Pct"] = counts["Share_Pct"].cumsum()
    counts.to_csv(RESULTS_DIR / filename.replace(".png", ".csv"), index=False)

    display = counts.head(15)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    bars = ax1.bar(range(len(display)), display["Count"], color=PALETTE["primary"],
                   alpha=0.85, edgecolor="white")
    ax1.set_title(title, fontsize=14, fontweight="bold")
    ax1.set_xticks(range(len(display)))
    ax1.set_xticklabels(display["Category"], rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Count")

    ax2 = ax1.twinx()
    ax2.plot(range(len(display)), display["Cumulative_Pct"], color=PALETTE["secondary"],
             marker="o", linewidth=2, markersize=6)
    ax2.set_ylabel("Cumulative %", color=PALETTE["secondary"])
    ax2.set_ylim(0, 105)
    ax2.tick_params(axis="y", colors=PALETTE["secondary"])

    if annotate_80:
        ax2.axhline(y=80, color=PALETTE["warning"], linestyle="--", linewidth=1.5, alpha=0.8)
        ax2.text(len(display) - 1, 82, "80% threshold", fontsize=9,
                 color=PALETTE["warning"], ha="right")

    for bar, val in zip(bars, display["Count"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 str(int(val)), ha="center", fontsize=8)

    ax1.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, filename)
    return counts


def analyze_lost_root_cause(df):
    print("\n--- Module 6: Lost Lead Root-Cause Analysis ---")

    lost = df[df["Is_Lost"]].copy()
    lost_overview = pd.DataFrame({
        "Metric": ["Total Lost Leads", "With lost reason", "With lost due to",
                    "With Lost Remark", "With lost by"],
        "Value": [
            len(lost),
            lost["lost reason"].notna().sum(),
            lost["lost due to"].notna().sum(),
            lost.get("Lost Remark", pd.Series(dtype=object)).notna().sum(),
            lost.get("lost by", pd.Series(dtype=object)).notna().sum(),
        ],
    })
    lost_overview.to_csv(RESULTS_DIR / "lost_overview.csv", index=False)

    # Pareto charts with 80% annotation
    reason_pareto = pareto_chart(
        lost["lost reason"], "Pareto: Lost Reason (80/20)", "lost_reason_pareto.png",
    )
    due_to_pareto = pareto_chart(
        lost["lost due to"], "Pareto: Lost Due To (80/20)", "lost_due_to_pareto.png",
    )

    # Monthly lost-reason trend
    lost_monthly = (
        lost[lost["lost due to"].notna()]
        .groupby(["Enquiry Month", "lost due to"])
        .size()
        .reset_index(name="Count")
    )
    lost_monthly.to_csv(RESULTS_DIR / "lost_due_to_monthly_trend.csv", index=False)

    # --- Chart: Monthly stacked bar for lost reasons ---
    if len(lost_monthly) > 2:
        pivot = lost_monthly.pivot_table(
            index="Enquiry Month", columns="lost due to", values="Count", fill_value=0
        ).sort_index()
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab10", edgecolor="white")
        ax.set_title("Monthly Lost Lead Reasons (Stacked)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Lost Leads")
        ax.set_xlabel("Month")
        ax.legend(title="Lost Due To", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "lost_monthly_stacked.png")

    # Lost remark keyword extraction
    remarks = (
        lost.get("Lost Remark", pd.Series(dtype=object))
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )
    remark_summary = remarks.value_counts().head(25).reset_index()
    remark_summary.columns = ["Lost_Remark", "Count"]
    remark_summary.to_csv(RESULTS_DIR / "lost_remark_top25.csv", index=False)

    # Keyword frequency from free-text remarks
    stop_words = {"the", "a", "an", "is", "was", "not", "for", "to", "and", "of",
                  "in", "on", "at", "by", "or", "no", "nan", "none", ""}
    all_words = []
    for remark in remarks:
        tokens = re.findall(r"[a-z]+", remark)
        all_words.extend([t for t in tokens if t not in stop_words and len(t) > 2])
    keyword_freq = Counter(all_words).most_common(20)
    keyword_df = pd.DataFrame(keyword_freq, columns=["Keyword", "Frequency"])
    keyword_df.to_csv(RESULTS_DIR / "lost_remark_keywords.csv", index=False)

    # --- Chart: Keyword frequency ---
    if len(keyword_df) > 3:
        fig, ax = plt.subplots(figsize=(10, 5))
        kw = keyword_df.head(15)
        ax.barh(kw["Keyword"].iloc[::-1], kw["Frequency"].iloc[::-1],
                color=PALETTE["secondary"], alpha=0.85)
        ax.set_title("Lost Remark — Top Keywords", fontsize=13, fontweight="bold")
        ax.set_xlabel("Frequency")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "lost_remark_keywords.png")

    # Lost by breakdown (may be empty)
    lost_by = lost.get("lost by", pd.Series(dtype=object)).dropna()
    lost_by_data = []
    if len(lost_by) > 0:
        lost_by_summary = lost_by.value_counts().reset_index()
        lost_by_summary.columns = ["lost_by", "Count"]
        lost_by_summary.to_csv(RESULTS_DIR / "lost_by_breakdown.csv", index=False)
        lost_by_data = df_to_json_records(lost_by_summary)

    # --- JSON export ---
    lost_json = {
        "overview": df_to_json_records(lost_overview),
        "reason_pareto": df_to_json_records(reason_pareto.head(15)),
        "due_to_pareto": df_to_json_records(due_to_pareto.head(15)),
        "monthly_trend": df_to_json_records(lost_monthly) if len(lost_monthly) > 0 else [],
        "remark_keywords": df_to_json_records(keyword_df),
        "lost_by": lost_by_data,
        "data_quality": {
            "lost_by_populated": len(lost_by) > 0,
        },
    }
    save_json(lost_json, "lost_leads_dashboard.json")
    return reason_pareto


# ---------------------------------------------------------------------------
# Module 7: Campaign & Digital Sourcing
# ---------------------------------------------------------------------------


def analyze_campaign_digital(df):
    print("\n--- Module 7: Campaign & Digital Sourcing ---")

    # Campaign analysis (flagging low volume)
    campaign_col = df.get("Campaign No", pd.Series(dtype=object))
    campaign_count = campaign_col.notna().sum()

    campaign_perf = performance_table(df, ["Campaign No", "Campaign Name"], min_volume=0)
    campaign_perf = campaign_perf.sort_values(["Retails", "Enquiries"], ascending=[False, False])
    campaign_perf.to_csv(RESULTS_DIR / "campaign_performance.csv", index=False)

    campaign_warning = None
    if campaign_count < 30:
        campaign_warning = (
            f"WARNING: Only {campaign_count} leads have campaign tags. "
            "Campaign-level ROI analysis is statistically unreliable."
        )
        print(f"  [!] {campaign_warning}")

    # Online Request Type analysis (this has real volume: ~2300 leads)
    request_perf = performance_table(df, ["Online Request Type"], min_volume=5)
    request_perf.to_csv(RESULTS_DIR / "online_request_type_performance.csv", index=False)

    # Website remark analysis
    website_df = df[df.get("Website Remark", pd.Series(dtype=object)).notna()].copy()
    website_summary = (
        website_df.groupby("Website Remark")
        .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
    )
    website_summary["Retail_Rate"] = website_summary["Retails"] / website_summary["Enquiries"]
    website_summary = website_summary.sort_values("Enquiries", ascending=False)
    website_summary.to_csv(RESULTS_DIR / "website_remark_performance.csv", index=False)

    # Categorise website remarks (date-based vs text-based)
    website_df["Remark_Type"] = website_df["Website Remark"].apply(
        lambda x: "Date/Time Slot" if re.search(r"\d{2}/\d{2}/\d{4}", str(x)) else "Text Remark"
    )
    remark_type_summary = (
        website_df.groupby("Remark_Type")
        .agg(Count=("Is_Enquiry", "sum"))
        .reset_index()
    )
    remark_type_summary.to_csv(RESULTS_DIR / "website_remark_type.csv", index=False)

    # Source-level digital lead breakdown
    digital_sources = df[df["Source"].astype(str).str.contains("Website|Online|Digital|Internet", case=False, na=False)]
    digital_summary = (
        digital_sources.groupby(["Source", "Sub-source"], dropna=False)
        .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
        .reset_index()
        .sort_values("Enquiries", ascending=False)
    )
    digital_summary["Retail_Rate"] = digital_summary["Retails"] / digital_summary["Enquiries"]
    digital_summary.to_csv(RESULTS_DIR / "digital_source_breakdown.csv", index=False)

    # --- Chart 1: Online Request Type funnel ---
    if len(request_perf) > 1:
        req_sorted = request_perf.sort_values("Enquiries", ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(12, 6))
        x = range(len(req_sorted))
        w = 0.35
        ax.bar([i - w / 2 for i in x], req_sorted["Enquiries"],
               width=w, color=PALETTE["primary"], label="Enquiries", edgecolor="white")
        ax.bar([i + w / 2 for i in x], req_sorted["Retails"],
               width=w, color=PALETTE["accent"], label="Retails", edgecolor="white")
        ax.set_xticks(x)
        ax.set_xticklabels(req_sorted["Online Request Type"].astype(str), rotation=35, ha="right", fontsize=9)
        ax.set_title("Online Request Type — Volume & Conversion", fontsize=13, fontweight="bold")
        ax.set_ylabel("Count")
        ax.legend()

        # Overlay conversion rate
        ax2 = ax.twinx()
        ax2.plot(x, req_sorted["Retail_Rate"].values * 100, color=PALETTE["secondary"],
                 marker="D", linewidth=2, markersize=6, label="Retail Rate %")
        ax2.set_ylabel("Retail Rate (%)", color=PALETTE["secondary"])
        ax2.tick_params(axis="y", colors=PALETTE["secondary"])
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "online_request_type_volume.png")

    # --- Chart 2: Campaign scatter (if enough data) ---
    ranked_campaigns = campaign_perf[campaign_perf["Enquiries"] > 0]
    if len(ranked_campaigns) > 1:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=ranked_campaigns, x="Enquiries", y="Retail_Rate",
                        hue="Campaign Name", s=120, ax=ax)
        ax.set_title("Campaign Volume vs Conversion Rate", fontsize=13, fontweight="bold")
        if campaign_warning:
            ax.annotate(f"[!] n={campaign_count} (low volume)",
                        xy=(0.02, 0.95), xycoords="axes fraction", fontsize=9,
                        color="orange", style="italic")
        save_plot(fig, "campaign_volume_vs_conversion.png")

    # --- JSON export ---
    campaign_json = {
        "campaign_performance": df_to_json_records(campaign_perf),
        "online_request_type": df_to_json_records(request_perf),
        "website_remarks": df_to_json_records(website_summary.head(20)),
        "website_remark_types": df_to_json_records(remark_type_summary),
        "digital_source_breakdown": df_to_json_records(digital_summary.head(20)),
        "data_quality": {
            "campaign_tagged_leads": int(campaign_count),
            "campaign_warning": campaign_warning,
            "online_request_type_leads": int(request_perf["Enquiries"].sum()) if len(request_perf) > 0 else 0,
            "website_remark_leads": int(len(website_df)),
        },
    }
    save_json(campaign_json, "campaign_digital_dashboard.json")
    return campaign_perf


# ---------------------------------------------------------------------------
# Module 8: Lead Velocity & Engagement
# ---------------------------------------------------------------------------


def analyze_lead_velocity(df):
    print("\n--- Module 8: Lead Velocity & Engagement ---")

    # Check email count data availability
    email_total = df["Total Quotation Email Count"].fillna(0).sum()
    has_email_data = email_total > 10

    # Core velocity metrics by outcome
    velocity = (
        df.groupby("Outcome")
        .agg(
            Count=("Is_Enquiry", "sum"),
            Avg_Aging=("enquiry aging days", "mean"),
            Median_Aging=("enquiry aging days", "median"),
            P25_Aging=("enquiry aging days", lambda s: s.quantile(0.25)),
            P75_Aging=("enquiry aging days", lambda s: s.quantile(0.75)),
            P90_Aging=("enquiry aging days", lambda s: s.quantile(0.90)),
            Avg_Quotation_Emails=("Total Quotation Email Count", "mean"),
            Median_Quotation_Emails=("Total Quotation Email Count", "median"),
        )
        .reset_index()
    )
    velocity.to_csv(RESULTS_DIR / "lead_velocity_outcome.csv", index=False)

    # Aging bucket performance — optimal response window
    aging_bins = [0, 3, 7, 14, 21, 30, 45, 60, 200]
    aging_labels = ["0-3d", "4-7d", "8-14d", "15-21d", "22-30d", "31-45d", "46-60d", "61d+"]
    df_temp = df.copy()
    df_temp["Aging_Bucket"] = pd.cut(df_temp["enquiry aging days"], bins=aging_bins, labels=aging_labels)

    aging_perf = (
        df_temp.groupby("Aging_Bucket", observed=False)
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Retails=("Is_Retail", "sum"),
            Lost=("Is_Lost", "sum"),
        )
        .reset_index()
    )
    aging_perf["Retail_Rate"] = aging_perf["Retails"] / aging_perf["Enquiries"]
    aging_perf["Lost_Rate"] = aging_perf["Lost"] / aging_perf["Enquiries"]
    aging_perf.to_csv(RESULTS_DIR / "aging_bucket_conversion.csv", index=False)

    # Aging bucket × Outcome heatmap data
    aging_outcome = (
        df_temp.groupby(["Aging_Bucket", "Outcome"], observed=False)
        .size()
        .reset_index(name="Count")
    )
    aging_outcome.to_csv(RESULTS_DIR / "aging_outcome_crosstab.csv", index=False)

    # --- Chart 1: Won vs Lost aging distribution (KDE) ---
    won_lost = df[df["Outcome"].isin(["Retailed", "Lost"])].copy()
    if len(won_lost) > 20:
        fig, ax = plt.subplots(figsize=(10, 5))
        for outcome, color in [("Retailed", PALETTE["accent"]), ("Lost", PALETTE["secondary"])]:
            subset = won_lost[won_lost["Outcome"] == outcome]["enquiry aging days"].dropna()
            if len(subset) > 5:
                sns.kdeplot(subset, fill=True, alpha=0.3, color=color, label=outcome, ax=ax, bw_adjust=1.2)
                ax.axvline(subset.median(), color=color, linestyle="--", alpha=0.7)
                ax.text(subset.median() + 0.5, ax.get_ylim()[1] * 0.9,
                        f"Median: {subset.median():.0f}d", fontsize=9, color=color)
        ax.set_title("Enquiry Aging Distribution: Won vs Lost", fontsize=14, fontweight="bold")
        ax.set_xlabel("Enquiry Aging Days")
        ax.legend(fontsize=11)
        ax.set_xlim(0, min(won_lost["enquiry aging days"].quantile(0.98), 100))
        ax.grid(alpha=0.3)
        fig.tight_layout()
        save_plot(fig, "aging_won_vs_lost.png")

    # --- Chart 2: Aging bucket conversion rate ---
    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(aging_perf))
    ax.bar(x, aging_perf["Enquiries"], color=PALETTE["neutral"], alpha=0.5, label="Enquiries")
    ax2 = ax.twinx()
    ax2.plot(x, aging_perf["Retail_Rate"] * 100, color=PALETTE["accent"], marker="o",
             linewidth=2.5, markersize=8, label="Retail Rate %")
    ax2.plot(x, aging_perf["Lost_Rate"] * 100, color=PALETTE["secondary"], marker="s",
             linewidth=2.5, markersize=8, label="Lost Rate %")
    ax.set_xticks(x)
    ax.set_xticklabels(aging_perf["Aging_Bucket"].astype(str), rotation=30)
    ax.set_ylabel("Lead Volume", color="gray")
    ax2.set_ylabel("Rate (%)")
    ax.set_title("Optimal Response Window — Conversion by Aging Bucket", fontsize=13, fontweight="bold")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    save_plot(fig, "aging_bucket_conversion.png")

    # --- Chart 3: Aging × Outcome heatmap ---
    heatmap_pivot = aging_outcome.pivot_table(
        index="Aging_Bucket", columns="Outcome", values="Count", fill_value=0
    )
    heatmap_pivot = heatmap_pivot.astype(int)
    if heatmap_pivot.shape[0] > 1 and heatmap_pivot.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(heatmap_pivot, annot=True, fmt="d", cmap="YlOrRd", ax=ax, linewidths=0.5)
        ax.set_title("Aging Bucket × Outcome Heatmap", fontsize=13, fontweight="bold")
        fig.tight_layout()
        save_plot(fig, "aging_outcome_heatmap.png")

    # Email count analysis (conditional on data availability)
    email_perf_records = []
    if has_email_data:
        email_bucket = pd.cut(
            df["Total Quotation Email Count"].fillna(0),
            bins=[-0.1, 0, 1, 2, 5, 100],
            labels=["0", "1", "2", "3-5", "6+"],
        )
        email_perf = (
            df.assign(Email_Bucket=email_bucket)
            .groupby("Email_Bucket", observed=False)
            .agg(Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum"))
            .reset_index()
        )
        email_perf["Retail_Rate"] = email_perf["Retails"] / email_perf["Enquiries"]
        email_perf.to_csv(RESULTS_DIR / "quotation_email_conversion.csv", index=False)
        email_perf_records = df_to_json_records(email_perf)

        corr = df[["Total Quotation Email Count", "Is_Retail", "Is_Booking"]].corr(numeric_only=True)
        corr.to_csv(RESULTS_DIR / "quotation_email_correlation.csv")
    else:
        print("  [!] Email count data is near-empty. Skipping email engagement analysis.")

    # Find optimal window (bucket with highest retail rate, min 50 leads)
    optimal = aging_perf[aging_perf["Enquiries"] >= 50].sort_values("Retail_Rate", ascending=False)
    optimal_window = optimal.iloc[0]["Aging_Bucket"] if len(optimal) > 0 else "N/A"

    # --- JSON export ---
    velocity_json = {
        "velocity_by_outcome": df_to_json_records(velocity),
        "aging_bucket_performance": df_to_json_records(aging_perf),
        "aging_outcome_crosstab": df_to_json_records(aging_outcome),
        "email_engagement": email_perf_records,
        "optimal_response_window": str(optimal_window),
        "data_quality": {
            "has_email_data": has_email_data,
            "total_email_count_sum": float(email_total),
            "aging_days_coverage_pct": round(df["enquiry aging days"].notna().mean() * 100, 1),
        },
    }
    save_json(velocity_json, "lead_velocity_dashboard.json")
    return velocity


# ---------------------------------------------------------------------------
# Legacy / Core Funnel Analyses
# ---------------------------------------------------------------------------


def run_legacy_analyses(df):
    print("\n--- Running Core Funnel Analysis ---")
    enq_count = len(df)
    td_count = df["Is_TD"].sum()
    booking_count = df["Is_Booking"].sum()
    retail_count = df["Is_Retail"].sum()

    funnel_summary = pd.DataFrame({
        "Stage": ["Enquiry", "Test Drive", "Booking", "Retail"],
        "Count": [enq_count, td_count, booking_count, retail_count],
        "Conversion_of_Enquiry": [
            1.0,
            safe_rate(td_count, enq_count),
            safe_rate(booking_count, enq_count),
            safe_rate(retail_count, enq_count),
        ],
        "Stage_to_Stage_Conversion": [
            1.0,
            safe_rate(td_count, enq_count),
            safe_rate(booking_count, td_count),
            safe_rate(retail_count, booking_count),
        ],
        "Drop_off_Rate": [
            0.0,
            1 - safe_rate(td_count, enq_count),
            1 - safe_rate(booking_count, td_count),
            1 - safe_rate(retail_count, booking_count),
        ],
    })
    funnel_summary.to_csv(RESULTS_DIR / "funnel_summary.csv", index=False)
    print(funnel_summary.to_string(index=False))

    source_perf = performance_table(df, ["Source"])
    source_perf.to_csv(RESULTS_DIR / "source_performance.csv", index=False)

    subsource_perf = performance_table(df, ["Source", "Sub-source"])
    subsource_perf.to_csv(RESULTS_DIR / "subsource_performance.csv", index=False)

    type_perf = performance_table(df, ["Type"])
    type_perf.to_csv(RESULTS_DIR / "lead_type_performance.csv", index=False)

    lost_reason = df["lost reason"].value_counts(dropna=False).reset_index()
    lost_reason.to_csv(RESULTS_DIR / "lost_reason_breakdown.csv", index=False)

    lost_due_to = df["lost due to"].value_counts(dropna=False).reset_index()
    lost_due_to.to_csv(RESULTS_DIR / "lost_due_to_breakdown.csv", index=False)

    lost_trend = (
        df[df["lost due to"].notnull()]
        .groupby(["Enquiry Month", "lost due to"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    lost_trend.to_csv(RESULTS_DIR / "lost_due_to_monthly_trend.csv", index=False)

    outcome_metrics = (
        df.groupby("Outcome")
        .agg(
            Count=("Is_Enquiry", "sum"),
            Avg_Aging=("enquiry aging days", "mean"),
            Median_Aging=("enquiry aging days", "median"),
            Avg_Followups=("Followup Count", "mean"),
            Median_Followups=("Followup Count", "median"),
        )
        .reset_index()
    )
    outcome_metrics.to_csv(RESULTS_DIR / "aging_followup_outcome.csv", index=False)

    df["Followup_Bucket"] = pd.cut(
        df["Followup Count"],
        bins=[-1, 0, 1, 2, 4, 6, 10, 100],
        labels=["0", "1", "2", "3-4", "5-6", "7-10", "11+"],
    )
    followup_perf = (
        df.groupby("Followup_Bucket", observed=False)
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Bookings=("Is_Booking", "sum"),
            Retails=("Is_Retail", "sum"),
        )
        .reset_index()
    )
    followup_perf["Booking_Rate"] = followup_perf["Bookings"] / followup_perf["Enquiries"]
    followup_perf["Retail_Rate"] = followup_perf["Retails"] / followup_perf["Enquiries"]
    followup_perf.to_csv(RESULTS_DIR / "followup_bucket_performance.csv", index=False)

    df["Aging_Bucket"] = pd.cut(
        df["enquiry aging days"],
        bins=[0, 7, 15, 30, 45, 60, 100],
        labels=["0-7 days", "8-15 days", "16-30 days", "31-45 days", "46-60 days", "61+ days"],
    )
    aging_perf = (
        df.groupby("Aging_Bucket", observed=False)
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Bookings=("Is_Booking", "sum"),
            Retails=("Is_Retail", "sum"),
        )
        .reset_index()
    )
    aging_perf["Booking_Rate"] = aging_perf["Bookings"] / aging_perf["Enquiries"]
    aging_perf["Retail_Rate"] = aging_perf["Retails"] / aging_perf["Enquiries"]
    aging_perf.to_csv(RESULTS_DIR / "aging_bucket_performance.csv", index=False)

    model_perf = performance_table(df, ["Model"])
    model_perf.to_csv(RESULTS_DIR / "model_performance.csv", index=False)

    variant_perf = performance_table(df, ["Model", "Variant"])
    variant_perf.to_csv(RESULTS_DIR / "variant_performance.csv", index=False)

    consultant_df = df.copy()
    consultant_df["Consultant Name"] = (
        consultant_df["Consultant Name"].astype(str).str.strip().str.upper()
    )
    consultant_df["Consultant Name"] = consultant_df["Consultant Name"].replace(
        {"NAN": np.nan, "NONE": np.nan}
    )
    consultant_perf = performance_table(consultant_df, ["Consultant Name"])
    consultant_perf.to_csv(RESULTS_DIR / "consultant_performance.csv", index=False)

    td_impact = (
        df.groupby("Is_TD")
        .agg(
            Enquiries=("Is_Enquiry", "sum"),
            Bookings=("Is_Booking", "sum"),
            Retails=("Is_Retail", "sum"),
        )
        .reset_index()
    )
    td_impact["Booking_Rate"] = td_impact["Bookings"] / td_impact["Enquiries"]
    td_impact["Retail_Rate"] = td_impact["Retails"] / td_impact["Enquiries"]
    td_impact.to_csv(RESULTS_DIR / "td_impact.csv", index=False)

    monthly_trends = performance_table(df, ["Enquiry Month"])
    monthly_trends.to_csv(RESULTS_DIR / "monthly_trends.csv", index=False)

    source_mix = df.groupby(["Enquiry Month", "Source"]).size().unstack(fill_value=0)
    source_mix_pct = source_mix.div(source_mix.sum(axis=1), axis=0) * 100
    source_mix_pct.to_csv(RESULTS_DIR / "source_mix_trend_pct.csv")


# ---------------------------------------------------------------------------
# Executive Summary Generator
# ---------------------------------------------------------------------------


def generate_executive_summary(df):
    """Create a single-page KPI summary JSON for the dashboard."""
    print("\n--- Generating Executive Summary ---")

    total = len(df)
    retails = df["Is_Retail"].sum()
    bookings = df["Is_Booking"].sum()
    test_drives = df["Is_TD"].sum()
    lost = df["Is_Lost"].sum()

    avg_cycle_won = df[df["Is_Retail"]]["Sales_Cycle_Days"].mean()
    median_cycle_won = df[df["Is_Retail"]]["Sales_Cycle_Days"].median()

    # Top model
    model_counts = df.groupby("Model").agg(
        Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum")
    ).reset_index()
    model_counts["Retail_Rate"] = model_counts["Retails"] / model_counts["Enquiries"]
    top_model_volume = model_counts.sort_values("Enquiries", ascending=False).iloc[0]
    top_model_conversion = model_counts[model_counts["Enquiries"] >= 50].sort_values("Retail_Rate", ascending=False).iloc[0]

    # Top source
    source_counts = df.groupby("Source").agg(
        Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum")
    ).reset_index()
    source_counts["Retail_Rate"] = source_counts["Retails"] / source_counts["Enquiries"]
    top_source = source_counts.sort_values("Enquiries", ascending=False).iloc[0]

    # Top city
    city_counts = df.groupby("City").agg(
        Enquiries=("Is_Enquiry", "sum"), Retails=("Is_Retail", "sum")
    ).reset_index()
    city_counts["Retail_Rate"] = city_counts["Retails"] / city_counts["Enquiries"]
    top_city = city_counts.sort_values("Enquiries", ascending=False).iloc[0]

    # Date range
    min_date = df["Enquiry Date"].min()
    max_date = df["Enquiry Date"].max()

    summary = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "date_range": {
            "start": min_date.strftime("%Y-%m-%d") if pd.notna(min_date) else "N/A",
            "end": max_date.strftime("%Y-%m-%d") if pd.notna(max_date) else "N/A",
        },
        "kpi": {
            "total_enquiries": int(total),
            "total_retails": int(retails),
            "total_bookings": int(bookings),
            "total_test_drives": int(test_drives),
            "total_lost": int(lost),
            "overall_retail_rate": round(safe_rate(retails, total), 4),
            "overall_booking_rate": round(safe_rate(bookings, total), 4),
            "overall_td_rate": round(safe_rate(test_drives, total), 4),
            "avg_sales_cycle_days_won": round(float(avg_cycle_won), 1) if pd.notna(avg_cycle_won) else None,
            "median_sales_cycle_days_won": round(float(median_cycle_won), 1) if pd.notna(median_cycle_won) else None,
        },
        "highlights": {
            "top_model_by_volume": {
                "model": str(top_model_volume["Model"]),
                "enquiries": int(top_model_volume["Enquiries"]),
                "retails": int(top_model_volume["Retails"]),
            },
            "top_model_by_conversion": {
                "model": str(top_model_conversion["Model"]),
                "retail_rate": round(float(top_model_conversion["Retail_Rate"]), 4),
                "enquiries": int(top_model_conversion["Enquiries"]),
            },
            "top_source": {
                "source": str(top_source["Source"]),
                "enquiries": int(top_source["Enquiries"]),
                "retail_rate": round(float(top_source["Retail_Rate"]), 4),
            },
            "top_city": {
                "city": str(top_city["City"]),
                "enquiries": int(top_city["Enquiries"]),
                "retail_rate": round(float(top_city["Retail_Rate"]), 4),
            },
        },
        "customer_split": {
            seg: {
                "count": int(cnt),
                "pct": round(cnt / total * 100, 1),
            }
            for seg, cnt in df["Customer Type"].value_counts().items()
        },
        "fuel_split": {
            fuel: {
                "count": int(cnt),
                "pct": round(cnt / total * 100, 1),
            }
            for fuel, cnt in df["Fuel type"].value_counts().items()
        },
    }

    save_json(summary, "executive_summary.json")
    return summary


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------


def run_analysis():
    sns.set_theme(style="whitegrid")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    if "Enquiry Month" not in df.columns and "Enquiry Date" in df.columns:
        df["Enquiry Date"] = pd.to_datetime(df["Enquiry Date"], errors="coerce")
        df["Enquiry Month"] = df["Enquiry Date"].dt.strftime("%Y-%m")

    df = prepare_funnel_flags(df)

    run_legacy_analyses(df)
    analyze_geographic(df)
    analyze_product_variant(df)
    analyze_customer_segmentation(df)
    analyze_exchange_funnel(df)
    analyze_pricing_negotiation(df)
    analyze_lost_root_cause(df)
    analyze_campaign_digital(df)
    analyze_lead_velocity(df)
    generate_executive_summary(df)

    print("\n" + "=" * 60)
    print("--- Analysis complete ---")
    print(f"CSV outputs  : {RESULTS_DIR}")
    print(f"Plot outputs : {PLOTS_DIR}")
    print(f"JSON outputs : {JSON_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_analysis()
