"""
Build VDE per-employee CSV + yearly aggregates + outliers from CTHRU dump.
Source: data/pay-scales/_raw_cthru_vde_2010-2023.json
Outputs:
  - vde-annual-salary-by-employee.csv (one row per employee per year, latest snapshot)
  - vde-annual-salary-aggregates.json (per-year and per-grade rollups + outliers)
"""
import json, csv, statistics, os, re
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "_raw_cthru_vde_2010-2023.json")
CSV_OUT = os.path.join(HERE, "vde-annual-salary-by-employee.csv")
AGG_OUT = os.path.join(HERE, "vde-annual-salary-aggregates.json")


def grade_for(title):
    t = (title or "").upper()
    if "CHIEF" in t:
        return "Chief VDE"
    if re.search(r"\bIV\b", t):
        return "IV"
    if re.search(r"\bIII\b", t):
        return "III"
    if re.search(r"\bII\b", t):
        return "II"
    if re.search(r"\bI\b", t) and "EXAMINER" in t:
        return "I"
    if "A/B" in t:
        return "A_B"
    if "(C)" in t:
        return "C"
    if "(D)" in t:
        return "D"
    return "OTHER"


def fl(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def quartiles(sorted_vals):
    if not sorted_vals:
        return None, None, None
    n = len(sorted_vals)
    q1 = statistics.median(sorted_vals[: n // 2]) if n >= 2 else sorted_vals[0]
    q2 = statistics.median(sorted_vals)
    q3 = (
        statistics.median(sorted_vals[(n + 1) // 2 :])
        if n >= 2
        else sorted_vals[-1]
    )
    return q1, q2, q3


def stats_block(vals):
    """Return mean/median/mode/stdev/min/max/p25/p75 for a list of floats."""
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    n = len(vals)
    q1, _, q3 = quartiles(vals)
    try:
        mode = statistics.mode(vals)
    except statistics.StatisticsError:
        mode = None
    return {
        "n": n,
        "min": round(vals[0], 2),
        "p25": round(q1, 2) if q1 is not None else None,
        "median": round(statistics.median(vals), 2),
        "mean": round(statistics.mean(vals), 2),
        "p75": round(q3, 2) if q3 is not None else None,
        "max": round(vals[-1], 2),
        "stdev": round(statistics.pstdev(vals), 2) if n >= 2 else 0,
        "mode": round(mode, 2) if mode is not None else None,
        "sum": round(sum(vals), 2),
    }


def find_outliers(items, key_fn, label_fn, top_n=5):
    """
    IQR method: outliers = values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR].
    Also returns top-N highest values regardless of IQR (useful for OT spotlight).
    """
    paired = [(key_fn(it), it) for it in items if key_fn(it) is not None]
    if not paired:
        return {"iqr_high": [], "iqr_low": [], "top_n": []}

    vals = sorted(v for v, _ in paired)
    q1, _, q3 = quartiles(vals)
    iqr = (q3 - q1) if (q1 is not None and q3 is not None) else 0
    lo = q1 - 1.5 * iqr if q1 is not None else None
    hi = q3 + 1.5 * iqr if q3 is not None else None

    iqr_high = sorted(
        [(v, it) for v, it in paired if hi is not None and v > hi],
        key=lambda x: -x[0],
    )[:top_n]
    iqr_low = sorted(
        [(v, it) for v, it in paired if lo is not None and v < lo],
        key=lambda x: x[0],
    )[:top_n]
    top = sorted(paired, key=lambda x: -x[0])[:top_n]

    def fmt(pair):
        v, it = pair
        return {"value": round(v, 2), "label": label_fn(it)}

    return {
        "iqr_threshold_high": round(hi, 2) if hi is not None else None,
        "iqr_threshold_low": round(lo, 2) if lo is not None else None,
        "iqr_high_outliers": [fmt(p) for p in iqr_high],
        "iqr_low_outliers": [fmt(p) for p in iqr_low],
        "top_n": [fmt(p) for p in top],
    }


def main():
    with open(RAW, "r", encoding="utf-8") as f:
        rows = json.load(f)

    # Dedup: latest service_end_date per (year, last, first)
    latest = {}
    for r in rows:
        k = (r["year"], r.get("name_last", "").upper(), r.get("name_first", "").upper())
        sed = r.get("service_end_date", "") or ""
        if k not in latest or sed > latest[k].get("service_end_date", ""):
            latest[k] = r
    dedup = list(latest.values())
    print(f"raw rows: {len(rows)}  dedup'd: {len(dedup)}")

    # Write per-employee CSV
    with open(CSV_OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        # Banner comment rows (lines beginning with # — most CSV parsers can be told to skip;
        # leaves a loud visual flag for anyone opening in Excel/text editor).
        w.writerow(["# DATA GAP: 2001-2009 NOT INCLUDED — CTHRU public payroll begins CY 2010. See README.md / methodology.md."])
        w.writerow(["# 2023 actual_paid + overtime are INCOMPLETE — CTHRU's latest 2023 snapshot is 2023-01-14 (~2 weeks of pay only). annual_rate field is fine for 2023."])
        w.writerow(["# Source: CTHRU rxhc-k6iz, chris='MRC', position_title LIKE '%DISAB EXAMINER%'. Build script: _build_vde_pay.py"])
        w.writerow([
            "year", "name_last", "name_first", "position_title", "grade", "position_type",
            "annual_rate", "regular_pay_paid", "overtime_pay_paid", "other_pay_paid",
            "buyout_pay_paid", "total_paid", "snapshot_through", "bargaining_unit",
        ])
        for r in sorted(dedup, key=lambda r: (r["year"], r.get("name_last", ""), r.get("name_first", ""))):
            w.writerow([
                r.get("year", ""),
                r.get("name_last", ""),
                r.get("name_first", ""),
                r.get("position_title", ""),
                grade_for(r.get("position_title", "")),
                r.get("position_type", ""),
                r.get("annual_rate", ""),
                r.get("pay_base_actual", ""),
                r.get("pay_overtime_actual", ""),
                r.get("pay_other_actual", ""),
                r.get("pay_buyout_actual", ""),
                r.get("pay_total_actual", ""),
                (r.get("service_end_date", "") or "")[:10],
                r.get("bargaining_group_no", ""),
            ])
    print(f"wrote: {CSV_OUT} ({os.path.getsize(CSV_OUT)} bytes)")

    # Group
    by_year_grade = defaultdict(list)
    by_year = defaultdict(list)
    for r in dedup:
        y = r["year"]
        g = grade_for(r.get("position_title", ""))
        by_year_grade[(y, g)].append(r)
        by_year[y].append(r)

    # Build aggregates with outliers
    def emp_label(r):
        name = f"{r.get('name_first','')} {r.get('name_last','')}".strip()
        return f"{name} ({grade_for(r.get('position_title',''))}, snap {(r.get('service_end_date','') or '')[:10]})"

    def block(items):
        return {
            "n": len(items),
            "annual_rate": stats_block([fl(r["annual_rate"]) for r in items if fl(r["annual_rate"]) > 0]),
            "actual_paid": stats_block([fl(r["pay_total_actual"]) for r in items if fl(r["pay_total_actual"]) > 0]),
            "overtime_paid_among_payers": stats_block([fl(r["pay_overtime_actual"]) for r in items if fl(r["pay_overtime_actual"]) > 0]),
            "overtime_total_sum": round(sum(fl(r["pay_overtime_actual"]) for r in items), 2),
            "overtime_n_payers": sum(1 for r in items if fl(r["pay_overtime_actual"]) > 0),
            "outliers": {
                "annual_rate":      find_outliers(items, lambda r: fl(r["annual_rate"]) or None, emp_label),
                "actual_paid":      find_outliers(items, lambda r: fl(r["pay_total_actual"]) or None, emp_label),
                "overtime_paid":    find_outliers(items, lambda r: fl(r["pay_overtime_actual"]) or None, emp_label),
            },
        }

    def year_complete(year, items):
        max_snap = max((r.get("service_end_date", "") or "")[:10] for r in items)
        return max_snap >= f"{year}-11-01", max_snap

    result = {
        "!!_DATA_GAP_2001_2009": {
            "status": "NOT AVAILABLE — CTHRU public payroll begins CY 2010",
            "affected_years": ["2001","2002","2003","2004","2005","2006","2007","2008","2009"],
            "what_is_missing": "Per-employee VDE annual salary and overtime for these 9 years.",
            "verified_sources_checked": [
                "MA Comptroller CTHRU (cthru.data.socrata.com) — earliest year is 2010",
                "MassOpenBooks — sources from Comptroller; same 2010 floor",
                "OpenTheBooks Massachusetts — sources from CTHRU; same 2010 floor",
                "Massachusetts Almanac salary index — no pre-2010 link",
                "Wayback Machine on mass.gov payroll URLs — no archived predecessor"
            ],
            "options_to_close_gap": {
                "(a)_PRR": "File a MA Public Records Request with the Office of the Comptroller for archival HRCMS extracts. Slow (weeks-months), may incur fees.",
                "(b)_Wayback_chart_based": "Pull old SEIU 509 Unit 8 salary chart PDFs from Wayback Machine and reconstruct *scheduled* (contract) rates. Note: chart-based, not actual paid — gives you what employees were entitled to per their step, NOT W-2 amounts. Cannot produce overtime data.",
                "(c)_declare_gap_acceptable": "Accept that pre-2010 individual VDE pay is not knowable without a PRR and proceed with 2010-2023 only."
            },
            "see_also": "docs/methodology.md → 'Pre-2010 gap' section"
        },
        "$comment": (
            "Per-year and per-(year,grade) aggregates of MA DDS-Det Vocational Disability Examiner pay. "
            "Source: CTHRU rxhc-k6iz, chris='MRC', position_title LIKE '%DISAB EXAMINER%'. "
            "Built from vde-annual-salary-by-employee.csv (deduplicated to latest service_end_date per "
            "(year, employee) — that snapshot's pay_year_to_date approximates W-2 earnings for that year). "
            "annual_rate = scheduled annualized rate (independent of snapshot). actual_paid = pay_total_actual "
            "as of last snapshot. For years where the latest snapshot reaches November or later "
            "(approximates_full_year=true), actual_paid is a near-W-2 figure; for 2023 the dataset's latest "
            "snapshot is 2023-01-14 so actual_paid is only ~2 weeks — flagged INCOMPLETE. "
            "PRE-2010 (2001–2009) DATA IS NOT INCLUDED — see !!_DATA_GAP_2001_2009 block above."
        ),
        "source": {
            "dataset": "https://cthru.data.socrata.com/resource/rxhc-k6iz.json",
            "filter": "chris='MRC' AND upper(position_title) LIKE '%DISAB EXAMINER%'",
            "fields_used": [
                "year", "name_last", "name_first", "position_title", "annual_rate",
                "pay_base_actual", "pay_overtime_actual", "pay_other_actual",
                "pay_buyout_actual", "pay_total_actual", "service_end_date",
            ],
            "scrape_date": "2026-05-04",
            "raw_row_count": len(rows),
            "dedup_row_count": len(dedup),
            "year_span": [min(r["year"] for r in dedup), max(r["year"] for r in dedup)],
        },
        "grade_legend": {
            "A_B": "Vocational Disab Examiner (A/B) — pre-2016, replaced by I",
            "C": "Vocational Disab Examiner (C) — pre-2016, replaced by II",
            "D": "Vocational Disab Examiner (D) — pre-2016, replaced by III",
            "I": "Vocational Disability Examiner I — Grade 20 (post-2016)",
            "II": "Vocational Disability Examiner II — Grade 21",
            "III": "Vocational Disability Examiner III — Grade 23",
            "IV": "Vocational Disability Examiner IV (post-2019)",
            "Chief VDE": "Chief Vocational Disability Examiner (job code 20-947)",
        },
        "outlier_methodology": (
            "IQR method: outliers are values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. "
            "iqr_high_outliers = values above the upper fence (top earners / heavy OT). "
            "iqr_low_outliers = values below the lower fence (often partial-year leavers). "
            "top_n = top 5 highest values regardless of IQR (always populated)."
        ),
        "year_data_completeness": {},
        "by_year": {y: block(by_year[y]) for y in sorted(by_year)},
        "by_year_and_grade": {
            y: {g: block(by_year_grade[(y, g)]) for g in sorted({k[1] for k in by_year_grade if k[0] == y})}
            for y in sorted(by_year)
        },
        "headline_findings": {
            "no_pre_2010_data": "CTHRU public payroll begins CY 2010. Per-employee 2001-2009 data not available without PRR.",
            "cy2023_incomplete": "Latest CTHRU snapshot for 2023 is 2023-01-14 — actual_paid and overtime sums reflect only ~2 weeks. Use annual_rate (scheduled) for 2023 trend analysis; do NOT compare actual_paid totals against prior years.",
            "vde_iv_post_2019_only": "Grade IV title introduced after 2018-2019 reclass cycle.",
            "old_grade_phaseout_2016": "A/B/C/D titles fully phased out by 2017.",
        },
    }

    for y, items in by_year.items():
        complete, max_snap = year_complete(y, items)
        result["year_data_completeness"][y] = {
            "latest_snapshot_in_dataset": max_snap,
            "approximates_full_year": complete,
        }

    with open(AGG_OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"wrote: {AGG_OUT} ({os.path.getsize(AGG_OUT)} bytes)")

    # Headline table
    print()
    hdr = f"{'YR':>4} {'N':>4} {'MIN_RATE':>8} {'MEAN_RATE':>9} {'MED_RATE':>8} {'MAX_RATE':>8} {'OT_TOT':>10} {'OT_MAX':>8} {'COMPLETE':>9}"
    print(hdr)
    print("-" * len(hdr))
    for y in sorted(by_year):
        a = result["by_year"][y]
        ar = a["annual_rate"] or {}
        c = result["year_data_completeness"][y]["approximates_full_year"]
        print(
            f"{y:>4} {a['n']:>4} "
            f"${ar.get('min',0):>7,.0f} ${ar.get('mean',0):>8,.0f} "
            f"${ar.get('median',0):>7,.0f} ${ar.get('max',0):>7,.0f} "
            f"${a['overtime_total_sum']:>9,.0f} ${(a['outliers']['overtime_paid'].get('top_n',[{}])[0] or {}).get('value',0):>7,.0f} "
            f"{'YES' if c else 'NO':>9}"
        )

    # Top OT earners across all time
    print("\nTop 10 single-year overtime earners across 2010-2023:")
    all_ot = [(fl(r["pay_overtime_actual"]), r) for r in dedup if fl(r["pay_overtime_actual"]) > 0]
    all_ot.sort(key=lambda x: -x[0])
    for v, r in all_ot[:10]:
        print(f"  {r['year']}  ${v:>9,.2f}  {r.get('name_first','')} {r.get('name_last','')}  ({r.get('position_title','')})")


if __name__ == "__main__":
    main()
