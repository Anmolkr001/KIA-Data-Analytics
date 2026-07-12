import os
import pandas as pd
import numpy as np

def run_analysis():
    df = pd.read_csv('d:/KIA/data/master_clean.csv')
    
    # Standardize columns to datetimes where needed
    date_cols = ['Enquiry Date', 'Test Drive Date', 'Booking Date', 'Retail date', 'Lost Date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    print("--- Loaded Clean Data ---")
    print(f"Total Rows: {len(df)}")
    
    # Create analysis directory
    os.makedirs('d:/KIA/data/analysis_results', exist_ok=True)
    
    # ------------------ STEP 2: FUNNEL & CONVERSION ANALYSIS ------------------
    print("\n--- Running Funnel Analysis ---")
    # Funnel flags
    df['Is_Enquiry'] = True
    df['Is_TD'] = df['Test Drive Date'].notnull() | (df['TD Status'] == 'Done') | (df['No. of test drive given'] > 0)
    df['Is_Booking'] = df['Booking Date'].notnull()
    df['Is_Retail'] = df['Retail date'].notnull() | (df['Enquiry Status'] == 'Retail')
    
    enq_count = len(df)
    td_count = df['Is_TD'].sum()
    booking_count = df['Is_Booking'].sum()
    retail_count = df['Is_Retail'].sum()
    
    funnel_summary = pd.DataFrame({
        'Stage': ['Enquiry', 'Test Drive', 'Booking', 'Retail'],
        'Count': [enq_count, td_count, booking_count, retail_count],
        'Conversion_of_Enquiry': [1.0, td_count/enq_count, booking_count/enq_count, retail_count/enq_count],
        'Stage_to_Stage_Conversion': [1.0, td_count/enq_count, booking_count/td_count if td_count > 0 else 0, retail_count/booking_count if booking_count > 0 else 0],
        'Drop_off_Rate': [0.0, 1 - (td_count/enq_count), 1 - (booking_count/td_count) if td_count > 0 else 0, 1 - (retail_count/booking_count) if booking_count > 0 else 0]
    })
    funnel_summary.to_csv('d:/KIA/data/analysis_results/funnel_summary.csv', index=False)
    print(funnel_summary.to_string(index=False))
    
    # Conversion rate by Source and Sub-source
    print("\n--- Running Source & Sub-source Conversion ---")
    source_perf = df.groupby('Source').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    source_perf['TD_Rate'] = source_perf['Test_Drives'] / source_perf['Enquiries']
    source_perf['Booking_Rate'] = source_perf['Bookings'] / source_perf['Enquiries']
    source_perf['Retail_Rate'] = source_perf['Retails'] / source_perf['Enquiries']
    source_perf['Booking_to_Retail'] = source_perf['Retails'] / source_perf['Bookings'].replace(0, np.nan)
    source_perf = source_perf.sort_values(by='Retails', ascending=False)
    source_perf.to_csv('d:/KIA/data/analysis_results/source_performance.csv', index=False)
    print(source_perf.to_string(index=False))
    
    subsource_perf = df.groupby(['Source', 'Sub-source']).agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    subsource_perf['Booking_Rate'] = subsource_perf['Bookings'] / subsource_perf['Enquiries']
    subsource_perf['Retail_Rate'] = subsource_perf['Retails'] / subsource_perf['Enquiries']
    subsource_perf = subsource_perf.sort_values(by='Retails', ascending=False)
    subsource_perf.to_csv('d:/KIA/data/analysis_results/subsource_performance.csv', index=False)
    
    # Conversion rate by Lead Type (Hot/Warm/Cold)
    print("\n--- Running Lead Type (Hot/Warm/Cold) Validation ---")
    type_perf = df.groupby('Type').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    type_perf['Booking_Rate'] = type_perf['Bookings'] / type_perf['Enquiries']
    type_perf['Retail_Rate'] = type_perf['Retails'] / type_perf['Enquiries']
    type_perf = type_perf.sort_values(by='Retail_Rate', ascending=False)
    type_perf.to_csv('d:/KIA/data/analysis_results/lead_type_performance.csv', index=False)
    print(type_perf.to_string(index=False))
    
    # Lost Analysis
    print("\n--- Running Lost Analysis ---")
    lost_df = df[df['lost reason'].notnull() | df['lost due to'].notnull() | (df['Enquiry Status'].str.contains('Cancel', na=False))]
    print(f"Total Lost Leads identified: {len(lost_df)}")
    
    # Lost reason count
    lost_reason = df['lost reason'].value_counts(dropna=False).reset_index()
    lost_reason.to_csv('d:/KIA/data/analysis_results/lost_reason_breakdown.csv', index=False)
    
    # Lost due to count
    lost_due_to = df['lost due to'].value_counts(dropna=False).reset_index()
    lost_due_to.to_csv('d:/KIA/data/analysis_results/lost_due_to_breakdown.csv', index=False)
    print("Top lost due to causes:")
    print(lost_due_to.to_string(index=False))
    
    # Lost due to trended by month (using Enquiry Month for trend comparison)
    lost_trend = df[df['lost due to'].notnull()].groupby(['Enquiry Month', 'lost due to']).size().unstack(fill_value=0).reset_index()
    lost_trend.to_csv('d:/KIA/data/analysis_results/lost_due_to_monthly_trend.csv', index=False)
    
    # Enquiry aging & Followup count vs conversion outcome
    print("\n--- Running Aging & Followup Impact Analysis ---")
    # Group by conversion outcome: Lost vs Booked vs Retailed vs Active
    # Let's categorize leads:
    # 1. Retailed: Is_Retail == True
    # 2. Booked (not retailed): Is_Booking == True & Is_Retail == False
    # 3. Lost: lost reason is not null or status is Cancel
    # 4. Active (other)
    conditions = [
        (df['Is_Retail'] == True),
        (df['Is_Booking'] == True) & (df['Is_Retail'] == False),
        (df['lost reason'].notnull()) | (df['Enquiry Status'].str.contains('Cancel', na=False)),
    ]
    choices = ['Retailed', 'Booked (Active)', 'Lost']
    df['Outcome'] = np.select(conditions, choices, default='Active')
    
    outcome_metrics = df.groupby('Outcome').agg(
        Count=('Is_Enquiry', 'sum'),
        Avg_Aging=('enquiry aging days', 'mean'),
        Median_Aging=('enquiry aging days', 'median'),
        Avg_Followups=('Followup Count', 'mean'),
        Median_Followups=('Followup Count', 'median')
    ).reset_index()
    outcome_metrics.to_csv('d:/KIA/data/analysis_results/aging_followup_outcome.csv', index=False)
    print(outcome_metrics.to_string(index=False))
    
    # Followup Count correlation or conversion rate by Followup Count bucket
    df['Followup_Bucket'] = pd.cut(df['Followup Count'], bins=[-1, 0, 1, 2, 4, 6, 10, 100], labels=['0', '1', '2', '3-4', '5-6', '7-10', '11+'])
    followup_perf = df.groupby('Followup_Bucket', observed=False).agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    followup_perf['Booking_Rate'] = followup_perf['Bookings'] / followup_perf['Enquiries']
    followup_perf['Retail_Rate'] = followup_perf['Retails'] / followup_perf['Enquiries']
    followup_perf.to_csv('d:/KIA/data/analysis_results/followup_bucket_performance.csv', index=False)
    print("\nConversion by Follow-up Count:")
    print(followup_perf.to_string(index=False))

    # Aging Days bucket performance
    df['Aging_Bucket'] = pd.cut(df['enquiry aging days'], bins=[0, 7, 15, 30, 45, 60, 100], labels=['0-7 days', '8-15 days', '16-30 days', '31-45 days', '46-60 days', '61+ days'])
    aging_perf = df.groupby('Aging_Bucket', observed=False).agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    aging_perf['Booking_Rate'] = aging_perf['Bookings'] / aging_perf['Enquiries']
    aging_perf['Retail_Rate'] = aging_perf['Retails'] / aging_perf['Enquiries']
    aging_perf.to_csv('d:/KIA/data/analysis_results/aging_bucket_performance.csv', index=False)
    print("\nConversion by Enquiry Aging Days:")
    print(aging_perf.to_string(index=False))

    # ------------------ STEP 3: MODEL & CONSULTANT PERFORMANCE ------------------
    print("\n--- Running Model & Variant Performance ---")
    model_perf = df.groupby('Model').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    model_perf['TD_Rate'] = model_perf['Test_Drives'] / model_perf['Enquiries']
    model_perf['Booking_Rate'] = model_perf['Bookings'] / model_perf['Enquiries']
    model_perf['Retail_Rate'] = model_perf['Retails'] / model_perf['Enquiries']
    model_perf = model_perf.sort_values(by='Enquiries', ascending=False)
    model_perf.to_csv('d:/KIA/data/analysis_results/model_performance.csv', index=False)
    print(model_perf.to_string(index=False))
    
    variant_perf = df.groupby(['Model', 'Variant']).agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    variant_perf['Retail_Rate'] = variant_perf['Retails'] / variant_perf['Enquiries']
    variant_perf = variant_perf.sort_values(by='Enquiries', ascending=False)
    variant_perf.to_csv('d:/KIA/data/analysis_results/variant_performance.csv', index=False)
    
    # Consultant Performance
    print("\n--- Running Consultant Performance ---")
    # Clean consultant name casing
    df['Consultant Name'] = df['Consultant Name'].astype(str).str.strip().str.upper()
    df['Consultant Name'] = df['Consultant Name'].replace({'NAN': np.nan, 'NONE': np.nan})
    
    consultant_perf = df.groupby('Consultant Name').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    
    # Filter consultants with at least 10 leads to avoid small sample sizes in rates
    consultant_perf['TD_Conversion'] = consultant_perf['Test_Drives'] / consultant_perf['Enquiries']
    consultant_perf['Booking_Conversion'] = consultant_perf['Bookings'] / consultant_perf['Enquiries']
    consultant_perf['Retail_Conversion'] = consultant_perf['Retails'] / consultant_perf['Enquiries']
    consultant_perf = consultant_perf.sort_values(by='Retails', ascending=False)
    consultant_perf.to_csv('d:/KIA/data/analysis_results/consultant_performance.csv', index=False)
    print("Top 10 Consultants by Retail Deliveries:")
    print(consultant_perf.head(10).to_string(index=False))
    
    # Test Drive Impact (TD Done vs No TD)
    print("\n--- Running Test Drive Impact Analysis ---")
    td_impact = df.groupby('Is_TD').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    td_impact['Booking_Rate'] = td_impact['Bookings'] / td_impact['Enquiries']
    td_impact['Retail_Rate'] = td_impact['Retails'] / td_impact['Enquiries']
    td_impact.to_csv('d:/KIA/data/analysis_results/td_impact.csv', index=False)
    print(td_impact.to_string(index=False))

    # ------------------ STEP 4: MONTHLY TRENDS ------------------
    print("\n--- Running Monthly Trends ---")
    monthly_trends = df.groupby('Enquiry Month').agg(
        Enquiries=('Is_Enquiry', 'sum'),
        Test_Drives=('Is_TD', 'sum'),
        Bookings=('Is_Booking', 'sum'),
        Retails=('Is_Retail', 'sum')
    ).reset_index()
    monthly_trends['TD_Rate'] = monthly_trends['Test_Drives'] / monthly_trends['Enquiries']
    monthly_trends['Booking_Rate'] = monthly_trends['Bookings'] / monthly_trends['Enquiries']
    monthly_trends['Retail_Rate'] = monthly_trends['Retails'] / monthly_trends['Enquiries']
    monthly_trends.to_csv('d:/KIA/data/analysis_results/monthly_trends.csv', index=False)
    print(monthly_trends.to_string(index=False))
    
    # Source Mix Shift Trend
    source_mix = df.groupby(['Enquiry Month', 'Source']).size().unstack(fill_value=0)
    source_mix_pct = source_mix.div(source_mix.sum(axis=1), axis=0) * 100
    source_mix_pct.to_csv('d:/KIA/data/analysis_results/source_mix_trend_pct.csv')
    print("\nSource Mix Trend (%):")
    print(source_mix_pct.round(2).to_string())

if __name__ == '__main__':
    run_analysis()
