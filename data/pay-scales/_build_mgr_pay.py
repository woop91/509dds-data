"""
Build manager-tier (non-VDE) per-employee CSV + incumbent timeline JSON for MRC
DDS-Det leadership roles 2010-2023. Counterpart to _build_vde_pay.py — drops
the VDE-only filter so we can see Asst Commissioners, Directors, Medical
Consultants, and Review Examiners.

Source: data/pay-scales/_raw_cthru_mrc_managers.json
  (pulled 2026-05-08 with $where=chris='MRC' AND (bargaining_group_no='M99' OR
  upper(position_title) LIKE '%COMMISSIONER%' OR upper(position_title) LIKE
  '%DIRECTOR%' OR upper(position_title) LIKE '%MEDICAL CONSULT%' OR
  upper(position_title) LIKE '%REVIEW EXAM%'))

Outputs:
  - mgr-annual-salary-by-employee.csv (one row per employee per year, latest snapshot)
  - mgr-incumbent-timeline-dds-det.json (year-by-year incumbents for the named §2 roles)
"""
import json, csv, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "_raw_cthru_mrc_managers.json")
CSV_OUT = os.path.join(HERE, "mgr-annual-salary-by-employee.csv")
TIMELINE_OUT = os.path.join(HERE, "mgr-incumbent-timeline-dds-det.json")

# Map raw position_title (uppercase) → canonical role name. Multiple
# raw titles can map to the same role (typos, dept rename, abbreviation).
TITLE_NORMALIZER = {
    "ASST COMMISSIONER DDS":             "Asst Comm DDS",
    "AST COMM DDS":                      "Asst Comm DDS",
    "ASST. COMM VOCATIONAL REHAB.":      "Asst Comm VR",
    "ASST COMM VOCATIONAL REHAB":        "Asst Comm VR",
    "ASST COMMISSIONER COMMUNITY LIVING":"Asst Comm CL",
    "ASST. COMM. COMMUNITY LIVING":      "Asst Comm CL",
    "DIR., QUALITY ASSURANCE, DDS":      "Director QA DDS",
    "DIR QUALITY ASSURANCE DDS":         "Director QA DDS",
    "FISCAL DIRECTOR DDS":               "Fiscal Director DDS",
    "REGIONAL DIRECTOR, DDS":            "Regional Director DDS",
    "REGIONAL DIRECTOR DDS":             "Regional Director DDS",
    "COMMISSIONER":                      "Commissioner MRC",
    "DEPUTY COMMISSIONER":               "Deputy Commissioner MRC",
    "TRAINING DIRECTOR":                 "Training Director",
    "DIR OF TRAINING":                   "Training Director",
    "HEARINGS DIRECTOR":                 "Hearings Director",
    "DIRECTOR OF HEARINGS UNIT":         "Hearings Director",
    "DIR OF HEARINGS UNIT":              "Hearings Director",
}

# Roles considered DDS-Det specifically (vs sister-division MRC roles)
DDS_DET_ROLES = [
    "Asst Comm DDS",
    "Director QA DDS",
    "Fiscal Director DDS",
    "Regional Director DDS",
    "Training Director",
    "Hearings Director",
]
# Adjacent context roles (MRC-level, oversees DDS-Det but not exclusive to it)
CONTEXT_ROLES = [
    "Commissioner MRC",
    "Deputy Commissioner MRC",
]
ALL_TRACKED_ROLES = DDS_DET_ROLES + CONTEXT_ROLES


