import os
import pandas as pd
import numpy as np

def generate_report():
    # Load analysis CSVs
    funnel = pd.read_csv('d:/KIA/data/analysis_results/funnel_summary.csv')
    source = pd.read_csv('d:/KIA/data/analysis_results/source_performance.csv')
    lead_type = pd.read_csv('d:/KIA/data/analysis_results/lead_type_performance.csv')
    lost_due = pd.read_csv('d:/KIA/data/analysis_results/lost_due_to_breakdown.csv')
    aging_followup = pd.read_csv('d:/KIA/data/analysis_results/aging_followup_outcome.csv')
    followup_buckets = pd.read_csv('d:/KIA/data/analysis_results/followup_bucket_performance.csv')
    aging_buckets = pd.read_csv('d:/KIA/data/analysis_results/aging_bucket_performance.csv')
    models = pd.read_csv('d:/KIA/data/analysis_results/model_performance.csv')
    consultants = pd.read_csv('d:/KIA/data/analysis_results/consultant_performance.csv')
    td_impact = pd.read_csv('d:/KIA/data/analysis_results/td_impact.csv')
    monthly = pd.read_csv('d:/KIA/data/analysis_results/monthly_trends.csv')
    source_mix = pd.read_csv('d:/KIA/data/analysis_results/source_mix_trend_pct.csv')

    # Convert to markdown tables
    funnel_md = funnel.to_markdown(index=False)
    source_md = source.to_markdown(index=False)
    lead_type_md = lead_type.to_markdown(index=False)
    lost_due_md = lost_due.head(10).to_markdown(index=False)
    aging_followup_md = aging_followup.to_markdown(index=False)
    followup_buckets_md = followup_buckets.to_markdown(index=False)
    aging_buckets_md = aging_buckets.to_markdown(index=False)
    models_md = models.to_markdown(index=False)
    consultants_md = consultants.head(10).to_markdown(index=False)
    td_impact_md = td_impact.to_markdown(index=False)
    monthly_md = monthly.to_markdown(index=False)
    source_mix_md = source_mix.to_markdown(index=False)

    report_content = f"""# Lead Conversion Intelligence - Analysis Report
Bhubaneswar Kia Dealership (Jan-Jun 2026)

This report outlines the detailed funnel, vehicle model, consultant, and monthly trend analysis of the 6,967 leads processed from the dealership CRM.

---

## 1. Funnel & Conversion Performance
The conversion funnel tracks customer progression from the initial CRM enquiry through the Test Drive, Booking, and final Retail Delivery stages.

{funnel_md}

**Key Funnel Takeaways**:
- **Overall Conversion**: **11.28%** of enquiries convert to a retail delivery.
- **Top Drop-off Point**: **53.37%** of leads drop off between Enquiry and Test Drive. Getting customers into a test drive is the single largest hurdle.
- **Stage-to-Stage**: Once a Test Drive is completed, **51.46%** book a vehicle. Of those who book, **47.01%** reach retail delivery.

---

## 2. Lead Source & Sub-Source Performance
Analysis of where leads originate and how they convert.

{source_md}

**Key Source Takeaways**:
- **Referral** is the highest-performing channel, converting **27.62%** of leads to retail. It has a high booking-to-retail conversion of **52.24%**.
- **Walk-in** and **Field** activities are solid channels, converting **13.46%** and **12.96%** respectively.
- **Hyperlocal** campaigns generate the highest lead volume (**2,232 leads**, 32.0% of total) but perform the worst, converting only **3.45%** to retail. This indicates low-quality lead generation that wastes consultant effort.

---

## 3. Lead Score (Type) Validation
Validation of the CRM's default lead scoring (Hot, Warm, Cold).

{lead_type_md}

**Key Scoring Takeaways**:
- **Hot Leads** are highly predictive, converting at a massive **45.76%** retail rate.
- **Warm Leads** (**0.09%**) and **Cold Leads** (**0.19%**) have virtually zero retail conversion.
- *Anomaly*: Warm leads convert at a lower rate than Cold leads. This suggests that the "Warm" criteria in the CRM are not predictive and need adjustment.

---

## 4. Lost Deal Analysis
Breakdown of lost leads and why they were cancelled.

{lost_due_md}

**Key Lost Takeaways**:
- **Plan Postponed** (**36.4%** of lost reasons) and **Change Request** (**23.3%**) represent almost 60% of cancellations. This indicates that timing and change of mind are the primary obstacles rather than product dislike.
- **Lost to co-dealer** (**7.5%**) indicates leakage to other Kia dealerships in the region.

---

## 5. Enquiry Aging and Follow-up Impact

### Outcome Comparison
{aging_followup_md}

### Conversion by Follow-up Count
{followup_buckets_md}

### Conversion by Enquiry Aging Days
{aging_buckets_md}

**Key Takeaways**:
- **Follow-up Sweet Spot**: Lead conversion peaks sharply at **2 to 4 follow-ups** (17-19% conversion). 
- **Diminishing Returns**: If a lead does not book by the 4th follow-up, further follow-ups are highly ineffective (dropping to ~1.6% at 5-6 and < 1% at 7+).
- **Early Abandonment**: Leads with 0 or 1 follow-ups convert at < 0.3%, suggesting a large pool of leads is abandoned prematurely.
- **Aging is not a Deal Killer**: Retailed leads have an average aging of **26.25 days**, and conversion rate actually increases with aging (up to 17.14% for 61+ days). This indicates that the buying process takes time, and mature leads should not be discarded.

---

## 6. Vehicle Model Demand and Conversion
Ranking models by volume and conversion rates.

{models_md}

**Key Model Takeaways**:
- **Kia Sonet** is the star model: it has high volume (2,115 leads) and the highest conversion rate (**16.26%**), delivering 344 cars.
- **New Seltos** has the highest volume (2,155 leads) but a lower conversion rate of **8.68%**.
- **Kia Carens** is very strong, converting **14.71%** of its 1,326 leads.
- **Crossover/EV models** (Carnival, EV6, EV9) have negligible volume and zero retail deliveries in this dataset.

---

## 7. Test Drive Impact
Comparing booking and retail rates for customers who did a Test Drive vs. those who did not.

{td_impact_md}

**Key Test Drive Takeaways**:
- Customers who complete a Test Drive are **4.3 times more likely to buy** (19.11% vs. 4.44% retail rate) and **5.1 times more likely to book** (42.04% vs. 8.23%).
- Completed Test Drives drive over 78.9% of all retail deliveries (621 out of 786).

---

## 8. Monthly Volume and Source Mix Trends

### Monthly Summary
{monthly_md}

### Source Mix Shift Trend (%)
{source_mix_md}

**Key Trend Takeaways**:
- Enquiry volume peaks in Jan/Feb and April, dropping to a low of 952 in June.
- Retail conversion rates peaked in January (**14.34%**) and have generally trended downward, hitting a low of **7.25%** in June.
- **Field** leads increased from 6.65% in January to 17.88% in June, showing an expansion in outdoor sourcing.
- **Online/CRM** leads halved from 11.67% in January to 5.68% in June.
"""
    
    os.makedirs('d:/KIA/docs', exist_ok=True)
    with open('d:/KIA/docs/analysis_report.md', 'w') as f:
        f.write(report_content)
    print("Saved Analysis Report to d:/KIA/docs/analysis_report.md")

if __name__ == '__main__':
    generate_report()
