import os
import pandas as pd


def load_optional_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def to_md(df, max_rows=None):
    if df is None or df.empty:
        return "_No data available._"
    view = df.head(max_rows) if max_rows else df
    return view.to_markdown(index=False)


def generate_report():
    results = "d:/KIA/data/analysis_results"

    funnel = pd.read_csv(f"{results}/funnel_summary.csv")
    source = pd.read_csv(f"{results}/source_performance.csv")
    lead_type = pd.read_csv(f"{results}/lead_type_performance.csv")
    lost_due = pd.read_csv(f"{results}/lost_due_to_breakdown.csv")
    aging_followup = pd.read_csv(f"{results}/aging_followup_outcome.csv")
    followup_buckets = pd.read_csv(f"{results}/followup_bucket_performance.csv")
    aging_buckets = pd.read_csv(f"{results}/aging_bucket_performance.csv")
    models = pd.read_csv(f"{results}/model_performance.csv")
    consultants = pd.read_csv(f"{results}/consultant_performance.csv")
    td_impact = pd.read_csv(f"{results}/td_impact.csv")
    monthly = pd.read_csv(f"{results}/monthly_trends.csv")
    source_mix = pd.read_csv(f"{results}/source_mix_trend_pct.csv")

    geo_top5 = load_optional_csv(f"{results}/geographic_top5_cities.csv")
    geo_bottom5 = load_optional_csv(f"{results}/geographic_bottom5_cities.csv")
    fuel_type = load_optional_csv(f"{results}/fuel_type_performance.csv")
    color_pref = load_optional_csv(f"{results}/color_preference.csv")
    customer_segment = load_optional_csv(f"{results}/customer_segment_performance.csv")
    customer_cycle = load_optional_csv(f"{results}/customer_sales_cycle.csv")
    exchange_impact = load_optional_csv(f"{results}/exchange_conversion_impact.csv")
    pricing_summary = load_optional_csv(f"{results}/pricing_negotiation_summary.csv")
    lost_reason_pareto = load_optional_csv(f"{results}/lost_reason_pareto.csv")
    campaign_perf = load_optional_csv(f"{results}/campaign_performance.csv")
    request_perf = load_optional_csv(f"{results}/online_request_type_performance.csv")
    lead_velocity = load_optional_csv(f"{results}/lead_velocity_outcome.csv")
    email_perf = load_optional_csv(f"{results}/quotation_email_conversion.csv")

    report_content = f"""# Lead Conversion Intelligence - Analysis Report
Bhubaneswar Kia Dealership (Jan-Jun 2026)

This report outlines the detailed funnel, vehicle model, consultant, and monthly trend analysis of the 6,967 leads processed from the dealership CRM, including the eight expanded proposal modules.

---

## 1. Funnel & Conversion Performance

{to_md(funnel)}

---

## 2. Lead Source & Sub-Source Performance

{to_md(source)}

---

## 3. Lead Score (Type) Validation

{to_md(lead_type)}

---

## 4. Lost Deal Analysis

{to_md(lost_due, 10)}

---

## 5. Enquiry Aging and Follow-up Impact

### Outcome Comparison
{to_md(aging_followup)}

### Conversion by Follow-up Count
{to_md(followup_buckets)}

### Conversion by Enquiry Aging Days
{to_md(aging_buckets)}

---

## 6. Vehicle Model Demand and Conversion

{to_md(models)}

---

## 7. Test Drive Impact

{to_md(td_impact)}

---

## 8. Monthly Volume and Source Mix Trends

### Monthly Summary
{to_md(monthly)}

### Source Mix Shift Trend (%)
{to_md(source_mix)}

---

## 9. Geographic & Regional Conversion

### Top 5 Performing Cities
{to_md(geo_top5)}

### Bottom 5 Performing Cities
{to_md(geo_bottom5)}

Plots: `data/analysis_results/plots/geographic_lead_volume.png`, `geographic_conversion_heatmap.png`

---

## 10. Product & Variant Demand

### Fuel Type Performance
{to_md(fuel_type)}

### Color Preferences
{to_md(color_pref, 10)}

Plot: `data/analysis_results/plots/fuel_type_volume_conversion.png`

---

## 11. Customer Segmentation

### Individual vs Corporate
{to_md(customer_segment)}

### Sales Cycle by Segment
{to_md(customer_cycle)}

---

## 12. Trade-In / Exchange Funnel

### Exchange Interest Impact on Conversion
{to_md(exchange_impact)}

Plot: `data/analysis_results/plots/exchange_funnel.png`

---

## 13. Pricing & Negotiation Gap

{to_md(pricing_summary)}

---

## 14. Lost Lead Root-Cause (Pareto)

### Lost Reason Pareto
{to_md(lost_reason_pareto, 10)}

Plots: `lost_reason_pareto.png`, `lost_due_to_pareto.png`

---

## 15. Campaign & Digital Sourcing

### Campaign Performance
{to_md(campaign_perf)}

### Online Request Type Breakdown
{to_md(request_perf, 10)}

---

## 16. Lead Velocity & Engagement

### Aging & Quotation Email Metrics by Outcome
{to_md(lead_velocity)}

### Conversion by Quotation Email Count
{to_md(email_perf)}

Plot: `data/analysis_results/plots/aging_won_vs_lost.png`
"""

    os.makedirs("d:/KIA/docs", exist_ok=True)
    with open("d:/KIA/docs/analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Saved Analysis Report to d:/KIA/docs/analysis_report.md")


if __name__ == "__main__":
    generate_report()
