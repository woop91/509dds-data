"""Pull BLS OEWS state-level wage estimates for SOC 43-4061
("Eligibility Interviewers, Government Programs"), the cross-state benchmark
for state DDS examiner pay.

Uses the BLS Public Data API v2 (https://www.bls.gov/developers/) which
requires a registered key for unlimited daily queries. Without a key, the
API allows 25 series/day and 10 years/query — adequate for one run, so the
script falls back gracefully if BLS_API_KEY is unset.

Output:
  data/external/bls-oews/oews-43-4061-state.json
  data/pay-scales/peer-states/bls-oews-43-4061.json    (rewritten)
  data/pay-scales/peer-states/bls-oews-43-4061.md      (human-readable)

Series ID format (OEWS):
  OEU{area_code}{industry_code}{occupation_code}{datatype_code}
  area_code        = "S" + 2-digit FIPS state code (e.g., S25 for MA)
                     "N" + 7-digit national area  (N0000000 for US national)
  industry_code    = 000000 for cross-industry (all NAICS)
  occupation_code  = 6-digit SOC, no dash (434061)
  datatype_code    = 01=employment, 02=hourly mean wage, 04=annual mean wage,
                     07=hourly P10, 08=hourly P25, 09=hourly median, 10=hourly P75,
                     11=hourly P90, 12=annual P10, 13=annual P25, 14=annual median,
                     15=annual P75, 16=annual P90
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
PEER_STATES = Path(REPO / "data/pay-scales/peer-states")
EXTERNAL_DIR = Path(REPO / "data/external/bls-oews")

API_KEY = os.environ.get("BLS_API_KEY")
API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

STATES = {
    "MA": "25", "TN": "47", "AZ": "04", "IN": "18", "MD": "24",
    "VA": "51", "WA": "53", "MO": "29", "WI": "55",
    "NY": "36", "CA": "06", "OR": "41", "MN": "27",
    "NJ": "34", "CT": "09", "HI": "15",
    "NV": "32", "IL": "17", "MI": "26", "PA": "42",
    "AK": "02", "MT": "30", "ME": "23", "VT": "50",
}

# We pull annual mean (04) + annual P10/P25/P50/P75/P90 (12-16) per state +
# national. That's 7 datatypes × ~25 areas = ~175 series. Within the 50/day
# limit if API_KEY is set, well under daily anonymous quota for one run.
DATATYPES = {
    "annual_mean": "04",
    "annual_p10": "12",
    "annual_p25": "13",
    "annual_median": "14",
    "annual_p75": "15",
    "annual_p90": "16",
    "employment": "01",
}

OCC = "434061"


def series_id(area_code: str, datatype: str) -> str:
    """Build OEWS series ID. area_code includes the leading S/N prefix."""
    return f"OEU{area_code}000000{OCC}{datatype}"


def state_area(fips: str) -> str:
    return f"S{fips}0000"  # state-level OEWS area code


def national_area() -> str:
    return "N0000000"  # US-national area code


def _post(payload: dict) -> dict:
    if API_KEY:
        payload["registrationkey"] = API_KEY
    resp = requests.post(API_URL, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def fetch_for_areas(areas: dict[str, str]) -> dict[str, dict]:
    """Fetch all DATATYPES for each area in the given mapping.

    `areas` is {label: area_code} where label is e.g. "MA" or "US",
    area_code is the BLS area string with the S/N prefix already applied.
    """
    out: dict[str, dict] = {label: {} for label in areas}
    series_ids = []
    id_to_target: list[tuple[str, str, str]] = []
    for label, area in areas.items():
        for dt_label, dt_code in DATATYPES.items():
            sid = series_id(area, dt_code)
            series_ids.append(sid)
            id_to_target.append((sid, label, dt_label))

    # BLS API allows up to 50 series per request with a registered key,
    # 25 without. Chunk to be safe.
    chunk = 25
    for i in range(0, len(series_ids), chunk):
        batch = series_ids[i : i + chunk]
        payload = {"seriesid": batch, "startyear": "2024", "endyear": "2024"}
        try:
            resp = _post(payload)
        except Exception as exc:
            print(f"BLS API error on chunk {i // chunk}: {exc}", file=sys.stderr)
            continue
        if resp.get("status") != "REQUEST_SUCCEEDED":
            print(f"BLS API non-success: {resp.get('status')} -- {resp.get('message')}", file=sys.stderr)
            continue
        for series in resp.get("Results", {}).get("series", []):
            sid = series["seriesID"]
            label, dt_label = next(((l, d) for s, l, d in id_to_target if s == sid), (None, None))
            if not label:
                continue
            data = series.get("data", [])
            if data:
                # OEWS publishes a single annual datapoint per series
                value = data[0].get("value")
                try:
                    out[label][dt_label] = float(value) if value not in ("", "-") else None
                except (TypeError, ValueError):
                    out[label][dt_label] = None
            else:
                out[label][dt_label] = None
        time.sleep(1)  # be polite to BLS

    return out


def write_outputs(data: dict[str, dict]) -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    PEER_STATES.mkdir(parents=True, exist_ok=True)

    pay_data = {
        "$comment": (
            "BLS OEWS SOC 43-4061 'Eligibility Interviewers, Government Programs' — "
            "cross-state benchmark for DDS examiner-equivalent role. NOTE: this SOC "
            "includes eligibility interviewers for non-disability programs (TANF, SNAP, "
            "Medicaid, etc.), so it OVER-broadens vs. true disability-only examiner work."
        ),
        "soc_code": "43-4061",
        "soc_title": "Eligibility Interviewers, Government Programs",
        "reference_period": "May 2024",
        "source_api": API_URL,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "national": data.get("US", {}),
        "states": {k: v for k, v in data.items() if k != "US"},
    }
    out_json = EXTERNAL_DIR / "oews-43-4061-state.json"
    out_json.write_text(json.dumps(pay_data, indent=2), encoding="utf-8")

    # Mirror to peer-states folder for direct cross-link from peer-states-pay-summary
    (PEER_STATES / "bls-oews-43-4061.json").write_text(
        json.dumps(pay_data, indent=2), encoding="utf-8"
    )

    # Write the human-readable markdown sorted by mean annual
    rows = []
    ma_mean = (data.get("MA") or {}).get("annual_mean")
    for label, vals in sorted(
        data.items(),
        key=lambda kv: (-1 if kv[0] == "US" else (kv[1].get("annual_mean") or 0)),
        reverse=True,
    ):
        mean = vals.get("annual_mean")
        median = vals.get("annual_median")
        emp = vals.get("employment")
        diff_vs_ma = ""
        if ma_mean and mean and label != "MA" and label != "US":
            pct = (mean - ma_mean) / ma_mean * 100
            diff_vs_ma = f"{pct:+.1f}%"
        rows.append(
            f"| {label} | {emp:.0f} |" if emp else f"| {label} | — |"
        )
        rows[-1] += f" ${mean:,.0f} |" if mean else " — |"
        rows[-1] += f" ${median:,.0f} |" if median else " — |"
        rows[-1] += f" {diff_vs_ma} |" if diff_vs_ma else " — |"

    md = [
        "# BLS OEWS SOC 43-4061 — Eligibility Interviewers, Government Programs",
        "",
        "Cross-state benchmark wages from the Bureau of Labor Statistics Occupational",
        "Employment and Wage Statistics (OEWS) program for SOC 43-4061. This SOC covers",
        "*all* government-program eligibility interviewers (TANF, SNAP, Medicaid, SSDI/SSI),",
        "so it over-broadens vs. true disability-examiner work; use as a benchmark, not a",
        "direct substitute for state-published DDS-specific schedules.",
        "",
        f"Reference period: **May 2024** · Pulled: {pay_data['fetched_at']}",
        "",
        "| Area | Employment | Mean annual | Median annual | Diff vs MA |",
        "|---|---:|---:|---:|---:|",
        *rows,
        "",
    ]
    (PEER_STATES / "bls-oews-43-4061.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    if not API_KEY:
        print("Note: BLS_API_KEY not set — using anonymous quota. May hit limits.", file=sys.stderr)

    areas = {label: state_area(fips) for label, fips in STATES.items()}
    areas["US"] = national_area()

    data = fetch_for_areas(areas)
    write_outputs(data)

    ok_states = [k for k, v in data.items() if v.get("annual_mean")]
    print(f"BLS OEWS pull complete: {len(ok_states)}/{len(areas)} areas with data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
