# Economic-Context Indicators Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three official economic-context datasets to `509dds-data` (both `main` and `ai-retrieval-index`): national inflation (BLS CPI-U), MA inflation (BLS Boston-metro CPI proxy), and cost of living by state (BEA Regional Price Parities) — each as a data file + `.meta.json` card, with `catalog.json`/`llms.txt`/value-stats/embeddings regenerated and all CI `--check` gates + `pytest` green.

**Architecture:** Two reproducible fetch scripts pull from key-free public sources (BLS API v2, BEA bulk zip) and emit CSVs into `data/external/bls-cpi/` and `data/external/bea-rpp/`. Hand-authored `.meta.json` cards describe each CSV. The repo's whole-repo regenerators rebuild the indexes. Verification is the four CI `--check` gates + `pytest` + first-hand value spot-checks against the live sources.

**Tech Stack:** Python 3.12 (`requests`, `numpy`, `fastembed`, `jsonschema` — all present), the repo's existing `scripts/*.py` toolchain.

**Source spec & anti-fabrication record:** `docs/economic-indicators-design-2026-06-03.md`.

**Repo (orchestrator-only) constraints — DO NOT delegate git to subagents:**
- Work happens on branch `feat/economic-indicators` cut from `main`. After green, fast-forward `main`, then `git branch -f ai-retrieval-index main`; push both to `origin`.
- `git add` **explicit paths only** (never `-A`/`.`): `node_modules/` is untracked-and-unignored.
- Untracked non-ours (`prr-templates/ma-comptroller-payroll-prr.md(+.meta.json)`, `prr-templates/ma-hrd-classification-prr.md(+.meta.json)`, `prr-templates/massability-dds-prr.md(+.meta.json)`, `prr-templates/ssa-foia-ma-dds.md(+.meta.json)`, `docs/records-request-gap-analysis.md`) are **isolated out of the tree before regenerating artifacts and restored after** — never committed.

---

### Task 0: Isolate concurrent-session untracked files (orchestrator)

**Files:** none created; move 9 untracked paths to a backup outside the repo.

- [ ] **Step 1:** Record current untracked state: `git status -sb` and save the list.
- [ ] **Step 2:** Move the 8 `prr-templates/*` files + `docs/records-request-gap-analysis.md` to `C:\Users\deskc\Documents\509dds-data.isolated-2026-06-03\` (preserving relative paths). Leave `node_modules/` in place (not scanned by build scripts; never added).
- [ ] **Step 3:** Verify `git status -sb` now shows a clean tree except `docs/economic-indicators-design-2026-06-03.md`, `docs/superpowers/`. Confirm `python scripts/build_catalog.py --check` reports up to date at **277** (proves isolation worked — no stray sidecars swept in).

### Task 1: BLS CPI fetch script

**Files:**
- Create: `scripts/pull_bls_cpi.py`
- Create (output): `data/external/bls-cpi/cpi-u-us-city-average-annual.csv`
- Create (output): `data/external/bls-cpi/cpi-u-boston-cambridge-newton-annual.csv`

- [ ] **Step 1: Write the script** (mirrors `scripts/pull_bls_oews_43_4061.py` conventions — `requests`, optional `BLS_API_KEY`, polite chunking):

```python
"""Pull BLS CPI-U annual-average indexes and derive inflation rates.

Two series (BLS Public Data API v2, key-free; BLS_API_KEY used if set):
  CUUR0000SA0   CPI-U, U.S. city average, all items, NSA  -> national
  CUURS11ASA0   CPI-U, Boston-Cambridge-Newton, MA-NH, all items, NSA -> MA proxy

Annual averages are the `period == "M13"` rows. The "inflation rate" is the
year-over-year % change of the annual-average index. We fetch from 1999 so the
year-2000 rate is computable; output rows start at 2000. Any year lacking an
annual average is left blank — never interpolated.

Outputs:
  data/external/bls-cpi/cpi-u-us-city-average-annual.csv
      year, annual_avg_index, inflation_rate_pct, deflator_to_latest
  data/external/bls-cpi/cpi-u-boston-cambridge-newton-annual.csv
      year, annual_avg_index, inflation_rate_pct, boston_minus_national_pct
"""
from __future__ import annotations

import csv
import datetime
import os
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "data" / "external" / "bls-cpi"
API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
API_KEY = os.environ.get("BLS_API_KEY")
NATIONAL = "CUUR0000SA0"
BOSTON = "CUURS11ASA0"
START_YEAR = 1999  # base year for the 2000 YoY rate; not emitted


