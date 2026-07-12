# Lead Conversion Intelligence - Analysis Report
Bhubaneswar Kia Dealership (Jan-Jun 2026)

This report outlines the detailed funnel, vehicle model, consultant, and monthly trend analysis of the 6,967 leads processed from the dealership CRM.

---

## 1. Funnel & Conversion Performance
The conversion funnel tracks customer progression from the initial CRM enquiry through the Test Drive, Booking, and final Retail Delivery stages.

| Stage      |   Count |   Conversion_of_Enquiry |   Stage_to_Stage_Conversion |   Drop_off_Rate |
|:-----------|--------:|------------------------:|----------------------------:|----------------:|
| Enquiry    |    6967 |                1        |                    1        |        0        |
| Test Drive |    3249 |                0.466341 |                    0.466341 |        0.533659 |
| Booking    |    1672 |                0.239989 |                    0.51462  |        0.48538  |
| Retail     |     786 |                0.112818 |                    0.470096 |        0.529904 |

**Key Funnel Takeaways**:
- **Overall Conversion**: **11.28%** of enquiries convert to a retail delivery.
- **Top Drop-off Point**: **53.37%** of leads drop off between Enquiry and Test Drive. Getting customers into a test drive is the single largest hurdle.
- **Stage-to-Stage**: Once a Test Drive is completed, **51.46%** book a vehicle. Of those who book, **47.01%** reach retail delivery.

---

## 2. Lead Source & Sub-Source Performance
Analysis of where leads originate and how they convert.

| Source     |   Enquiries |   Test_Drives |   Bookings |   Retails |   TD_Rate |   Booking_Rate |   Retail_Rate |   Booking_to_Retail |
|:-----------|------------:|--------------:|-----------:|----------:|----------:|---------------:|--------------:|--------------------:|
| Referral   |        1097 |           645 |        580 |       303 |  0.587967 |      0.528715  |     0.276208  |            0.522414 |
| Walkin     |        1627 |          1191 |        465 |       219 |  0.732022 |      0.285802  |     0.134604  |            0.470968 |
| Field      |         941 |           610 |        297 |       122 |  0.648247 |      0.315622  |     0.129649  |            0.410774 |
| Hyperlocal |        2232 |           412 |        170 |        77 |  0.184588 |      0.0761649 |     0.0344982 |            0.452941 |
| Online/CRM |         676 |           197 |         71 |        36 |  0.29142  |      0.10503   |     0.0532544 |            0.507042 |
| Telephone  |         384 |           191 |         88 |        29 |  0.497396 |      0.229167  |     0.0755208 |            0.329545 |

**Key Source Takeaways**:
- **Referral** is the highest-performing channel, converting **27.62%** of leads to retail. It has a high booking-to-retail conversion of **52.24%**.
- **Walk-in** and **Field** activities are solid channels, converting **13.46%** and **12.96%** respectively.
- **Hyperlocal** campaigns generate the highest lead volume (**2,232 leads**, 32.0% of total) but perform the worst, converting only **3.45%** to retail. This indicates low-quality lead generation that wastes consultant effort.

---

## 3. Lead Score (Type) Validation
Validation of the CRM's default lead scoring (Hot, Warm, Cold).

| Type   |   Enquiries |   Test_Drives |   Bookings |   Retails |   Booking_Rate |   Retail_Rate |
|:-------|------------:|--------------:|-----------:|----------:|---------------:|--------------:|
| Hot    |        1698 |          1251 |       1242 |       777 |      0.731449  |   0.457597    |
| Cold   |        4214 |          1489 |        327 |         8 |      0.0775985 |   0.00189843  |
| Warm   |        1055 |           509 |        103 |         1 |      0.0976303 |   0.000947867 |

**Key Scoring Takeaways**:
- **Hot Leads** are highly predictive, converting at a massive **45.76%** retail rate.
- **Warm Leads** (**0.09%**) and **Cold Leads** (**0.19%**) have virtually zero retail conversion.
- *Anomaly*: Warm leads convert at a lower rate than Cold leads. This suggests that the "Warm" criteria in the CRM are not predictive and need adjustment.

---

## 4. Lost Deal Analysis
Breakdown of lost leads and why they were cancelled.