def fl(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def normalize_title(raw_title):
    upper = (raw_title or "").upper().strip()
    return TITLE_NORMALIZER.get(upper, None)


def main():
    with open(RAW, "r", encoding="utf-8") as f:
        rows = json.load(f)

    # Dedup: latest service_end_date per (year, last, first, position_title)
    # Note we include position_title in the key because someone can transition
    # mid-year (e.g., Aja James VDE→Director in 2015 — both rows preserved).
    latest = {}
    for r in rows:
        k = (
            r["year"],
            r.get("name_last", "").upper(),
            r.get("name_first", "").upper(),
            r.get("position_title", "").upper(),
        )
        sed = r.get("service_end_date", "") or ""
        if k not in latest or sed > latest[k].get("service_end_date", ""):
            latest[k] = r
    dedup = list(latest.values())
    print(f"raw rows: {len(rows)}  dedup'd (year×name×title): {len(dedup)}")

    # Per-employee CSV (full manager dataset)
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["# 2010-2023 MRC manager-tier records (M99 OR commissioner/director title)."])
        w.writerow(["# Source: CTHRU rxhc-k6iz, chris='MRC', mgr-class titles. Pulled 2026-05-08."])
        w.writerow(["# 2023 actual_paid is INCOMPLETE — latest snapshot 2023-01-14 (~2 weeks)."])
        w.writerow([
            "year", "name_last", "name_first", "position_title", "canonical_role",
            "bargaining_group_no", "annual_rate",
            "actual_paid", "overtime_paid", "other_paid", "buyout_paid",
            "snapshot_through", "department_division",
        ])
        for r in sorted(dedup, key=lambda r: (r["year"], r.get("name_last", ""), r.get("name_first", ""))):
            w.writerow([
                r.get("year", ""),
                r.get("name_last", ""),
                r.get("name_first", ""),
                r.get("position_title", ""),
                normalize_title(r.get("position_title", "")) or "",
                r.get("bargaining_group_no", ""),
                r.get("annual_rate", ""),
                r.get("pay_total_actual", ""),
                r.get("pay_overtime_actual", ""),
                r.get("pay_other_actual", ""),
                r.get("pay_buyout_actual", ""),
                (r.get("service_end_date", "") or "")[:10],
                r.get("department_division", ""),
            ])
    print(f"wrote: {CSV_OUT} ({os.path.getsize(CSV_OUT)} bytes)")

    # Build per-role per-year incumbent table
    by_role_year = defaultdict(lambda: defaultdict(dict))
    for r in dedup:
        role = normalize_title(r.get("position_title", ""))
        if role not in ALL_TRACKED_ROLES:
            continue
        y = r["year"]
        name = f"{r.get('name_first','').strip()} {r.get('name_last','').strip()}".strip()
        sed = r.get("service_end_date", "")
        cur = by_role_year[role][y].get(name)
        if cur is None or sed > cur.get("service_end_date", ""):
            by_role_year[role][y][name] = r

    # Build the incumbent JSON
    timeline = {
        "$comment": (
            "DDS-Det leadership incumbent timeline 2010-2023, derived from CTHRU "
            "rxhc-k6iz manager-tier pull. Each role lists every person who held it "
            "in each year, with their annual_rate, actual_paid, and snapshot date. "
            "When more than one person appears in a year, that signals a mid-year "
            "transition; the snapshot dates show when each held the role. "
            "2023 entries are partial-year (~2-week snapshot only)."
        ),
        "source": {
            "dataset": "https://cthru.data.socrata.com/resource/rxhc-k6iz.json",
            "filter": (
                "chris='MRC' AND (bargaining_group_no='M99' OR upper(position_title) LIKE "
                "'%COMMISSIONER%' OR upper(position_title) LIKE '%DIRECTOR%' OR "
                "upper(position_title) LIKE '%MEDICAL CONSULT%' OR "
                "upper(position_title) LIKE '%REVIEW EXAM%')"
            ),
            "pulled": "2026-05-08",
            "raw_rows": len(rows),
        },
        "title_normalizer": {k: v for k, v in TITLE_NORMALIZER.items()},
        "headline_findings": {
            "asst_comm_dds_predecessor_chain": [
                "Barbara Kinney (2008 per MRC AR 2012, observed in CTHRU 2010 → Jan 2015)",
                "Patricia Roda (2015 → March 2021 — silent transition, no public press release found)",
                "Aja James (March 7, 2021 → present per mass.gov press release 2021-02-25)",
            ],
            "mrc_commissioner_chain": [
                "Charles Carr (observed CTHRU 2010 → March 2015)",
                "Adelaide Osborne (2015 → February 2017 — interim/acting; not previously identified in firecrawl results)",
                "Toni Wolf (2017 → present)",
            ],
            "deputy_commissioner_chain": [
                "Kasper Goshgarian (2010 → 2017)",
                "Kathleen Biebel (2018 → present)",
            ],
            "director_qa_dds_chain": [
                "Brian Miles (2010 → 2013)",
                "Kristine Robbins (2013 → present)",
            ],
            "fiscal_director_dds_chain": [
                "Luis Mancebo (2010 → present, single incumbent across full 14-year span)",
            ],
        },
        "by_role": {},
    }

    for role in ALL_TRACKED_ROLES:
        timeline["by_role"][role] = {}
        for y in sorted(by_role_year[role]):
            timeline["by_role"][role][y] = []
            for name, r in sorted(by_role_year[role][y].items()):
                timeline["by_role"][role][y].append({
                    "name": name,
                    "raw_title": r.get("position_title", ""),
                    "bargaining_group_no": r.get("bargaining_group_no", ""),
                    "annual_rate": fl(r.get("annual_rate")),
                    "actual_paid": fl(r.get("pay_total_actual")),
                    "overtime_paid": fl(r.get("pay_overtime_actual")),
                    "snapshot_through": (r.get("service_end_date", "") or "")[:10],
                })

    with open(TIMELINE_OUT, "w", encoding="utf-8") as fh:
        json.dump(timeline, fh, indent=2)
    print(f"wrote: {TIMELINE_OUT} ({os.path.getsize(TIMELINE_OUT)} bytes)")

    # Headline: Asst Comm DDS + Commissioner MRC tables to stdout for verification
    print()
    for role in ["Asst Comm DDS", "Commissioner MRC"]:
        print(f"=== {role} ===")
        for y in sorted(timeline["by_role"][role]):
            for entry in timeline["by_role"][role][y]:
                print(f"  {y}  {entry['name']:<30}  ${entry['annual_rate']:>10,.0f}  paid ${entry['actual_paid']:>10,.0f}  through {entry['snapshot_through']}")
        print()


if __name__ == "__main__":
    main()