def _post(series_ids, startyear, endyear):
    payload = {"seriesid": series_ids, "startyear": str(startyear), "endyear": str(endyear)}
    if API_KEY:
        payload["registrationkey"] = API_KEY
    r = requests.post(API_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS API error: {data.get('status')} {data.get('message')}")
    return data


def annual_index(series_id, start, end):
    """Return {year:int -> annual_avg_index:float} for M13 rows, chunked <=20yr."""
    out = {}
    yr = start
    while yr <= end:
        chunk_end = min(yr + 19, end)  # v2 key-free limit: 20 years/request
        data = _post([series_id], yr, chunk_end)
        for s in data["Results"]["series"]:
            for row in s.get("data", []):
                if row.get("period") == "M13":  # annual average
                    try:
                        out[int(row["year"])] = float(row["value"])
                    except (TypeError, ValueError):
                        pass
        yr = chunk_end + 1
    return out


def yoy(idx, year):
    a, b = idx.get(year), idx.get(year - 1)
    if a is None or b is None or b == 0:
        return None
    return round((a / b - 1.0) * 100.0, 2)


def main() -> int:
    if not API_KEY:
        print("Note: BLS_API_KEY not set — using key-free quota.", file=sys.stderr)
    this_year = datetime.date.today().year
    nat = annual_index(NATIONAL, START_YEAR, this_year)
    bos = annual_index(BOSTON, START_YEAR, this_year)
    if not nat:
        raise SystemExit("no national annual data returned")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest = max(nat)
    nat_years = [y for y in sorted(nat) if y >= 2000]

    nat_csv = OUT_DIR / "cpi-u-us-city-average-annual.csv"
    with nat_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "annual_avg_index", "inflation_rate_pct", "deflator_to_latest"])
        for y in nat_years:
            idx = nat[y]
            defl = round(nat[latest] / idx, 4) if idx else ""
            w.writerow([y, idx, yoy(nat, y) if yoy(nat, y) is not None else "", defl])

    bos_csv = OUT_DIR / "cpi-u-boston-cambridge-newton-annual.csv"
    with bos_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "annual_avg_index", "inflation_rate_pct", "boston_minus_national_pct"])
        for y in [y for y in sorted(bos) if y >= 2000]:
            idx = bos[y]
            b_rate, n_rate = yoy(bos, y), yoy(nat, y)
            gap = round(b_rate - n_rate, 2) if (b_rate is not None and n_rate is not None) else ""
            w.writerow([y, idx, b_rate if b_rate is not None else "", gap])

    print(f"national rows {len(nat_years)} (latest {latest}); boston rows "
          f"{len([y for y in bos if y >= 2000])}; deflator base {latest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it** — `python scripts/pull_bls_cpi.py`. Expected: prints national/boston row counts and latest year (≥2024).
- [ ] **Step 3: First-hand verify** the data is real, not fabricated: confirm `cpi-u-us-city-average-annual.csv` 2024 `annual_avg_index` ≈ **313.689** and Boston 2024 ≈ **336.376** (matches the live-API probe). Spot-check one computed `inflation_rate_pct` by hand (e.g. 2024 national = 313.689/304.702−1 ≈ 2.95%).

### Task 2: BEA RPP fetch script

**Files:**
- Create: `scripts/pull_bea_rpp.py`
- Create (output): `data/external/bea-rpp/SARPP_STATE_2008_2024.source.csv` (verbatim, un-carded)
- Create (output): `data/external/bea-rpp/rpp-by-state-2008-2024.csv`

- [ ] **Step 1: Write the script** (key-free bulk download; maps categories by Description text — never hardcode line-code meanings):

```python
"""Pull BEA Regional Price Parities by state (cost of living, US=100).

Source: https://apps.bea.gov/regional/zip/SARPP.zip  (key-free bulk download)
        -> SARPP_STATE_2008_2024.csv  (table SARPP, state level, 2008-2024)

Emits a verbatim provenance copy and a tidy long CSV. Category columns are
mapped from the Description text (not assumed from numeric LineCodes); any
category not present is left blank. rpp_all_items_rank is a per-year dense rank
over the 50 states + DC (US baseline excluded; US row rank blank).
"""
from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "data" / "external" / "bea-rpp"
ZIP_URL = "https://apps.bea.gov/regional/zip/SARPP.zip"
MEMBER = "SARPP_STATE_2008_2024.csv"

# Description-substring -> tidy column. Verified against the file's distinct
# Descriptions in Step 2 before trusting the mapping.
CATEGORY_MAP = [
    ("all items", "rpp_all_items"),
    ("goods", "rpp_goods"),
    ("housing", "rpp_housing"),
    ("other services", "rpp_other_services"),
]


def category_for(description: str):
    d = (description or "").lower()
    for needle, col in CATEGORY_MAP:
        if needle in d:
            return col
    return None


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(ZIP_URL, timeout=120)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        raw = z.read(MEMBER).decode("utf-8-sig")
    (OUT_DIR / "SARPP_STATE_2008_2024.source.csv").write_text(raw, encoding="utf-8")

    rows = list(csv.DictReader(io.StringIO(raw)))
    # year columns are the 4-digit headers present in the file
    year_cols = [c for c in rows[0].keys() if c.strip().isdigit() and len(c.strip()) == 4]
    years = [int(c) for c in year_cols]

    # nested: data[(geofips, geoname)][year][tidy_col] = value
    data: dict = {}
    for r in rows:
        geofips = (r.get("GeoFips") or r.get("GeoFIPS") or "").strip()
        geoname = (r.get("GeoName") or "").strip()
        col = category_for(r.get("Description", ""))
        if not col or not geofips:
            continue
        slot = data.setdefault((geofips, geoname), {y: {} for y in years})
        for yc, y in zip(year_cols, years):
            v = (r.get(yc) or "").strip()
            try:
                slot[y][col] = float(v)
            except ValueError:
                slot[y][col] = None  # BEA uses (NA)/(NM) sentinels

    # per-year dense rank of rpp_all_items over states+DC (exclude US 00000)
    rank: dict = {y: {} for y in years}
    for y in years:
        vals = [((gf, gn), data[(gf, gn)][y].get("rpp_all_items"))
                for (gf, gn) in data if gf != "00000"]
        vals = [(k, v) for k, v in vals if v is not None]
        for pos, (k, _v) in enumerate(sorted(vals, key=lambda kv: -kv[1]), start=1):
            rank[y][k] = pos

    out = OUT_DIR / "rpp-by-state-2008-2024.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["geofips", "state", "year", "rpp_all_items", "rpp_goods",
                    "rpp_housing", "rpp_other_services", "rpp_all_items_rank"])
        for (gf, gn) in sorted(data, key=lambda k: (k[0] != "00000", k[1])):
            for y in years:
                cell = data[(gf, gn)][y]
                def g(c):
                    v = cell.get(c)
                    return "" if v is None else v
                rk = rank[y].get((gf, gn), "")
                w.writerow([gf, gn, y, g("rpp_all_items"), g("rpp_goods"),
                            g("rpp_housing"), g("rpp_other_services"), rk])

    print(f"states+US rows: {len(data)}; years {min(years)}-{max(years)}; "
          f"MA latest rank: {rank[max(years)].get(('25000','Massachusetts'),'?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run + verify mapping** — `python scripts/pull_bea_rpp.py`. BEFORE trusting category columns, print the file's distinct `Description` values and confirm `CATEGORY_MAP` covers them (adjust needles if BEA's wording differs). Expected: 52 geos (US + 50 states + DC), years 2008-2024, MA latest rank printed.
- [ ] **Step 3: First-hand verify** — confirm the `United States` row `rpp_all_items` is `100.0` for every year (BEA baseline), and MA's `rpp_all_items` is plausibly >100 (high cost of living). Spot-check one value against the verbatim `.source.csv`.

### Task 3: Author the three `.meta.json` cards

**Files:**
- Create: `data/external/bls-cpi/cpi-u-us-city-average-annual.csv.meta.json`
- Create: `data/external/bls-cpi/cpi-u-boston-cambridge-newton-annual.csv.meta.json`
- Create: `data/external/bea-rpp/rpp-by-state-2008-2024.csv.meta.json`

Required fields: `id,title,description,path,format,source(publisher,url),confidence_tier`. Include `columns` (name+type from enum `integer|number|string|...`), `temporal_coverage`, `geographic_coverage`, `update_cadence`, `tags` (canonical: lowercase/sorted), `notes`, and `related` where relevant. Match the compact style of `data/external/bls-oews/soc-13-1031-definition.md.meta.json`.

- [ ] **Step 1:** National CPI card — `confidence_tier: "Computed"`; columns `year`(integer), `annual_avg_index`(number), `inflation_rate_pct`(number), `deflator_to_latest`(number); source publisher "U.S. Bureau of Labor Statistics (CPI)", url `https://data.bls.gov/timeseries/CUUR0000SA0`; `update_cadence` "Annual (BLS publishes annual averages each January)"; `notes` stating the index is verbatim BLS and the rate/deflator are computed (standard YoY; deflator base = latest year); `related` to the pay-scales datasets with a real-terms usage example; tags e.g. `["authoritative-source","bls","computed","cost-of-living","cpi","inflation","national","time-series"]`.
- [ ] **Step 2:** Boston-metro CPI card — `confidence_tier: "Computed"`; columns `year`(integer), `annual_avg_index`(number), `inflation_rate_pct`(number), `boston_minus_national_pct`(number); `geographic_coverage` "Boston-Cambridge-Newton, MA-NH metropolitan area (BLS proxy for Massachusetts — no statewide MA CPI is published)"; source url `https://data.bls.gov/timeseries/CUURS11ASA0`; `notes` the no-statewide-CPI caveat + gap-column meaning; tags include `bls,cpi,inflation,massachusetts,boston,computed`.
- [ ] **Step 3:** BEA RPP card — `confidence_tier: "Authoritative"`; columns `geofips`(string), `state`(string), `year`(integer), `rpp_all_items`(number), `rpp_goods`(number), `rpp_housing`(number), `rpp_other_services`(number), `rpp_all_items_rank`(integer); `geographic_coverage` "United States — 50 states + DC (+ US=100 baseline row)"; `temporal_coverage {start:"2008",end:"2024"}`; source publisher "U.S. Bureau of Economic Analysis", title "Regional Price Parities by State (SARPP)", url `https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area`; `update_cadence` "Annual (~December)"; `derived_from` referencing the `.source.csv`; `notes` that all RPP values are verbatim BEA (US=100), `rpp_all_items_rank` is computed (per-year dense rank over states+DC, US excluded), and MA's latest-year rank; tags `["authoritative-source","bea","cost-of-living","rpp","states","time-series"]`.
- [ ] **Step 4 (optional housekeeping):** add any genuinely new canonical tags to `schemas/tags.vocabulary.json` in its existing style (no test gates this; skip if it complicates).

### Task 4: Regenerate indexes + README

**Files:** Modify `catalog.json`, `llms.txt`, the 3 card files (value-stats), `embeddings/index.bin`, `embeddings/manifest.json`, `README.md`.

- [ ] **Step 1:** `python scripts/compute_value_stats.py` → fills per-column stats + row_count into the 3 new CSV cards.
- [ ] **Step 2:** `python scripts/build_catalog.py` → catalog.json (277 → **280**) + llms.txt.
- [ ] **Step 3:** `python scripts/build_embeddings.py` → embeddings/index.bin + manifest.json (280 vectors).
- [ ] **Step 4:** Edit `README.md` — add `data/external/bls-cpi/` + `data/external/bea-rpp/` rows to the "What's here" table and the two CPI series + BEA RPP to the "Updating" cadence table.

### Task 5: Verify all gates green (mirror CI exactly)

- [ ] **Step 1:** `python scripts/validate_catalog.py --strict` → `errors: 0` (no missing sidecars).
- [ ] **Step 2:** `python scripts/compute_value_stats.py --check` → "value-stats current".
- [ ] **Step 3:** `python scripts/build_catalog.py --check` → "up to date (280 datasets)".
- [ ] **Step 4:** `python scripts/build_embeddings.py --check` → "up to date (280 cards embedded)".
- [ ] **Step 5:** `python -m pytest -q` → all pass (integration test may skip).

### Task 6: Commit to both branches + push (orchestrator)

- [ ] **Step 1:** `git checkout -b feat/economic-indicators` (from main).
- [ ] **Step 2:** `git add` **explicit paths**: the 2 scripts, the 5 data files (2 CPI csv + bea source csv + bea tidy csv... note .source.csv IS committed as provenance), the 3 card files, `catalog.json`, `llms.txt`, `embeddings/index.bin`, `embeddings/manifest.json`, `README.md`, `schemas/tags.vocabulary.json` (if edited), `docs/economic-indicators-design-2026-06-03.md`, `docs/superpowers/plans/2026-06-03-economic-indicators.md`. Then `git status` to confirm nothing stray (no node_modules, no prr-templates) is staged.
- [ ] **Step 3:** Commit: `feat(external): add national + MA inflation (BLS CPI) and cost-of-living-by-state (BEA RPP)`.
- [ ] **Step 4:** `git checkout main && git merge --ff-only feat/economic-indicators`; then `git branch -f ai-retrieval-index main`.
- [ ] **Step 5:** `git push origin main ai-retrieval-index`.
- [ ] **Step 6:** Restore the Task-0 isolated files back into the working tree.
- [ ] **Step 7:** Report final SHAs + CI status.

---

## Self-Review
- **Spec coverage:** national inflation (Task 1+3.1), MA inflation proxy (Task 1+3.2), cost of living by state (Task 2+3.3), 3 extras — deflator (3.1), Boston-minus-national (1/3.2), RPP rank (2/3.3) — all present; regenerate + verify (Tasks 4-5); both branches + push (Task 6); concurrent-file isolation (Task 0). ✓
- **Placeholders:** none — full script code given; card fields enumerated with exact types/tiers/urls.
- **Type consistency:** column names in the cards (Task 3) match the CSV headers emitted by the scripts (Tasks 1-2) exactly; `dataset_count` 277→280 consistent across Tasks 4-5.
