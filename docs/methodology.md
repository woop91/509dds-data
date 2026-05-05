# Methodology & Data Caveats

## Year conventions (read this first)

Three different "year" conventions appear across sources. They don't align perfectly:

| Convention | Span | Where it appears |
|---|---|---|
| **Calendar Year (CY)** | Jan 1 – Dec 31 | CTHRU payroll data |
| **Federal Fiscal Year (FFY)** | Oct 1 – Sep 30 | SSA-SA-FYWL.csv, DDS-Net-Accuracy.csv |
| **MA State Fiscal Year (SFY)** | Jul 1 – Jun 30 | MA annual reports, MA legislative budgets |

For the master DDS Statistics table, the year column is **federal FY** (verified by exact match between SSA FYWL data and the user's spreadsheet for 2013–2020 initial-claim counts). However, MA-specific MA-report values (FY24 = 60,305 receipts) reflect MA state FY24 (Jul 2023 – Jun 2024). These overlap ~75%; small variance is expected.

## Sources by metric (with confidence levels)

| Metric | Authoritative source | Years available | Notes |
|---|---|---|---|
| Total Receipts | MA Section 9F reports (PRR for pre-2023) | 2013–2024 (gaps) | Includes initial + recon + CDR + hearings |
| Total Dispositions | MA Section 9F reports | 2013–2024 (gaps) | Same scope |
| Initial Claims Filed | SSA-SA-FYWL.csv (Adult+Child Receipts) | 2001–2024 | Federal FY |
| Initial Claims Disposed | SSA-SA-FYWL.csv (All Determinations) | 2001–2024 | Federal FY |
| % Allowed | SSA-SA-FYWL.csv (Favorable Determination Rate) | 2001–2024 | Federal FY |
| CDR Receipts/Dispositions | MA Section 9F reports | 2013–2024 (gaps) | PRR for missing years |
| CE Purchased / Rate | MA Section 9F reports | 2013–2024 (gaps) | Rate computed = Purchased ÷ Total Dispositions |
| MER Purchased / Rate | MA Section 9F reports | 2013–2024 (gaps) | Rate computed = Purchased ÷ Total Dispositions |
| DDS Accuracy | DDS-Net-Accuracy.csv (federal QA) | 2007–2022 | Plus 2023–2025 from MA reports |
| Federal Accuracy Standard | SSA program docs / MA reports | All years | 90% (1990s) → 90.6% (2010s) → 95% (2023+) |
| Cost Per Case | MA Section 9F reports | 2013–2024 (gaps) | Methodology may differ between years (per-disposition vs per-case) |
| DDS Total Budget (state-level) | MA Annual Report fiscal tables | 2023–2025 | PRR for earlier years. **Note: SSA-side per-state DDS budget allocations are structurally unpublished — see "DDS budget visibility" below.** |
| % Federal Funding | SSA program documentation | All years | 100% by statute |
| Homeless Cases (count) | MA Section 9F reports | None publicly available | PRR — count, not rate |
| VDE / DDS Staff | CTHRU payroll | 2010–2023 | Calendar year basis; SAOR FTE counts may differ |

## SSA SAOR vs CTHRU staffing (read carefully)

Two different staffing data sources exist with different methodologies:

| Source | What it counts | Consequence |
|---|---|---|
| **SSA SAOR** (State Agency Operations Report — internal SSA) | FTE-authorized examiner positions | More stable year-over-year; reflects budget decisions |
| **CTHRU** (MA Comptroller payroll) | Payroll records per calendar year | Inflated when employees change positions mid-year (one person → two records); reflects actual paid headcount |

Example: For CY 2010, SAOR-style data shows VDE-MA = 189 (per the master spreadsheet). CTHRU shows 246 records matching VDE titles. The 57-employee gap is methodology, not a real discrepancy.

**For continuity with prior 509 data, use SAOR conventions.** CTHRU is best for: (a) year-over-year *trends*, (b) verifying directional shifts, (c) cross-checking via paid-out salary distributions.

## Computed metrics (derivations)

### Consultative Examination Rate
```
CE Rate = CE Purchased ÷ Total Dispositions
```
Verified against 2013: 20,534 ÷ 85,854 = 23.92% → matches published 23.90%.

### Medical Evidence of Record Rate
```
MER Rate = MER Purchased ÷ Total Dispositions
```
Verified against 2013: 77,472 ÷ 85,854 = 90.24% → matches published 90.2%.

### Annual VDE Salary Estimate
```
Annual estimate = Bi-weekly rate × 26 pay periods
```
Verified against CTHRU CY 2023 actual paid amounts (see `data/pay-scales/vde-grades-extracted.json`).

### Per-Employee VDE Annual Salary (CTHRU 2010–2023)
File: `data/pay-scales/vde-annual-salary-by-employee.csv`
Aggregates: `data/pay-scales/vde-annual-salary-aggregates.json`

Pulled from CTHRU dataset `rxhc-k6iz` with filter `chris='MRC' AND upper(position_title) LIKE '%DISAB EXAMINER%'`.

**Key methodology point**: `rxhc-k6iz` is a *per-pay-period snapshot* table, not an annual roll-up. Each (employee, year) typically has multiple rows — one per pay period the snapshot caught. To produce per-employee annual figures we **dedupe to the latest `service_end_date` per (year, employee)**. The latest snapshot's `pay_year_to_date` ≈ that employee's W-2 earnings for the year (regular + overtime + other + buyout).

Field meanings:
- `annual_rate` — scheduled annualized base rate at last snapshot. Independent of how much they actually got paid.
- `pay_base_actual` — regular pay actually paid YTD as of last snapshot.
- `pay_overtime_actual` — overtime pay actually paid YTD.
- `pay_other_actual` — stipends, differentials, etc.
- `pay_buyout_actual` — vacation/comp-time buyouts.
- `pay_total_actual` = sum of the four above.

Outlier detection in aggregates JSON uses Tukey IQR fences (Q1−1.5·IQR, Q3+1.5·IQR) plus an unconditional top-5 list per metric per year.

### CY 2023 incompleteness flag (CRITICAL)
The latest CTHRU snapshot date in the public dataset for VDE-MRC records is **2023-01-14**. CY 2023's `pay_total_actual` and overtime sums therefore reflect only ~2 weeks of pay, not a full year. Compare 2023 to prior years using `annual_rate` only; `actual_paid` and OT figures for 2023 are NOT comparable. The aggregates JSON marks this with `year_data_completeness[year].approximates_full_year=false`.

### Pre-2010 gap (no public per-employee data)
Per-employee MA state payroll data is **not publicly available for years 2001–2009.** Verified across:
- MA Comptroller CTHRU (starts CY 2010)
- MassOpenBooks (sources from Comptroller; same start)
- OpenTheBooks (sources from CTHRU)
- Massachusetts Almanac salary index (no pre-2010 link present)
- Wayback Machine on mass.gov payroll URLs (no archived predecessor)

Three options to address the gap (pick one — there is no fourth):

- **(a) PRR** — file a MA Public Records Request with the Office of the Comptroller for archival HRCMS extracts. Slow (weeks-to-months), may incur fees. Yields per-employee historical data comparable to CTHRU columns.
- **(b) Wayback / CBA scrape (chart-based, not actual paid)** — pull old SEIU 509 Unit 8 salary chart PDFs from the Wayback Machine and reconstruct *scheduled* (contract) rates. Note: chart-based, **not actual paid**. Cannot produce overtime data. Cannot show step-progression for any individual person.
- **(c) Declare the gap acceptable** — accept that pre-2010 individual VDE pay is not knowable without a PRR and proceed with 2010–2023 only.

If the gap is filled via (a) or (b), write into `data/pay-scales/vde-annual-salary-by-employee-2001-2009.csv` with the same column layout, plus a `source` column noting `PRR-2026-XX` or `CBA-YYYY-YYYY-Appendix-A`.

### DDS-Det Division Total Staff
Sum of CTHRU records matching all DDS-titled position patterns (VDE all grades, Medical Consultants, Medical Review Examiner, Review Examiner, Asst Commissioner DDS, Regional Director DDS, Director Hearings Unit, Dir QA DDS, Dir Training DDS, Director A&F DDS, Fiscal Director DDS, Hearings Director).

## DDS budget visibility (federal vs state)

Per-state DDS budget allocations are **not published** by SSA. Verified by the
FY25 Congressional Justification extract at
[`data/ssa/budget/cj-fy25-extracted.md`](../data/ssa/budget/cj-fy25-extracted.md):

- SSA's CJ publishes DDS funding at the **national level only** (FY25:
  13,555 work-years, ~$2.6B total)
