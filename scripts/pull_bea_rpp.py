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
# Descriptions before trusting the mapping. BEA's actual wording (SARPP) is:
#   'RPPs: All items', 'RPPs: Goods', 'RPPs: Services: Housing',
#   'RPPs: Services: Other', 'RPPs: Services: Utilities'.
# "services: other" (not "other services") is the real needle for other-services;
# "services: utilities" is a real BEA category the tidy schema intentionally does
# not carry, so it is left unmapped (never invented, never collided).
CATEGORY_MAP = [
    ("all items", "rpp_all_items"),
    ("goods", "rpp_goods"),
    ("housing", "rpp_housing"),
    ("services: other", "rpp_other_services"),
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
        # BEA quotes the FIPS inside the cell (e.g. '"00000"'); strip the
        # embedded quote chars so geofips is a bare 5-digit string.
        geofips = (r.get("GeoFips") or r.get("GeoFIPS") or "").strip().strip('"')
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
