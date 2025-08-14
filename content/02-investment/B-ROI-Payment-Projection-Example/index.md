---
date: 2025-08-14
title: index
---
---
title: B. ROI Payment Projection Example
description: Seasonal retainer with KPI-based revenue share and a quarterly savings bonus, modeled against historical seasonality.
tags: [investment, roi, projection, finance, billing]
publish: True
enableToc: True
lastmod: 2025-08-10
date: 2025-08-11
---
# B. ROI Payment Projection Example

> **Assumptions (editable):**
> - Monthly revenue (Apr→Mar): 42,580 · 33,050 · 51,472 · 18,329 · 20,592 · 33,139 · 36,253 · 22,696 · 19,924 · 19,208 · 69,567 · 25,440  
> - **Seasonal retainer:** $1,000 × clamp(Rev ÷ Annual Avg, 0.75, 1.25) → **$750–$1,250**  
> - **Rev share:** **3%** (example; final % depends on monthly KPI score; **cap 5%**)  
> - **Tools:** **$150/mo** pass-through  
> - **Time savings value:** first **3 months = 10 hrs/week**, then **20 hrs/week** once stabilized  
> - **Rate for savings calc:** **$85/hr** (entry-level virtual C-Suite)  
> - **Bonus on savings:** **15%**, **true-up quarterly**

### Monthly Projection (fees)

| Month | Income | Retainer | Rev Share (3%) | Tools | Bonus (15% time value) | Fee excl Bonus | Fee incl Bonus |
|---|---:|---:|---:|---:|---:|---:|---:|
| Apr | $42,580.17 | $1,250.00 | $1,277.41 | $150.00 | $552.07 | $2,677.41 | $3,229.48 |
| May | $33,049.89 | $1,010.00 | $991.50 | $150.00 | $552.07 | $2,151.50 | $2,703.57 |
| Jun | $51,472.27 | $1,250.00 | $1,544.17 | $150.00 | $552.07 | $2,944.17 | $3,496.24 |
| Jul | $18,329.38 | $750.00 | $549.88 | $150.00 | $1,104.15 | $1,449.88 | $2,554.03 |
| Aug | $20,591.78 | $750.00 | $617.75 | $150.00 | $1,104.15 | $1,517.75 | $2,621.90 |
| Sep | $33,138.93 | $1,010.00 | $994.17 | $150.00 | $1,104.15 | $2,154.17 | $3,258.32 |
| Oct | $36,252.81 | $1,110.00 | $1,087.58 | $150.00 | $1,104.15 | $2,347.58 | $3,451.73 |
| Nov | $22,695.60 | $750.00 | $680.87 | $150.00 | $1,104.15 | $1,580.87 | $2,685.02 |
| Dec | $19,923.79 | $750.00 | $597.71 | $150.00 | $1,104.15 | $1,497.71 | $2,601.86 |
| Jan | $19,207.83 | $750.00 | $576.23 | $150.00 | $1,104.15 | $1,476.23 | $2,580.38 |
| Feb | $69,566.94 | $1,250.00 | $2,087.01 | $150.00 | $1,104.15 | $3,487.01 | $4,591.16 |
| Mar | $25,440.45 | $870.00 | $763.21 | $150.00 | $1,104.15 | $1,783.21 | $2,887.36 |
| **Totals** | **$392,749.84** | **$11,412.00** | **$11,766.50** | **$1,800.00** | **$11,594.02** | **$24,978.50** | **$36,572.52** |

**Reading the table**
- **Fee excl Bonus** = Retainer + Rev Share + Tools (billed monthly).  
- **Bonus** = 15% of measured savings; we **true-up quarterly** using time-tracking & invoices.  
- Rev share adjusts monthly by KPI score (1%/3%/5% ladder; **5% cap**).

---

### What the client gets back (quick ROI view)

- **Time savings value (year): ~ $77,291** (10→20 hrs/wk at $85/hr).  
  - Client keeps **~85%** of that; the 15% bonus (~**$11,594**) is paid only when realized and verified.  
- **Total annual fees incl bonus:** **~$36,573**  
- **ROI on time savings alone:** **~2.1×** (excludes any lift from added leads, faster collections, fewer errors, etc.)

