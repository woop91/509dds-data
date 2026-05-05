# Pay Scales — VDE Annual Salary & Overtime Data

> # ⚠️ DATA GAP: 2001–2009 IS NOT INCLUDED ⚠️
>
> Per-employee VDE annual salary and overtime data **does not exist** in this folder for years **2001 through 2009**.
> Public Massachusetts state payroll only starts at **CY 2010** (the launch year of the Comptroller's CTHRU portal).
>
> This is a **hard data limitation**, not an oversight.

## Files in this folder

| File | Coverage | Notes |
|---|---|---|
| `vde-annual-salary-by-employee.csv` | **2010–2023** | One row per (employee, year). Annual rate, regular pay paid, overtime paid, total paid. Latest CTHRU snapshot per row. |
| `vde-annual-salary-aggregates.json` | **2010–2023** | Per-year and per-(year, grade) stats: min, P25, median, mean, P75, max, stdev, mode, sum. Plus IQR outliers + top-5 lists per metric. |
| `vde-grades-extracted.json` | **2024-07-14 → 2026-07-12** | Scheduled bi-weekly chart rates by grade and step (current/future contract period). |
| `effective-YYYY-MM-DD.md` | Single chart per file | Markdown text of each Unit 8 SEIU 509 salary chart (5 charts spanning 2024-07-14 → 2026-07-12). |
| `_salary-compensation-guide.md` | Reference | mass.gov "Salary and Compensation" guide — index of all bargaining unit charts, mileage rates, intern rates, etc. |
| `_raw_cthru_vde_2010-2023.json` | Raw API dump | Reproducibility — re-run `_build_vde_pay.py` to regenerate the CSV/JSON outputs from this. |
| `_build_vde_pay.py` | Build script | Pulls fresh data from CTHRU Socrata API and rebuilds CSV + aggregates JSON. |

## What's missing and why

| Years | Status | Why |
|---|---|---|
| **2001–2009** | **GAP — NOT AVAILABLE PUBLICLY** | CTHRU portal began CY 2010. No predecessor public dataset exists. Verified across MassOpenBooks, OpenTheBooks, Massachusetts Almanac, and Wayback Machine. |
| **2010–2022** | ✅ Complete | Annual snapshots include November or later → `pay_total_actual` ≈ W-2 amount. |
| **2023** | ⚠️ INCOMPLETE | CTHRU's latest snapshot for VDE-MRC is 2023-01-14. `annual_rate` is fine; `actual_paid` and OT sums reflect only ~2 weeks. |
| **2024+** | Not yet published | CTHRU lag — expect 6+ months after CY end. Re-run `_build_vde_pay.py` quarterly to refresh. |

## Three options to address the 2001–2009 gap

You have to pick one of these. There is no fourth.

### (a) PRR — file a Public Records Request with the MA Comptroller
**What you get**: per-employee historical HRCMS extracts (the same fields CTHRU later exposed).
**Cost**: weeks-to-months turnaround, possibly fees.
**Best for**: bargaining-table evidence, members who need real W-2-grade history.
**Template**: build one in `prr-templates/` (parallel to `prr-templates/massability-prr.md`).

### (b) Wayback / CBA scrape — chart-based scheduled rates only
**What you get**: the contract step-rate that VDEs in each grade *should have* been paid each year, derived from old SEIU 509 Unit 8 CBA appendices and historical Unit 8 salary chart PDFs preserved on the Wayback Machine.
**Cost**: a few hours of scraping + PDF extraction.
**Limit**: scheduled, **NOT actual paid**. Cannot produce overtime, cannot show step-progression for any individual person, cannot reveal pay distribution within a year.
**Best for**: "what was the contracted top-step rate in 2003" type questions only.

### (c) Declare the gap acceptable
**What you get**: nothing for 2001–2009; rely on 2010–2023 alone.
**Cost**: zero.
**Best for**: when the storyline only needs to show recent trends (e.g., the 2019→2023 staffing/OT collapse).

See [`docs/methodology.md`](../../docs/methodology.md) "Pre-2010 gap" section for full evidence trail.
