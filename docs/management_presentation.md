---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #111111
color: #eeeeee
style: |
  section {
    font-family: 'Outfit', 'Inter', sans-serif;
    padding: 40px;
  }
  h1 {
    color: #e51937; /* Kia Red */
  }
  h2 {
    color: #ffffff;
  }
  footer {
    font-size: 0.5em;
    color: #888888;
  }
---

# Lead Conversion Intelligence
## Bhubaneswar Kia Dealership Sales Performance
### Data Analysis: January – June 2026

**Presented by**: Data Analytics Team
**Dataset**: 6,967 Real CRM Leads

---

# 1. Executive Summary & Core KPIs

- **Dealership Health**: Over 6 months, the dealership generated **6,967 enquiries**, leading to **1,672 bookings** and **786 retail deliveries**.
- **Overall Conversion Rate**: **11.28%** of enquiries convert to a final car delivery.
- **The Core Sourcing Dilemma**: Our highest volume channel (*Hyperlocal*) is our lowest quality channel (**3.45%** conversion), while our lowest volume channel (*Referrals*) converts at **27.62%**.
- **The Conversion Driver**: Completing a Test Drive increases a customer's retail conversion probability by **4.3x** (**19.11%** vs **4.44%**).
- **Follow-up Sweet Spot**: Focus sales effort on **2 to 4 follow-ups**. After the 4th follow-up, conversion drops to **< 2.0%**.

---

# 2. The Conversion Funnel

```
[6,967] Enquiries (100%)
   │
   ├── Drop-off: 53.37% (No Test Drive)
   ▼
[3,249] Completed Test Drives (46.63%)
   │
   ├── Drop-off: 48.54% (No Booking)
   ▼
[1,672] Bookings (24.00%)
   │
   ├── Drop-off: 52.99% (Cancelled/Slipped)
   ▼
[786] Retail Deliveries (11.28%)
```

- **Slipped Bookings**: **52.99%** of bookings fail to convert to delivery. We must focus on reducing booking-to-retail cancellation rates.

---

# 3. Test Drives: The Ultimate Catalyst

Getting a customer behind the wheel is the strongest driver of sales conversion.

| Metric | No Test Drive | Test Drive Done | Lift |
| :--- | :---: | :---: | :---: |
| **Total Enquiries** | 3,718 | 3,249 | - |
| **Bookings** | 306 | 1,366 | **+346%** |
| **Retail Deliveries** | 165 | 621 | **+276%** |
| **Booking Rate** | 8.23% | **42.04%** | **5.1x** |
| **Retail Conversion Rate** | 4.44% | **19.11%** | **4.3x** |

**Action**: Implement a "Test Drive First" mandate for all walk-in and field leads.

---

# 4. Sourcing Channel Quality Audit

Are we paying for lead volume or lead conversions?

| Lead Source | Enquiries | Retails | Retail Conversion Rate | Booking-to-Retail |
| :--- | :---: | :---: | :---: | :---: |
| **Referral** | 1,097 | 303 | **27.62%** | **52.24%** |
| **Walk-in** | 1,627 | 219 | **13.46%** | 47.10% |
| **Field Sourcing** | 941 | 122 | **12.96%** | 41.08% |
| **Telephone** | 384 | 29 | **7.55%** | 32.95% |
| **Online / CRM** | 676 | 36 | **5.33%** | 50.70% |
| **Hyperlocal** | 2,232 | 77 | **3.45%** | 45.29% |

- **Hyperlocal Sourcing**: Sourced 32.0% of leads, but delivered only 9.8% of sales.
- **Referrals**: Sourced 15.7% of leads, but delivered 38.5% of sales.

---

# 5. Lead Score Validation

We evaluated the predictive power of the CRM's default lead classification (Hot/Warm/Cold).

| Lead Classification | Enquiries | Retails | Retail Conversion Rate | Booking Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Hot** | 1,698 | 777 | **45.76%** | 73.14% |
| **Warm** | 1,055 | 1 | **0.09%** | 9.76% |
| **Cold** | 4,214 | 8 | **0.19%** | 7.76% |

