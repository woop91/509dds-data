"""
generate-personnel-seed-migration.py

Reads data/pay-scales/_raw_cthru_mrc_managers.json (the unfiltered CTHRU
manager-tier dump from chris=MRC) and emits a Supabase seed migration that
populates public.mrc_payroll_snapshots. The schema lives in 509dds-coord
migration 0316_dds_personnel_schema.sql.

Output target:
    ../509dds-coord/supabase/migrations/0317_seed_dds_personnel.sql

Runs from the 509dds-data repo root:
    python scripts/generate-personnel-seed-migration.py \
        --out ../509dds-coord/supabase/migrations/0317_seed_dds_personnel.sql

Idempotent: ON CONFLICT clauses keyed on the unique constraint
(year, name_last, name_first, position_title, snapshot_through) — re-runnable
after a fresh CTHRU pull without producing duplicate rows.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "data", "pay-scales", "_raw_cthru_mrc_managers.json")

# Mirrors the TITLE_NORMALIZER in data/pay-scales/_build_mgr_pay.py.
# Keep this list in sync with that file when adding new title variants.
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


def normalize_title(raw_title):
    upper = (raw_title or "").upper().strip()
    return TITLE_NORMALIZER.get(upper)


def sql_str(s):
    """Escape a string value for SQL — doubles single quotes; null when None or empty."""
    if s is None or s == "":
        return "null"
    return "'" + str(s).replace("'", "''") + "'"


def sql_num(v):
    """Render a numeric value or null."""
    if v is None or v == "":
        return "null"
    try:
        return f"{float(v):.2f}"
    except (TypeError, ValueError):
        return "null"


def sql_int(v):
    if v is None or v == "":
        return "null"
    try:
        return str(int(v))
    except (TypeError, ValueError):
        return "null"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="-",
                        help="Output path for the generated SQL. '-' writes to stdout.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit rows emitted (for testing).")
    parser.add_argument("--leadership-only", action="store_true",
                        help="Emit only rows where canonical_role IS NOT NULL — for fast initial UI seeding while the full bulk load is deferred.")
    args = parser.parse_args()

    with open(RAW, "r", encoding="utf-8") as f:
        rows = json.load(f)

    # Dedup by the unique key in the schema:
    # (year, name_last, name_first, position_title, snapshot_through)
    # Latest snapshot wins (highest service_end_date).
    seen = {}
    for r in rows:
        sed = (r.get("service_end_date", "") or "")[:10]
        if not sed:
            continue
        k = (
            r.get("year"),
            (r.get("name_last") or "").upper(),
            (r.get("name_first") or "").upper(),
            (r.get("position_title") or ""),
            sed,
        )
        if k not in seen:
            seen[k] = r

    rows_unique = list(seen.values())
    if args.leadership_only:
        rows_unique = [r for r in rows_unique
                       if normalize_title(r.get("position_title", "")) is not None]
    if args.limit:
        rows_unique = rows_unique[: args.limit]

    rows_unique.sort(key=lambda r: (
        int(r.get("year") or 0),
        (r.get("name_last") or ""),
        (r.get("name_first") or ""),
        (r.get("service_end_date") or ""),
    ))

    # Build the SQL
    out = []
    out.append("-- 0317_seed_dds_personnel.sql")
    out.append("-- Seeds public.mrc_payroll_snapshots from CTHRU manager-tier pull.")
    out.append("-- Source: 509dds-data/data/pay-scales/_raw_cthru_mrc_managers.json")
    out.append("-- Generator: 509dds-data/scripts/generate-personnel-seed-migration.py")
    out.append(f"-- Row count: {len(rows_unique)} dedup'd rows")
    out.append("--")
    out.append("-- Idempotent via ON CONFLICT on the unique constraint")
    out.append("-- (year, name_last, name_first, position_title, snapshot_through).")
    out.append("--")
    out.append("-- DEMO-ONLY: this seed honors the [No seed to prod] hard rule via the")
    out.append("-- @demo-only / @end-demo-only markers below. The husky pre-commit gate")
    out.append("-- (scripts/husky-pre-commit-gates.mjs) skips raw INSERTs inside this")
    out.append("-- block when the migration is applied to the demo Supabase project.")
    out.append("-- Prod application requires removing the markers AND explicit user OK.")
    out.append("")
    out.append("-- @demo-only")

    # Insert in batches of ~500 rows for SQL parser friendliness
    BATCH = 500
    for batch_start in range(0, len(rows_unique), BATCH):
        batch = rows_unique[batch_start: batch_start + BATCH]
        out.append("insert into public.mrc_payroll_snapshots (")
        out.append("  year, name_last, name_first, position_title, canonical_role,")
        out.append("  bargaining_group_no, department_division,")
        out.append("  annual_rate, actual_paid, overtime_paid, other_paid, buyout_paid,")
        out.append("  snapshot_through, source_id, raw_trans_no")
        out.append(") values")
        value_lines = []
        for r in batch:
            year = r.get("year")
            last = r.get("name_last", "")
            first = r.get("name_first", "")
            title = r.get("position_title", "")
            canonical = normalize_title(title)
            bgn = r.get("bargaining_group_no", "")
            dept = r.get("department_division", "")
            annual_rate = r.get("annual_rate")
            actual = r.get("pay_total_actual")
            ot = r.get("pay_overtime_actual")
            other = r.get("pay_other_actual")
            buyout = r.get("pay_buyout_actual")
            sed = (r.get("service_end_date", "") or "")[:10]
            trans = r.get("trans_no", "")

            value_lines.append("  ({y}, {l}, {f}, {t}, {c}, {b}, {d}, {ar}, {ap}, {ot}, {oth}, {bo}, {s}, 'CTHRU_MRC_MANAGERS', {tn})".format(
                y=sql_int(year),
                l=sql_str(last),
                f=sql_str(first),
                t=sql_str(title),
                c=sql_str(canonical),
                b=sql_str(bgn),
                d=sql_str(dept),
                ar=sql_num(annual_rate),
                ap=sql_num(actual),
                ot=sql_num(ot),
                oth=sql_num(other),
                bo=sql_num(buyout),
                s=sql_str(sed),
                tn=sql_str(trans),
            ))
        out.append(",\n".join(value_lines))
        out.append("on conflict (year, name_last, name_first, position_title, snapshot_through) do update set")
        out.append("  canonical_role = excluded.canonical_role,")
        out.append("  bargaining_group_no = excluded.bargaining_group_no,")
        out.append("  department_division = excluded.department_division,")
        out.append("  annual_rate = excluded.annual_rate,")
        out.append("  actual_paid = excluded.actual_paid,")
        out.append("  overtime_paid = excluded.overtime_paid,")
        out.append("  other_paid = excluded.other_paid,")
        out.append("  buyout_paid = excluded.buyout_paid,")
        out.append("  source_id = excluded.source_id,")
        out.append("  raw_trans_no = excluded.raw_trans_no;")
        out.append("")

    out.append("-- @end-demo-only")
    sql = "\n".join(out)

    if args.out == "-":
        sys.stdout.write(sql)
    else:
        out_path = os.path.abspath(os.path.join(REPO, args.out)) if not os.path.isabs(args.out) else args.out
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(sql)
        print(f"wrote {len(rows_unique)} rows to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
