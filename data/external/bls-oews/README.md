# BLS OEWS Data for SOC 13-1031 (Claims Adjusters, Examiners, Investigators)

## Status

**⚠️ MANUAL COMPLETION REQUIRED** — Direct access to BLS.gov is currently blocked. Data files have been initialized with correct column structure. Complete by downloading from BLS manually or via alternative sources.

## Files

### Latest Data (2024)
- **`soc-13-1031-by-state-LATEST.csv`** — State-level wage/employment estimates, SOC 13-1031 (May 2024)
  - Expected rows: 51 (50 states + DC)
  - Columns: state, year, employment, mean_hourly, median_hourly, mean_annual, median_annual, p10, p25, p75, p90
  - Source: https://www.bls.gov/oes/current/oes131031.htm

- **`bls-comparable-occupations-by-state-LATEST.csv`** — Comparison occupations (2024)
  - SOC 13-1041: Compliance Officers
  - SOC 21-1093: Social and Human Service Assistants
  - Expected rows: 102 (51 states/DC × 2 occupations)

### Time Series (2014–Latest)
- **`soc-13-1031-by-state-2014-LATEST.csv`** — Annual state-level data, 10+ years
  - Expected rows: ~510 (51 jurisdictions × 10 years)

### Definitions
- **`soc-13-1031-definition.md`** — Official BLS SOC definition and duty description

## How to Download

### Option 1: BLS Website (Direct)
1. Go to https://www.bls.gov/oes/tables.htm
2. Under "All data," download `all_data_M_2024.zip` (May 2024 OEWS estimates)
3. Extract and find state-level files (e.g., `oesm24.txt` or similar state breakouts)
4. Filter for SOC 13-1031 rows and save to `soc-13-1031-by-state-LATEST.csv`

### Option 2: BLS Archives (By Year)
- https://www.bls.gov/oes/archives/
- For each year 2014–2024:
  - Download the May OEWS state-level data
  - Extract SOC 13-1031 rows and append to `soc-13-1031-by-state-2014-LATEST.csv`

### Option 3: Alternative Data Sources
- **Data.World**: https://data.world/ (search "BLS OEWS")
- **Kaggle**: https://www.kaggle.com/ (search "BLS occupation wage")
- **FRED (St. Louis Fed)**: https://fred.stlouisfed.org/ (limited series, not all state-level)

## Column Definitions

| Column        | Definition                                                   |
|---------------|--------------------------------------------------------------|
| state         | Two-letter state code or "US" for national                  |
| year          | Year of estimate (May survey data published in following yr)|
| employment    | Total employment (rounded to nearest 10)                    |
| mean_hourly   | Mean hourly wage (dollars)                                  |
| median_hourly | Median hourly wage (dollars)                                |
| mean_annual   | Mean annual wage (calculated from hourly)                   |
| median_annual | Median annual wage (calculated from hourly)                |
| p10           | 10th percentile wage (hourly or annual, depending on source)|
| p25           | 25th percentile wage                                         |
| p75           | 75th percentile wage                                         |
| p90           | 90th percentile wage                                         |

## Key Notes

### SOC 13-1031 does NOT distinguish:
- **Insurance adjusters/examiners** (private sector)
- **Government claims examiners** (state DDS, workers' comp boards)

The BLS aggregate includes both. **Massachusetts VDE (Vocational Disability Examiners) classification in state payroll may differ** from BLS national coding.

### Missing State Sub-classification:
BLS does not publish a separate "government claims examiners" subcategory. If arguing reclassification, you'll need to:
1. Compare to SOC 13-1031 private-sector benchmarks
2. Cross-reference Mass. Civil Service occupational codes (HR/CMS)
3. Potentially request custom BLS tabulation for government-only subset (if available)

## Source Metadata

Each CSV file has a corresponding `.source.txt` file with:
- Source URL
- Fetch date (2026-05-05)
- Latest year of data
- Row count

---

**Last Updated:** 2026-05-05  
**For:** 509 DDS data research repository