| lost due to              |   count |
|:-------------------------|--------:|
| nan                      |    5424 |
| Plan Postponed           |     655 |
| Change Request           |     418 |
| Lost to co-dealer        |     135 |
| Finance / budget related |     134 |
| Lost to competition      |     117 |
| Do not like the car      |      68 |
| Delay in delivery        |      16 |

**Key Lost Takeaways**:
- **Plan Postponed** (**36.4%** of lost reasons) and **Change Request** (**23.3%**) represent almost 60% of cancellations. This indicates that timing and change of mind are the primary obstacles rather than product dislike.
- **Lost to co-dealer** (**7.5%**) indicates leakage to other Kia dealerships in the region.

---

## 5. Enquiry Aging and Follow-up Impact

### Outcome Comparison
| Outcome         |   Count |   Avg_Aging |   Median_Aging |   Avg_Followups |   Median_Followups |
|:----------------|--------:|------------:|---------------:|----------------:|-------------------:|
| Active          |    3672 |     20.3295 |             17 |         2.50136 |                  2 |
| Booked (Active) |     886 |     21.0801 |             18 |         2.60497 |                  2 |
| Lost            |    1623 |     29.2304 |             28 |         2.7443  |                  2 |
| Retailed        |     786 |     26.2468 |             24 |         2.58651 |                  2 |

### Conversion by Follow-up Count
| Followup_Bucket   |   Enquiries |   Bookings |   Retails |   Booking_Rate |   Retail_Rate |
|:------------------|------------:|-----------:|----------:|---------------:|--------------:|
| 0                 |         372 |          0 |         0 |     0          |    0          |
| 1                 |        1591 |          9 |         5 |     0.00565682 |    0.00314268 |
| 2                 |        2203 |        894 |       420 |     0.40581    |    0.190649   |
| 3-4               |        2034 |        747 |       351 |     0.367257   |    0.172566   |
| 5-6               |         487 |         18 |         8 |     0.036961   |    0.0164271  |
| 7-10              |         211 |          3 |         2 |     0.014218   |    0.00947867 |
| 11+               |          69 |          1 |         0 |     0.0144928  |    0          |

### Conversion by Enquiry Aging Days
| Aging_Bucket   |   Enquiries |   Bookings |   Retails |   Booking_Rate |   Retail_Rate |
|:---------------|------------:|-----------:|----------:|---------------:|--------------:|
| 0-7 days       |        1103 |        247 |        66 |       0.223935 |     0.0598368 |
| 8-15 days      |        1496 |        363 |       169 |       0.242647 |     0.112968  |
| 16-30 days     |        2300 |        546 |       256 |       0.237391 |     0.111304  |
| 31-45 days     |        1318 |        339 |       186 |       0.257208 |     0.141123  |
| 46-60 days     |         680 |        157 |        97 |       0.230882 |     0.142647  |
| 61+ days       |          70 |         20 |        12 |       0.285714 |     0.171429  |

**Key Takeaways**:
- **Follow-up Sweet Spot**: Lead conversion peaks sharply at **2 to 4 follow-ups** (17-19% conversion). 
- **Diminishing Returns**: If a lead does not book by the 4th follow-up, further follow-ups are highly ineffective (dropping to ~1.6% at 5-6 and < 1% at 7+).
- **Early Abandonment**: Leads with 0 or 1 follow-ups convert at < 0.3%, suggesting a large pool of leads is abandoned prematurely.
- **Aging is not a Deal Killer**: Retailed leads have an average aging of **26.25 days**, and conversion rate actually increases with aging (up to 17.14% for 61+ days). This indicates that the buying process takes time, and mature leads should not be discarded.

---

## 6. Vehicle Model Demand and Conversion
Ranking models by volume and conversion rates.

| Model            |   Enquiries |   Test_Drives |   Bookings |   Retails |   TD_Rate |   Booking_Rate |   Retail_Rate |
|:-----------------|------------:|--------------:|-----------:|----------:|----------:|---------------:|--------------:|
| NEW SELTOS       |        2155 |          1241 |        537 |       187 | 0.57587   |      0.249188  |     0.0867749 |
| SONET            |        2115 |          1123 |        640 |       344 | 0.530969  |      0.3026    |     0.162648  |
| CARENS           |        1326 |           656 |        354 |       195 | 0.494721  |      0.266968  |     0.147059  |
| SELTOS           |         566 |            32 |         41 |        24 | 0.0565371 |      0.0724382 |     0.0424028 |
| CARENS CLAVIS EV |         441 |           110 |         50 |        20 | 0.249433  |      0.113379  |     0.0453515 |
| SYROS            |         332 |            87 |         50 |        16 | 0.262048  |      0.150602  |     0.0481928 |
| CARNIVAL         |          23 |             0 |          0 |         0 | 0         |      0         |     0         |
| EV6              |           8 |             0 |          0 |         0 | 0         |      0         |     0         |
| EV9              |           1 |             0 |          0 |         0 | 0         |      0         |     0         |

