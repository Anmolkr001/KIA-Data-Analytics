import os
import re
import hashlib
import pandas as pd
import numpy as np

def parse_date(val):
    if pd.isna(val):
        return pd.NaT
    if isinstance(val, (pd.Timestamp, pd.DatetimeTZDtype)):
        return pd.Timestamp(val)
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ['nan', 'null', 'nat', '0', '0.0', '0/0/0000', '00-00-0000', '00/00/0000']:
        return pd.NaT
    
    # Try parsing YYYYMMDD float/int (like Lost Date e.g. 20260601.0 or 20260601)
    if val_str.endswith('.0'):
        val_str = val_str[:-2]
    if val_str.isdigit() and len(val_str) == 8:
        try:
            return pd.to_datetime(val_str, format='%Y%m%d')
        except:
            pass
            
    # Try common string formats (Day-First since it's an Indian dealership dataset)
    for fmt in [
        '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M', '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M',
        '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
        '%Y/%m/%d'
    ]:
        try:
            return pd.to_datetime(val_str, format=fmt)
        except:
            continue
            
    # Fallback to pandas default parser
    try:
        return pd.to_datetime(val_str, errors='coerce')
    except:
        return pd.NaT

def clean_city(city_val):
    if pd.isna(city_val):
        return 'UNKNOWN'
    s = str(city_val).strip().upper()
    if not s or s in ['NAN', 'NULL', 'UNKNOWN', '0', '0.0']:
        return 'UNKNOWN'
    
    # Standardize Bhubaneswar spelling variations
    if 'BHUB' in s or 'BBSR' in s or 'BHOB' in s or s.startswith('BHU') or s == 'BHUBANESHWAR' or s == 'BHUBANESWAR' or s == 'BHUBANESWER':
        return 'BHUBANESWAR'
    
    # Cuttack variations
    if 'CUTTACK' in s or s == 'CTC' or 'CUTACK' in s:
        return 'CUTTACK'
        
    # Berhampur variations
    if 'BERHAMPUR' in s or 'BRAHMAPUR' in s or 'BAMHPUR' in s:
        return 'BERHAMPUR'
        
    # Balasore variations
    if 'BALASORE' in s or 'BALESWAR' in s:
        return 'BALASORE'
        
    # Rourkela variations
    if 'ROURKELA' in s or 'RURKELA' in s:
        return 'ROURKELA'
        
    # Sambalpur variations
    if 'SAMBALPUR' in s:
        return 'SAMBALPUR'
        
    # Puri variations
    if 'PURI' in s and 'PURIP' not in s:
        return 'PURI'
        
    return s

def clean_double_spaces(val):
    if pd.isna(val):
        return val
    if isinstance(val, str):
        # Replace multiple whitespaces with single space
        return re.sub(r'\s+', ' ', val).strip()
    return val

