# Kia Dealership Lead Conversion Intelligence Project

This repository hosts the **Lead Conversion Intelligence Project** for a Kia automobile dealership in Bhubaneswar, Odisha. Using a real CRM dataset of **6,967 leads** across 6 monthly sheets (January – June 2026), this project merges, cleans, and anonymizes the data, evaluates funnel drop-offs, ranks model demand, analyzes consultant leaderboards, and proposes a data-driven BI dashboard and management presentation.

---

## 1. Repository Structure

```
├── data/
│   ├── master_clean.csv             # Cleaned, merged, and anonymized master lead dataset
│   └── analysis_results/            # CSV tables of structured analysis metrics
├── notebooks/
│   └── analysis.ipynb               # Jupyter Notebook with exploratory data analysis & plotting
├── dashboard/
│   ├── README.md                    # BI dashboard layout specifications & visual mockup
│   ├── dax_measures.md              # Calculated columns & DAX measures for Power BI / Looker
│   └── kia_dashboard_mockup.png     # Visual executive dashboard UI mockup
├── docs/
│   ├── data_quality_notes.md        # Detailed document on data merging and validation
│   ├── analysis_report.md           # Full markdown text analysis report with tables
│   └── management_presentation.md   # Executive slide deck (Marp format) for dealership management
├── src/
│   ├── clean_data.py                # Automated Python script to merge, clean, and anonymize data
│   ├── run_analysis.py              # Automated Python script to calculate conversion metrics
│   └── generate_report.py           # Script to compile analysis results into the final report
├── README.md                        # Master repository documentation
└── .gitignore                       # Git ignore file containing raw data rules
```

---

## 2. Analytical Insights Summary

### Core Conversion KPIs
- **Total Enquiries Sourced**: `6,967` leads
- **Completed Test Drive Rate**: `46.6%` (Completed TDs / Enquiries)
- **Booking Rate**: `24.0%` (Bookings / Enquiries)
- **Overall Conversion (Retail)**: `11.3%` (Retail deliveries / Enquiries)

### Top Strategic Findings
1. **The Test Drive Catalyst**: Customers completing a Test Drive are **4.3 times more likely to buy** (19.11% vs. 4.44% retail rate) and **5.1 times more likely to book** (42.04% vs. 8.23%). Test drives drive 79% of all sales.
2. **Sourcing Spend Inefficiency**: The highest volume source (*Hyperlocal*, generating 32.0% of leads) converts at an abysmal **3.45%**. The lowest volume source (*Referrals*, 15.7% of leads) converts at an outstanding **27.62%**.
3. **Follow-up Sweet Spot**: Focus on exactly **2 to 4 follow-ups**. Conversion peaks at **19.06%** for 2 follow-ups and drops to **1.64%** at 5-6. Following up more than 4 times yields near-zero returns and wastes sales capacity.
4. **CRM Scoring Disconnect**: "Hot" leads are highly accurate (45.76% conversion), but "Warm" leads convert at **0.09%**, which is actually *worse* than "Cold" leads (**0.19%**).

---

## 3. How to Run the Pipeline

### Prerequisites
Make sure Python 3.x is installed along with the required libraries:
```bash
pip install pandas numpy openpyxl tabulate matplotlib seaborn
```

### Steps:
1. **Copy Source File**: Place the raw source excel file `enq (1).xlsx` in the root workspace folder as `raw_enq.xlsx`.
2. **Execute Data Cleaning**:
   ```bash
   python clean_data.py
   ```
   *This outputs `/data/master_clean.csv` and `/docs/data_quality_notes.md`.*
3. **Execute Analytics Calculations**:
   ```bash
   python run_analysis.py
   ```
   *This calculates all funnel, vehicle model, consultant, and trend metrics, saving them as CSV tables in `/data/analysis_results/`.*
4. **Generate Markdown Report**:
   ```bash
   python generate_report.py
   ```
   *This compiles the CSV metrics into the comprehensive text report at `/docs/analysis_report.md`.*

---

## 4. Visual Dashboard Mockup
A design spec for the dashboard layout is included in the [dashboard/](dashboard/) folder. You can reference the layout, DAX formulas, and review the visual interface mockups directly.
- **DAX Measures Configuration**: [dashboard/dax_measures.md](dashboard/dax_measures.md)
- **UI Mockup**: [dashboard/kia_dashboard_mockup.png](dashboard/kia_dashboard_mockup.png)