- **Hot Leads Work**: Hot leads are highly accurate and represent 98.8% of all retailed vehicles (777 out of 786).
- **Scoring Failure**: Warm leads convert at **0.09%**, which is actually *worse* than Cold leads (**0.19%**).
- **Recommendation**: Redefine the CRM scoring rules for Warm leads.

---

# 6. Follow-up Optimization

*Does more follow-up help, or does it waste sales team energy?*

- **The 2-4 Follow-up Peak**: Retail conversion rate is virtually **0.3%** for 1 follow-up, but shoots up to **19.06%** at 2 follow-ups and **17.26%** at 3-4 follow-ups.
- **The Cliff**: At 5-6 follow-ups, conversion collapses to **1.64%**, and falls to **< 1.0%** for 7+ follow-ups.
- **Over-servicing**: Consultants are wasting time doing 5 to 28 follow-ups on dead deals.
- **Under-servicing**: 1,963 leads had **0 or 1 follow-ups** and converted at < 0.3%. 

**Action**: Mandate exactly **3 follow-ups**. Reallocate resources from high-aging, high-followup leads to new leads.

---

# 7. Model Demand & Conversion

Which Kia models drive Bhubaneswar dealership revenue?

- **Kia Sonet**: The dealership's undisputed star. Sells **344 units** (43.8% of sales) with a strong **16.26%** conversion rate.
- **Kia Carens**: Highly efficient family segment. Sells **195 units** (24.8% of sales) with a strong **14.71%** conversion rate.
- **New Seltos**: High interest (**2,155 leads**, top volume), but weak conversion (**8.68%** conversion). It underperforms in turning interest into deliveries.
- **Kia Syros**: Emerging crossover segment. Converts **4.82%** of 332 leads.

---

# 8. Consultant Leaderboard

Top performing consultants drive conversions through high Test Drive rates.

| Consultant Name | Enquiries | Test Drives | Retails | TD Conversion | Retail Conversion |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **RAJ KUMAR JENA** | 144 | 115 | 42 | **79.86%** | **29.17%** |
| **MANISHA NAYAK** | 201 | 106 | 36 | 52.74% | 17.91% |
| **SOUMYA SASWAT NAYAK** | 145 | 106 | 32 | **73.10%** | **22.07%** |
| **RASHMITA SAHANI** | 147 | 111 | 31 | **75.51%** | **21.09%** |
| **CHITTARANJAN SAHOO** | 129 | 71 | 30 | 55.04% | **23.26%** |

- **Top Performer Benchmark**: Raj Kumar Jena achieves a **29.17% conversion rate** (2.5x dealership average) by ensuring **80%** of his leads take a Test Drive.

---

# 9. Lost Deal Analysis: Why are Leads Cancelling?

Out of 1,797 cancelled leads:

1. **Plan Postponed (36.4%)**: The customer decided to defer the purchase (market cooling or waiting for new models).
2. **Change Request (23.3%)**: The customer changed their mind about the vehicle segment or brand.
3. **Lost to Co-Dealer (7.5%)**: Leaked to another Kia dealer (pricing/discount war).
4. **Finance / Budget (7.5%)**: Loan rejection or budget mismatch.
5. **Lost to Competition (6.5%)**: Customer bought Maruti, Hyundai, or Mahindra instead.

---

# 10. Strategic Recommendations

1. **Reallocate Marketing Spend**: Cut Hyperlocal lead generation budget by **40%** and reallocate to **Referral/Co-marketing campaigns** and **Walk-in dealership experiences** which convert at 4x to 8x higher rates.
2. **Enforce Test Drive (TD) Compliance**: Set a KPI of **> 70% TD Rate** for walk-in and field leads. Sponsoring test drive events will directly multiply sales.
3. **Optimized Follow-up Policy**: Implement a strict **"3 & Out" follow-up policy**. Stop following up after the 4th call unless the lead is actively booking, saving consultant time.
4. **Revamp CRM Lead Scoring**: Adjust the algorithm for "Warm" leads to reflect actual buying signals, as the current Warm classification is not predictive.
5. **Mitigate Booking-to-Retail Slipped Leads**: Implement a finance pre-approval check at the booking stage to address the **53% booking-to-retail drop-off**.
