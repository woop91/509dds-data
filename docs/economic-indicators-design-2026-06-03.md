# Economic-Context Indicators — Design & Anti-Fabrication Record

**Date:** 2026-06-03 · **Branches:** `main` + `ai-retrieval-index` (identical at `6f58cbd`) · **Status:** approved, executing

Adds three official economic-context datasets requested for the member-facing
dashboards and bargaining materials: **national inflation**, **Massachusetts
inflation** (Boston-metro proxy), and **cost of living by state**. Each follows
the repo's repo-as-database convention: one data file + a sibling
`<file>.meta.json` card conforming to `schemas/dataset.meta.schema.json`, with
`catalog.json` + embeddings regenerated, never hand-edited.

## Why these three exist as designed

| Requested stat | What's actually official | Decision |
|---|---|---|
| National inflation rate | BLS CPI-U, U.S. city average (`CUUR0000SA0`). The "inflation rate" is the year-over-year % change of the annual-average index. | Carry verbatim index **and** computed YoY %. |
| MA inflation rate | **No statewide MA CPI exists.** BLS publishes only the metro series "Boston-Cambridge-Newton, MA-NH" (`CUURS11ASA0`). | Use Boston-metro as the MA proxy, **explicitly labeled** in `geographic_coverage` + `notes`. |
| Cost of living by state | No single official federal index. The authoritative federal source is **BEA Regional Price Parities** (RPP), US=100, all 50 states + DC. (MERIC is C2ER-derived/proprietary → rejected for provenance.) | BEA RPP, table `SARPP`. RPP only starts **2008**, which sets the floor. |

## Datasets

All under `data/external/`.

### 1. `bls-cpi/cpi-u-us-city-average-annual.csv` — National inflation — tier `Computed`
Columns: `year`, `annual_avg_index` (1982-84=100, **verbatim BLS**),
`inflation_rate_pct` (YoY % of annual avg — computed), `deflator_to_latest`
(latest-year index ÷ that year's index; multiply a nominal $ of `year` to express
it in latest-year dollars). Coverage 1999→latest (1999 included only so 2000's
YoY can be computed; first published row is 2000). Card `related` → `pay-scales/*`
with a `notes` worked example of converting VDE pay to real terms.

### 2. `bls-cpi/cpi-u-boston-cambridge-newton-annual.csv` — MA (Boston-metro) inflation — tier `Computed`
Columns: `year`, `annual_avg_index` (**verbatim BLS**), `inflation_rate_pct`
(computed), `boston_minus_national_pct` (Boston rate − national rate, pp; positive
= MA ran hotter). Coverage 2000→latest. `geographic_coverage` and `notes` state
this is the Boston-metro proxy and that no statewide MA CPI exists.

### 3. `bea-rpp/rpp-by-state-2008-2024.csv` — Cost of living by state — tier `Authoritative`
Tidy long: `geofips`, `state`, `year`, `rpp_all_items`, `rpp_goods`,
`rpp_housing`, `rpp_other_services` (all US=100, **verbatim BEA**),
`rpp_all_items_rank` (dense rank within each year, 1 = most expensive; 50 states +
DC, US baseline excluded — **computed, disclosed in `notes`**). Card stays
`Authoritative` because every RPP value is verbatim; only the rank is derived (same
precedent as the existing `bls-oews` card). `notes` surfaces MA's latest-year rank.
Raw BEA file kept verbatim as `bea-rpp/SARPP_STATE_2008_2024.source.csv`
(provenance, un-carded — same pattern as existing `.source.*` files).

## Provenance / honesty guards
- **Reproducible fetch scripts** (mirror `scripts/pull_bls_oews_43_4061.py`):
  - `scripts/pull_bls_cpi.py` — BLS API v2, both CPI series, annual averages
    (`period == M13`); chunks year ranges to stay within the keyless 20-year limit.
  - `scripts/pull_bea_rpp.py` — downloads `https://apps.bea.gov/regional/zip/SARPP.zip`,
    extracts `SARPP_STATE_2008_2024.csv`, emits raw `.source.csv` + tidy CSV.
- No value is hand-typed; all flow from the fetch scripts. Any year a source lacks
  an annual average is left **blank**, never interpolated.
- Access verified 2026-06-03: BLS API key-free OK (national 2024 idx 313.689;
  Boston 2024 idx 336.376); BEA bulk zip key-free OK (contains
  `SARPP_STATE_2008_2024.csv`).

## Regeneration + verification (in order)
1. `python scripts/build_catalog.py` (count 277 → 280)
2. `python scripts/validate_catalog.py` (add tags to `schemas/tags.vocabulary.json`
   only if the validator enforces controlled vocab)
3. `python scripts/compute_value_stats.py` (3 new CSV cards)
4. `python scripts/build_embeddings.py` (`embeddings/index.bin` + `manifest.json`)
5. `pytest` — **must be fully green before any commit**

## Branches, commit, push
Commit on `main`; fast-forward `ai-retrieval-index` to the same commit. Push both
to `origin` (Woop91/509dds-data) once `pytest` is green. README "What's here" +
"Updating" tables updated with the new `data/external/bls-cpi/` and
`data/external/bea-rpp/` rows and their update cadences.
