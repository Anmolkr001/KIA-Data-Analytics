# Data Quality Notes - Lead Conversion CRM Dataset

This document details the quality, anomalies, and transformations applied to the Kia Bhubaneswar CRM enquiry dataset spanning Jan-Jun 2026.

## 1. Merging & Schema Alignment
- **Total Rows Processed**: 6967
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
- **Quoted Price**: 90.89% zero or null (6332 zeros, 0 nulls).
- **Expected Price**: 90.89% zero or null (6332 zeros, 0 nulls).
- **Final Buying Price**: 100.00% zero or null (308 zeros, 6659 nulls).

## 4. Date Parsing Results
All dates have been parsed from mixed string/numeric structures into `YYYY-MM-DD` date objects:
- **Enquiry Date**: 6967 parsed (100% complete)
- **Test Drive Date**: 3249 parsed (missing dates imply "No Test Drive")
- **Booking Date**: 1672 parsed (missing dates imply "No Booking")
- **Retail Date**: 786 parsed (missing dates imply "No Retail Delivery")
- **Lost Date**: 1532 parsed (missing dates imply lead is active or not flagged as lost)

## 5. Categorical Inconsistencies Standardized
- **City**: Cleaned spellings and casings for 205 unique locations.
  - E.g. `Bhubaneshwar`, `Bhubaneswar`, `BBSR`, `bhubaneswar` standardized to `BHUBANESWAR`.
  - Mapped surrounding cities like Cuttack, Berhampur, Balasore, Rourkela, Sambalpur to uniform uppercase spellings.
- **Lost Due To**: Cleaned double spaces in values (e.g. `'Change  Request'` mapped to `'Change Request'`).
- **Model**: Unified casing for the 9 distinct Kia models.
