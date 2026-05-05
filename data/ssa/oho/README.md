# SSA Office of Hearings Operations (OHO) — Public Data

OHO handles the **post-DDS appeal stage**: when a DDS-Det denies a disability
claim, the claimant can request an Administrative Law Judge (ALJ) hearing. OHO
publishes hearing-office-level workload, wait times, and ALJ-level disposition
data. This data joins to DDS-stage workload via state/region, giving a complete
"DDS denial → ALJ outcome" journey per state.

## Files in this directory

| File | Source | Period | Coverage |
|---|---|---|---|
| `alj-disposition-by-judge-LATEST.csv` | `03_ALJ_Disposition_Data.html` | FY 2025 YTD | **1,439 individual ALJs** with hearing office, total dispositions, awards, denials, fully/partially favorable |
| `hearing-office-wait-time-LATEST.csv` | `01_NetStat_Report.html` | FY 2025 YTD | **165 hearing offices** with site code + average wait time in months |
| `03-alj-disposition.tables.json` | (same as above) | (same) | Raw rendered HTML capture (624 KB) — source for the ALJ CSV |
| `01-netstat-report.tables.json` | (same as above) | (same) | Raw rendered HTML capture (35 KB) — source for the wait-time CSV |
| `FIELD_DEFINITIONS.txt` / `AVAILABILITY_SUMMARY.txt` | OHO docs | n/a | Field-by-field meaning + freshness/archive notes |

Source root: https://www.ssa.gov/appeals/DataSets/

## Schema

### `alj-disposition-by-judge-LATEST.csv` (9 columns, 1,439 rows)

```
Judge, Office, Total Dispositions, Total ALJ Dispositions Across All Offices,
Decisions, Awards, Denials, Fully Favorable, Partially Favorable
```

- `Total Dispositions` — disposition count at the ALJ's primary office
- `Total ALJ Dispositions Across All Offices` — disposition count across all
  offices the ALJ heard cases at (often equal to the first column for ALJs not
  hearing remotely)
- `Decisions` = Awards + Denials (excludes dismissals)
- `Fully Favorable` + `Partially Favorable` = Awards (subset breakdown)
- Example MA-relevant rows: `BOSTON` office (7 ALJs)

### `hearing-office-wait-time-LATEST.csv` (3 columns, 165 rows)

```
Site Code, Hearing Office, Hearing Office Times in Months
```

- `Site Code` — internal SSA office identifier (e.g., `T1P` = Akron OH)
- `Hearing Office Times in Months` — average wait from request-for-hearing to
  hearing held, current period

## How this joins to DDS-stage data

Hearing offices serve geographic regions but are not 1:1 with states. To attach
state to each office:

1. The OHO datasets index page lists each office's coverage region. (As of the
   May 2026 fetch, the index page itself is bot-blocked from this environment;
   see `../../MANUAL-FETCH-NEEDED.md`.)
2. Office naming convention: most cities map to their state via standard
   geocoding (e.g., `BOSTON` → MA, `AKRON OH` → OH suffix). For ambiguous codes,
   cross-reference SSA's hearing-office-locator page.

## Refresh

OHO publishes monthly. To refresh:

```
NODE_PATH=scripts/.npm/node_modules node scripts/playwright-fetch.js
node scripts/extract-oho-alj-table.js
```

Both scripts are idempotent. The Playwright fetch overwrites the JSON captures;
the extractor overwrites the CSVs.

## Caveats

- **ALJ table is national, not state-aggregated.** To produce a per-state
  allowance rate at the ALJ stage, group rows by office state, then divide
  `Awards` ÷ `Decisions`.
- **Wait-time table is current-period snapshot, not time series.** OHO publishes
  monthly archives going back to FY 2011 — see the index page for archive URLs.
- **Some ALJs have very low caseloads** (1–7 dispositions). Filter by
  `Decisions >= 50` for stable allowance-rate comparisons.