> **Lead-lift upside (framework):**  
> With **1,700 new leads** added + outbound, the revenue upside depends on your conversion and average gross profit per job:
>
> ```
> Added Gross Profit ≈ Leads × Close Rate × Avg Gross Profit per Job
> Example knobs to try:
>   - Close Rate: 1–5% (cold outbound construction range)
>   - Avg Gross Profit / Job: $2,500 – $7,500 (adjust to your book)
> ```
> We’ll plug in your actuals and attribute uplift in the quarterly true-up.

---

### Quarterly Audit & True-Up (how it works)

1) **Lock a baseline** (trailing 3 months before engagement) for revenue, hours, chargebacks/waivers, and tool spend.  
2) **Track** weekly: dashboards, time entries, revenue, and savings events with evidence.  
3) **Quarterly true-up**:  
   - Recompute KPI score → final rev-share% (never above **5% cap**)  
   - Compute **verified savings** → 15% bonus  
   - Reconcile any provisional vs actuals (+/– credit or charge)

> This keeps incentives aligned and fees right-sized to results.

---

### Notes & Options
- Want a **fixed weekly** setup? Use **$230/week** retainer + % rev-share + quarterly bonus as above.  
- If monthly revenue is highly volatile, we can use **quarterly averaging** for the seasonality factor to smooth the retainer.

---
---
title: "B. ROI & Payment Projection (Example)"
date: 2025-08-11
summary: A concrete example of monthly totals, weekly smoothing, and quarterly true-ups.
tags: [investment, payments, roi, pricing, example]
publish: true
enableToc: true
aliases: ["ROI and Payment Projection Example"]
---

> [!note]
> This page shows **how the math works** and a **readable schedule**. For live numbers, we maintain a spreadsheet with formulas and true-up inputs each quarter.

## Inputs (you can tweak)

- **Base Retainer:** `$1,000 / month`
- **Seasonality clamp:** `0.75×` to `1.25×`
- **Tools:** `$150 / month`
- **Revenue Share (baseline):** `3% of monthly revenue`
- **Revenue Share (stretch view):** `5%` (for planning comparison)
- **Bonus (budgeted):** `15% × Estimated Annual Savings`, allocated by seasonality

## Formulas (plain English)

- **Seasonal weight** for a month = `month revenue ÷ annual revenue`.
- **Retainer per month** = `BaseRetainer × CLAMP( month revenue ÷ avg revenue, 0.75, 1.25 )`.
- **Monthly baseline total** = `Retainer + Tools + (3% × month revenue) + (BonusPool × seasonal weight)`.
- **Weekly baseline** = `Monthly baseline ÷ 4.333` (approx weeks/month).
- **Quarterly true-up** = `(Actuals − Plan)` over the last 3 months.  
  Spread across **future months by seasonal weight**, then divided by weeks to add/subtract on each weekly payment.

## Example schedule (illustrative)

> Replace `Forecast Revenue` with your plan. The totals update per formulas above.

| Month | Forecast Revenue | Retainer* | Tools | Rev-Share 3% | Bonus (budgeted) | **Monthly Total** | **Weekly (≈/wk)** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Apr | 42,580 | 1,250 | 150 | 1,277 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| May | 33,050 | 1,000 | 150 | 992 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Jun | 51,472 | 1,250 | 150 | 1,544 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Jul | 18,329 | 750 | 150 | 550 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Aug | 20,592 | 750 | 150 | 618 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Sep | 33,139 | 1,000 | 150 | 994 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Oct | 36,253 | 1,000 | 150 | 1,088 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Nov | 22,696 | 750 | 150 | 681 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Dec | 19,924 | 750 | 150 | 598 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Jan | 19,208 | 750 | 150 | 576 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Feb | 69,567 | 1,250 | 150 | 2,087 | *(φ·BonusPool)* | **(calc)** | **(calc)** |
| Mar | 25,440 | 1,000 | 150 | 763 | *(φ·BonusPool)* | **(calc)** | **(calc)** |

\*Retainer is clamped between \$750 and \$1,250 per month.

> [!tip]
> If you want a **stretch** column at 5% revenue share for comparison, duplicate the table and use `5% × Forecast Revenue` in that column.