- ODD (Office of Disability Determinations) further allocates these funds to
  individual DDSs, but those internal allocations are not in any public
  congressional or annual-report document
- State-level operating budgets that *are* published (e.g., MA Annual Report)
  show the state's total DDS spending — but that's the state's own fiscal
  reporting, not a federal allocation breakdown

**Implication for the master statistics table:** cells under
`dds_total_budget_per_state_year` for years/states where there's no MA Annual
Report equivalent are not retrievable via web fetch *or* state PRR — they would
require a federal FOIA to SSA. This is a stronger gate than the PRR templates
in `prr-templates/` are designed for. Until/unless a federal FOIA is filed,
treat these cells as **structurally unavailable**, not "PRR-pending."

## Known data quality flags

- **2016 reclassification year**: VDE A/B/C/D titles were renamed to VDE I/II/III. CTHRU records show some employees under both naming conventions in 2016, inflating raw counts. Use ~190–200 VDE / ~310 DDS staff as the corrected estimate.
- **2022 % Allowed = 57%**: MA-published value diverges sharply from SSA FYWL FY2022 = 46.76% combined. Origin unknown — verify against original Section 9F report before publishing trend charts.
- **PRR cells**: marked explicitly in `dds-statistics-master-table.json`. Do NOT silently coerce to NULL or 0.
- **2024 cost-per-case**: MA-published $1,071 vs. arithmetic estimate of $840 ($50.8M ÷ 60,453 dispositions). Methodology divergence; use MA's published figure.
- **DDS Accuracy 2014 mismatch**: MA report shows 96.7%; SSA federal QA shows 98.1%. State internal QA vs federal QA may use different sampling.
- **CTHRU update lag**: latest year is 2023 as of 2026-05. CY 2024 data expected mid-2025. CY 2025 expected mid-2026.

## Data freshness

| File | Updated | Re-fetch instructions |
|---|---|---|
| MA annual reports | Annual (Sep–Nov of following year) | Refetch from mass.gov when new year drops |
| SSA-SA-FYWL.csv | Annual (~Nov) | `firecrawl scrape https://www.ssa.gov/disability/data/SSA-SA-FYWL.csv --format rawHtml` |
| DDS-Net-Accuracy.csv | Annual | Same pattern |
| CDP-Time-Monthly.csv | Monthly | Same pattern |
| CTHRU staffing | Quarterly | Re-query Socrata API |
| Salary charts | When new effective date drops | Watch mass.gov/guides/salary-and-compensation |
| CBA | Every 2-3 years | Watch mass.gov for next contract signing |
