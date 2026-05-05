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
| DDS Total Budget | MA Annual Report fiscal tables | 2023–2025 | PRR for earlier years |
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

### DDS-Det Division Total Staff
Sum of CTHRU records matching all DDS-titled position patterns (VDE all grades, Medical Consultants, Medical Review Examiner, Review Examiner, Asst Commissioner DDS, Regional Director DDS, Director Hearings Unit, Dir QA DDS, Dir Training DDS, Director A&F DDS, Fiscal Director DDS, Hearings Director).

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