## Quarterly true-up example

- **Inputs:** Q1 actual revenue, tools receipts, realized savings, KPI results.  
- **Delta computed:** `Quarter Delta = Actual − Plan`.  
- **Spread:** Allocate delta across **future months** by seasonal weight.  
- **Weekly effect:** `AdjWeekly = (Delta_for_month ÷ 4.333)` added to each week in that month.

## How we keep it fair

- Busy months carry **more of any delta**, slow months carry **less**.  
- Weekly smoothing avoids spikes.  
- We re-plan every quarter over an **18-month window** so agreements stay aligned with results.

## Next steps

- Want us to load your latest plan here and publish the live numbers?  
  Ping us and we’ll sync the spreadsheet → site view for you.
- Back to terms: [[A-Investment-Payment-Terms]]

<!-- AUTO-TOC:START -->

## Contents
- [[02-investment/B-ROI-Payment-Projection-Example/B-ROI-and-Payment-Projection-Example]]
- [[02-investment/B-ROI-Payment-Projection-Example]]

<!-- AUTO-TOC:END -->

<!-- RELATED:START -->

## Related
**Backlinks**
- [[01-scope/D-What-I-Do]]
- [[01-scope/E-What-I-DON-T-Do]]
- [[01-scope/F-What-I-Expect-From-You]]
- [[01-scope/G-KPIs-Goals]]
- [[02-investment/B-ROI-Payment-Projection-Example]]
- [[03-roadmap-strategies-faqs/A-Roadmap]]
- [[03-roadmap-strategies-faqs/B-Strategies]]
- [[03-roadmap-strategies-faqs/C-FAQs]]
- [[05-agreement/A. Agreement Sections]]
- [[07-financials/A-Assets/assets]]
- [[07-financials/B-Banks/banking]]
- [[07-financials/C-Contractors/payroll-contractors]]
- [[07-financials/D-Liability/loans-n-credit]]
- [[07-financials/E-Expenses/expenses]]
- [[07-financials/F-Entity-Docs/entity-docs]]
- [[07-financials/I-Insurance/insurance]]
- [[07-financials/O-Others/other-deductions]]
- [[07-financials/R-Reports/reports]]
- [[07-financials/T-Taxes/taxes]]
- [[08-marketing/A-Brand-Assets/logos-and-assets]]
- [[08-marketing/B-Sales-Materials/sales-materials]]
- [[08-marketing/D-Decks/brochures-and-decks]]
- [[08-marketing/E-Testimonials/testimonials]]
- [[08-marketing/F-Websites/website-and-socials]]
- [[08-marketing/marketing-overview]]
- [[09-operations/A-Sops/sample-sop]]
- [[09-operations/A-Sops/standard-ops]]
- [[09-operations/C-Vendors/vendors-list]]
- [[09-operations/operations-overview]]
- [[10-technology/A-Architecture/cfo-os-technical-architecture]]
- [[10-technology/B-Development/integrations]]
- [[10-technology/B-Development/web-deployment-readme]]
- [[10-technology/C-Chatbot/chatbot-readme]]
- [[10-technology/D-Docs/client-installation-guide]]
- [[10-technology/D-Docs/deployment-checklist]]
- [[10-technology/D-Docs/licenses-and-keys]]
- [[10-technology/E-Tech-Stack/technology]]
- [[10-technology/E-Tech-Stack/tools-stack]]
- [[11-legal-compliance/legal-compliance]]
- [[12-human-resources/hr-overview]]
- [[12-human-resources/policies-and-handbooks]]
- [[12-human-resources/team-directory]]
- [[13-engagements/engagements]]
- [[99-archives/archives-overview]]
- [[.]]

**Similar by tag**
- [[01-scope/B-QiSuiteTM-Overview]]
- [[02-investment/A-Investment-Payment-Terms/A-Investment-and-Payment-Terms]]
- [[02-investment/A-Investment-Payment-Terms]]
- [[02-investment/B-ROI-Payment-Projection-Example/B-ROI-and-Payment-Projection-Example]]
- [[14-analytics/A-Work Summaries/2025-08-09-BuiltByRays Launch Day Work Log & ROI Final]]

<!-- RELATED:END -->