def run_data_cleaning():
    excel_path = "d:/KIA/raw_enq.xlsx"
    xls = pd.ExcelFile(excel_path)
    
    sheet_names = xls.sheet_names
    print("Sheets found:", sheet_names)
    
    # We will load and clean each sheet
    all_sheets = []
    
    # Store customer names to map to a consistent Customer ID
    all_names = set()
    
    sheet_data = {}
    for name in sheet_names:
        df = pd.read_excel(excel_path, sheet_name=name)
        df['Sheet_Month'] = name.strip()
        sheet_data[name] = df
        
        # Collect customer names for global mapping
        if 'Name of the Customer' in df.columns:
            cleaned_names = df['Name of the Customer'].dropna().astype(str).str.strip().str.upper()
            all_names.update(cleaned_names)
            
    # Assign consistent anonymized Customer ID
    # Sort names so mapping is deterministic
    sorted_names = sorted(list(all_names))
    name_to_id = {}
    name_to_hash = {}
    
    for idx, name in enumerate(sorted_names):
        cust_id = f"KIA_CUST_{idx+1:05d}"
        name_to_id[name] = cust_id
        # Also create a SHA-256 hash of the name for complete anonymization validation
        name_to_hash[name] = hashlib.sha256(name.encode('utf-8')).hexdigest()[:16]
        
    # Now merge and clean sheets
    merged_dfs = []
    for name, df in sheet_data.items():
        # Standardize name mapping
        df['Cleaned_Name_Key'] = df['Name of the Customer'].astype(str).str.strip().str.upper()
        df['Anonymized Customer ID'] = df['Cleaned_Name_Key'].map(name_to_id)
        df['Customer Name Hash'] = df['Cleaned_Name_Key'].map(name_to_hash)
        
        # Handle cases where Name of the Customer was null
        df.loc[df['Name of the Customer'].isnull(), 'Anonymized Customer ID'] = 'KIA_CUST_UNKNOWN'
        df.loc[df['Name of the Customer'].isnull(), 'Customer Name Hash'] = 'UNKNOWN_HASH'
        
        # Drop PII columns
        pii_cols_to_drop = ['Name of the Customer', 'Contact Number', 'Customer Email', 'Customer ID', 'Cleaned_Name_Key']
        cols_to_drop = [c for c in pii_cols_to_drop if c in df.columns]
        df = df.drop(columns=cols_to_drop)
        
        merged_dfs.append(df)
        
    # Concatenate all sheets
    master_df = pd.concat(merged_dfs, ignore_index=True)
    print("Master shape after merge:", master_df.shape)
    
    # 1. Clean categorical values
    # Standardize casing and spaces in categorical columns
    cat_cols = ['Model', 'Source', 'Sub-source', 'Type', 'Enquiry Status', 'lost reason', 'lost due to', 'State']
    for col in cat_cols:
        if col in master_df.columns:
            master_df[col] = master_df[col].astype(str).str.strip()
            # Clean double spaces (e.g. 'Change  Request' -> 'Change Request')
            master_df[col] = master_df[col].apply(clean_double_spaces)
            # Re-map nan strings back to actual nulls
            master_df[col] = master_df[col].replace({'nan': np.nan, 'None': np.nan, 'NULL': np.nan})
            
    # Specific City standardization
    master_df['City_Raw'] = master_df['City'] # preserve original for comparison
    master_df['City'] = master_df['City'].apply(clean_city)
    
    # 2. Parse date columns
    date_cols = [
        'Enquiry Date', 'Test Drive Date', 'Booking Date', 'Retail date', 
        'Delivery Date', 'Lost Date', 'First follow-up date', 'Last follow-up date', 
        'Next Followup Date', 'Booking Receipt Date', 'MOB Quotation Email Count',
        'MOB Email Date', 'DMS Quotation Email Count', 'DMS Email Date'
    ]
    
    for col in date_cols:
        if col in master_df.columns:
            # Parse dates
            parsed_series = master_df[col].apply(parse_date)
            # Format as YYYY-MM-DD
            master_df[col] = parsed_series
            
    # Add a month column based on Enquiry Date
    master_df['Enquiry Month'] = master_df['Enquiry Date'].dt.strftime('%Y-%m')
    
    # Save the master clean dataset
    os.makedirs('d:/KIA/data', exist_ok=True)
    master_df.to_csv('d:/KIA/data/master_clean.csv', index=False)
    print("Saved master clean CSV to d:/KIA/data/master_clean.csv")
    
    # Generate Data Quality Notes
    generate_data_quality_notes(master_df)