**Key Model Takeaways**:
- **Kia Sonet** is the star model: it has high volume (2,115 leads) and the highest conversion rate (**16.26%**), delivering 344 cars.
- **New Seltos** has the highest volume (2,155 leads) but a lower conversion rate of **8.68%**.
- **Kia Carens** is very strong, converting **14.71%** of its 1,326 leads.
- **Crossover/EV models** (Carnival, EV6, EV9) have negligible volume and zero retail deliveries in this dataset.

---

## 7. Test Drive Impact
Comparing booking and retail rates for customers who did a Test Drive vs. those who did not.

| Is_TD   |   Enquiries |   Bookings |   Retails |   Booking_Rate |   Retail_Rate |
|:--------|------------:|-----------:|----------:|---------------:|--------------:|
| False   |        3718 |        306 |       165 |      0.0823023 |     0.0443787 |
| True    |        3249 |       1366 |       621 |      0.420437  |     0.191136  |

**Key Test Drive Takeaways**:
- Customers who complete a Test Drive are **4.3 times more likely to buy** (19.11% vs. 4.44% retail rate) and **5.1 times more likely to book** (42.04% vs. 8.23%).
- Completed Test Drives drive over 78.9% of all retail deliveries (621 out of 786).

---

## 8. Monthly Volume and Source Mix Trends

### Monthly Summary
| Enquiry Month   |   Enquiries |   Test_Drives |   Bookings |   Retails |   TD_Rate |   Booking_Rate |   Retail_Rate |
|:----------------|------------:|--------------:|-----------:|----------:|----------:|---------------:|--------------:|
| 2026-01         |        1234 |           387 |        289 |       177 |  0.313614 |       0.234198 |     0.143436  |
| 2026-02         |        1269 |           563 |        276 |       137 |  0.443656 |       0.217494 |     0.107959  |
| 2026-03         |        1140 |           588 |        272 |       100 |  0.515789 |       0.238596 |     0.0877193 |
| 2026-04         |        1253 |           675 |        309 |       157 |  0.538707 |       0.246608 |     0.125299  |
| 2026-05         |        1119 |           589 |        318 |       146 |  0.526363 |       0.284182 |     0.130474  |
| 2026-06         |         952 |           447 |        208 |        69 |  0.469538 |       0.218487 |     0.072479  |

### Source Mix Shift Trend (%)
| Enquiry Month   |    Field |   Hyperlocal |   Online/CRM |   Referral |   Telephone |   Walkin |
|:----------------|---------:|-------------:|-------------:|-----------:|------------:|---------:|
| 2026-01         |  6.64506 |      40.6807 |     11.6694  |    16.4506 |     2.8363  |  21.718  |
| 2026-02         | 11.746   |      32.619  |     12.7778  |    12.8571 |     5.07937 |  24.9206 |
| 2026-03         | 11.1404  |      28.5088 |     11.4912  |    16.2281 |     6.31579 |  26.3158 |
| 2026-04         | 15.1636  |      32.4022 |      8.30008 |    15.0838 |     5.98563 |  23.0646 |
| 2026-05         | 20.0179  |      23.5925 |      7.32797 |    18.3199 |     6.43432 |  24.3074 |
| 2026-06         | 17.8759  |      34.0694 |      5.67823 |    16.0883 |     6.94006 |  19.3481 |

**Key Trend Takeaways**:
- Enquiry volume peaks in Jan/Feb and April, dropping to a low of 952 in June.
- Retail conversion rates peaked in January (**14.34%**) and have generally trended downward, hitting a low of **7.25%** in June.
- **Field** leads increased from 6.65% in January to 17.88% in June, showing an expansion in outdoor sourcing.
- **Online/CRM** leads halved from 11.67% in January to 5.68% in June.
