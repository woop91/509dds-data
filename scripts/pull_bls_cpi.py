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
    # BLS only returns the M13 annual-average rows when annualaverage is requested.
    payload = {"seriesid": series_ids, "startyear": str(startyear),
               "endyear": str(endyear), "annualaverage": True}
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
        chunk_end = min(yr + 9, end)  # v2 key-free limit: 10 years/request
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