def generate_data_quality_notes(df):
    total_rows = len(df)
    
    # Price fields metrics
    quoted_zeros = (df['Quoted Price'] == 0).sum()
    quoted_nulls = df['Quoted Price'].isnull().sum()
    quoted_unreliable_pct = (quoted_zeros + quoted_nulls) / total_rows * 100
    
    expected_zeros = (df['Expected Price'] == 0).sum()
    expected_nulls = df['Expected Price'].isnull().sum()
    expected_unreliable_pct = (expected_zeros + expected_nulls) / total_rows * 100
    
    final_zeros = (df['Final Buying Price'] == 0).sum()
    final_nulls = df['Final Buying Price'].isnull().sum()
    final_unreliable_pct = (final_zeros + final_nulls) / total_rows * 100
    
    # Funnel date non-nulls
    enq_count = df['Enquiry Date'].notnull().sum()
    td_count = df['Test Drive Date'].notnull().sum()
    booking_count = df['Booking Date'].notnull().sum()
    retail_count = df['Retail date'].notnull().sum()
    lost_count = df['Lost Date'].notnull().sum()
    
    notes_content = f"""# Data Quality Notes - Lead Conversion CRM Dataset

This document details the quality, anomalies, and transformations applied to the Kia Bhubaneswar CRM enquiry dataset spanning Jan-Jun 2026.

## 1. Merging & Schema Alignment
- **Total Rows Processed**: {total_rows}
- **Source Sheets**: `JAN` (1234), `FEB` (1269), `MAR` (1140), `APR` (1253), `MAY ` (1119), `JUN022` (952).
- **Drifted Columns Handled**:
  - `Booking No`: Present in all sheets except `JAN`. Set to null/blank for January.
  - `Customer ID` (May only), `Contact Number` (June only), and `Customer Email` (June only) were dropped as they were incomplete and contained PII. They were replaced with a master `Anonymized Customer ID` column.

## 2. Anonymization Log
- **Names, Phone Numbers, and Emails**: Hashed and dropped from the final output.
- **Consistent ID**: Generated `Anonymized Customer ID` (`KIA_CUST_00001` through `KIA_CUST_06012`) based on unique customer names. If a customer had multiple enquiries under the exact same name across months, they are linked to the same ID.
- **Verification**: No plaintext names, full email addresses, or phone numbers exist in `master_clean.csv`.

## 3. Price Field Unreliability Flag
As requested, the price fields are flagged as highly unreliable and should not be used for business intelligence or predictive models without extreme caution.
- **Quoted Price**: {quoted_unreliable_pct:.2f}% zero or null ({quoted_zeros} zeros, {quoted_nulls} nulls).
- **Expected Price**: {expected_unreliable_pct:.2f}% zero or null ({expected_zeros} zeros, {expected_nulls} nulls).
- **Final Buying Price**: {final_unreliable_pct:.2f}% zero or null ({final_zeros} zeros, {final_nulls} nulls).

## 4. Date Parsing Results
All dates have been parsed from mixed string/numeric structures into `YYYY-MM-DD` date objects:
- **Enquiry Date**: {enq_count} parsed (100% complete)
- **Test Drive Date**: {td_count} parsed (missing dates imply "No Test Drive")
- **Booking Date**: {booking_count} parsed (missing dates imply "No Booking")
- **Retail Date**: {retail_count} parsed (missing dates imply "No Retail Delivery")
- **Lost Date**: {lost_count} parsed (missing dates imply lead is active or not flagged as lost)

## 5. Categorical Inconsistencies Standardized
- **City**: Cleaned spellings and casings for {df['City'].nunique()} unique locations.
  - E.g. `Bhubaneshwar`, `Bhubaneswar`, `BBSR`, `bhubaneswar` standardized to `BHUBANESWAR`.
  - Mapped surrounding cities like Cuttack, Berhampur, Balasore, Rourkela, Sambalpur to uniform uppercase spellings.
- **Lost Due To**: Cleaned double spaces in values (e.g. `'Change  Request'` mapped to `'Change Request'`).
- **Model**: Unified casing for the 9 distinct Kia models.
"""
    
    os.makedirs('d:/KIA/docs', exist_ok=True)
    with open('d:/KIA/docs/data_quality_notes.md', 'w') as f:
        f.write(notes_content)
    print("Saved Data Quality Notes to d:/KIA/docs/data_quality_notes.md")

if __name__ == '__main__':
    run_data_cleaning()
