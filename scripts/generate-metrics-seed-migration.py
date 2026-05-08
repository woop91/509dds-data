"""
generate-metrics-seed-migration.py

Reads the 5 long-form JSON extracts under data/ssa/ and emits a Supabase
migration file that seeds:

  1. metric_sources   — provenance for each upstream dataset
  2. metrics          — catalog rows for every metric_id used in the data
  3. metric_series    — bulk INSERT of all (metric, scope, code, year, value)

Output is written to stdout by default, or to --out <path>. Designed to
write the generated SQL into ../509dds-coord/supabase/migrations/0305_*.sql
where it lives alongside the schema migration (0304).

Run from the 509dds-data repo root:
    python scripts/generate-metrics-seed-migration.py \
        --out ../509dds-coord/supabase/migrations/0305_seed_metrics.sql
"""
import argparse
import json
import os
import sys
from typing import Iterable

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Source registry — one row per upstream dataset that produces metric_series.
SOURCES = [
    {
        "id": "SSA_DDS_EXAMINERS_BY_STATE",
        "name": "SSA: Disability Examiners by State (annual)",
        "url": "https://www.ssa.gov/foia/readingroom.html",
        "description": "Federal-source annual count of DDS Disability Examiners by state, FY2002-2018.",
        "fetch_manifest_sha": None,
    },
    {
        "id": "SSA_DDS_EMPLOYEES_BY_STATE",
        "name": "SSA: Total State DDS Employees by State (annual)",
        "url": "https://www.ssa.gov/foia/readingroom.html",
        "description": "Federal-source annual count of total DDS staff by state, FY2010-2023.",
        "fetch_manifest_sha": None,
    },
    {
        "id": "SSA_INITIAL_CLAIMS_BY_TITLE",
        "name": "SSA: Initial Claims Receipts by Title (national)",
        "url": "https://www.ssa.gov/foia/readingroom.html",
        "description": "National-level initial disability claims receipts split by Title II (SSDI), Title XVI (SSI), and Concurrent, FY2001-2019.",
        "fetch_manifest_sha": None,
    },
    {
        "id": "SSA_ALLOWANCE_RATES_BY_STATE",
        "name": "SSA: Disability Claims Allowance Rates by Nation, Region & State (annual)",
        "url": "https://www.ssa.gov/foia/readingroom.html",
        "description": "Annual SSA publication of initial and reconsideration allowance rates by state and SSA region, FY2018-2024.",
        "fetch_manifest_sha": None,
    },
    {
        "id": "SSA_ALLOWANCE_FOIA_AI9370_01",
        "name": "SSA FOIA AI9370-01: FY2019 Allowance Rates (Reading Room)",
        "url": "https://www.ssa.gov/foia/readingroom.html",
        "description": "FOIA-pedigreed FY2019 allowance rates by state, used to fill the gap between the 2017 PDF and the 2018-2024 xlsx with audit-grade numbers.",
        "fetch_manifest_sha": None,
    },
]


# Metric catalog — one row per metric_id actually present in the JSONs.
METRICS = [
    {
        "id": "dds_examiners_count",
        "label": "DDS Disability Examiners (by state)",
        "short_label": "DDS Examiners",
        "description": "Annual count of state DDS Disability Examiners (the production-bottleneck role responsible for adjudicating SSDI/SSI claims). Federal-source. State-level cuts plus SSA region totals (BOS, NEW YORK, PHILADELPHIA, ATL, CHICAGO, DALLAS, KANSAS CITY, DENVER, SAN FRANCISCO, SEATTLE) and a National row.",
        "unit": "count",
        "format": "integer",
        "category": "staffing",
        "scope": "state",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_DDS_EXAMINERS_BY_STATE",
        "tags": ["staffing", "examiners", "production", "workforce", "dds"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "total_dds_employees",
        "label": "Total State DDS Employees (by state)",
        "short_label": "Total DDS Staff",
        "description": "Annual count of total state DDS employees including examiners, support staff, medical consultants, and supervisors. Pair with dds_examiners_count to compute examiner-share-of-staff.",
        "unit": "count",
        "format": "integer",
        "category": "staffing",
        "scope": "state",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_DDS_EMPLOYEES_BY_STATE",
        "tags": ["staffing", "headcount", "workforce", "dds"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "initial_claims_ssdi",
        "label": "Initial SSDI claims filed (national)",
        "short_label": "SSDI claims",
        "description": "Annual national count of initial SSDI (Title II) claims filed.",
        "unit": "cases",
        "format": "integer",
        "category": "workload",
        "scope": "national",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_INITIAL_CLAIMS_BY_TITLE",
        "tags": ["claims", "workload", "ssdi", "title-2"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "initial_claims_ssi",
        "label": "Initial SSI claims filed (national)",
        "short_label": "SSI claims",
        "description": "Annual national count of initial SSI (Title XVI) claims filed.",
        "unit": "cases",
        "format": "integer",
        "category": "workload",
        "scope": "national",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_INITIAL_CLAIMS_BY_TITLE",
        "tags": ["claims", "workload", "ssi", "title-16"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "initial_claims_concurrent",
        "label": "Initial concurrent claims filed (national)",
        "short_label": "Concurrent claims",
        "description": "Annual national count of initial claims filed for both SSDI (Title II) and SSI (Title XVI) concurrently.",
        "unit": "cases",
        "format": "integer",
        "category": "workload",
        "scope": "national",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_INITIAL_CLAIMS_BY_TITLE",
        "tags": ["claims", "workload", "concurrent"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "initial_claims_total",
        "label": "Total initial disability claims filed (national)",
        "short_label": "Total claims",
        "description": "Annual national total of initial disability claims (SSDI + SSI + Concurrent).",
        "unit": "cases",
        "format": "integer",
        "category": "workload",
        "scope": "national",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_INITIAL_CLAIMS_BY_TITLE",
        "tags": ["claims", "workload", "total"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "allowance_rate_initial_pct",
        "label": "Initial allowance rate (by state)",
        "short_label": "Initial allowance %",
        "description": "Percent of initial disability claims allowed at the DDS level. Computed by SSA as favorable initial determinations divided by all initial determinations. Note: this differs from the SSA-FYWL 'eligible-population allowance rate' which uses a different denominator.",
        "unit": "pct",
        "format": "percent",
        "category": "allowance",
        "scope": "state",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_ALLOWANCE_RATES_BY_STATE",
        "tags": ["allowance", "outcomes", "initial", "dds"],
        "is_public": True,
        "is_ai_visible": True,
    },
    {
        "id": "allowance_rate_recon_pct",
        "label": "Reconsideration allowance rate (by state)",
        "short_label": "Recon allowance %",
        "description": "Percent of reconsideration disability claims allowed at the DDS level. Reconsideration is the second adjudicative level after initial denial. Some states show '2/' (redacted: small sample size).",
        "unit": "pct",
        "format": "percent",
        "category": "allowance",
        "scope": "state",
        "default_chart": "line",
        "confidence": "authoritative",
        "source_id": "SSA_ALLOWANCE_RATES_BY_STATE",
        "tags": ["allowance", "outcomes", "reconsideration", "dds"],
        "is_public": True,
        "is_ai_visible": True,
    },
]


def sql_str(s) -> str:
    """SQL-escape a string literal."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def sql_array(items) -> str:
    if not items:
        return "ARRAY[]::text[]"
    return "ARRAY[" + ", ".join(sql_str(i) for i in items) + "]"


def sql_num(v) -> str:
    if v is None:
        return "NULL"
    return str(v)


def sql_bool(v) -> str:
    return "true" if v else "false"


def emit_sources(out) -> None:
    out.write("-- ── 1. Sources ──\n")
    for s in SOURCES:
        out.write(
            "INSERT INTO public.metric_sources (id, name, url, description, fetch_manifest_sha) VALUES "
            f"({sql_str(s['id'])}, {sql_str(s['name'])}, {sql_str(s['url'])}, "
            f"{sql_str(s['description'])}, {sql_str(s['fetch_manifest_sha'])}) "
            "ON CONFLICT (id) DO UPDATE SET "
            "name = EXCLUDED.name, url = EXCLUDED.url, description = EXCLUDED.description;\n"
        )
    out.write("\n")


def emit_metrics(out) -> None:
    out.write("-- ── 2. Metric catalog ──\n")
    for m in METRICS:
        out.write(
            "INSERT INTO public.metrics (id, label, short_label, description, unit, format, "
            "category, scope, default_chart, confidence, source_id, tags, is_public, is_ai_visible) VALUES "
            f"({sql_str(m['id'])}, {sql_str(m['label'])}, {sql_str(m['short_label'])}, "
            f"{sql_str(m['description'])}, {sql_str(m['unit'])}, {sql_str(m['format'])}, "
            f"{sql_str(m['category'])}, {sql_str(m['scope'])}, {sql_str(m['default_chart'])}, "
            f"{sql_str(m['confidence'])}, {sql_str(m['source_id'])}, {sql_array(m['tags'])}, "
            f"{sql_bool(m['is_public'])}, {sql_bool(m['is_ai_visible'])}) "
            "ON CONFLICT (id) DO UPDATE SET "
            "label = EXCLUDED.label, short_label = EXCLUDED.short_label, "
            "description = EXCLUDED.description, unit = EXCLUDED.unit, format = EXCLUDED.format, "
            "category = EXCLUDED.category, scope = EXCLUDED.scope, "
            "default_chart = EXCLUDED.default_chart, confidence = EXCLUDED.confidence, "
            "source_id = EXCLUDED.source_id, tags = EXCLUDED.tags, "
            "is_public = EXCLUDED.is_public, is_ai_visible = EXCLUDED.is_ai_visible, "
            "updated_at = now();\n"
        )
    out.write("\n")


def emit_series(out) -> None:
    out.write("-- ── 3. metric_series rows from JSON extracts ──\n")
    json_files = [
        "data/ssa/staffing/dds-examiners-by-state-fy2002-2018.json",
        "data/ssa/staffing/dds-employees-by-state-fy2010-2023.json",
        "data/ssa/claims/initial-claims-by-title-fy2001-2019.json",
        "data/ssa/allowance-rates/allowance-rates-by-state-2018-2024.json",
        "data/ssa/allowance-rates/fy2019-foia-reading-room.json",
    ]
    total_rows = 0
    for jf in json_files:
        path = os.path.join(REPO, jf.replace("/", os.sep))
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rows = data.get("rows", [])
        if not rows:
            continue
        out.write(f"\n-- {jf}: {len(rows)} rows\n")
        # Bulk INSERT in chunks of 500 for parser-friendliness
        chunk_size = 500
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            out.write(
                "INSERT INTO public.metric_series "
                "(metric_id, state_code, period_year, period_grain, period_index, value) VALUES\n"
            )
            value_lines = []
            for r in chunk:
                value_lines.append(
                    f"  ({sql_str(r['metric'])}, {sql_str(r['code'])}, "
                    f"{int(r['year'])}, 'annual', 0, {sql_num(r['value'])})"
                )
            out.write(",\n".join(value_lines))
            out.write(
                "\nON CONFLICT (metric_id, state_code, period_year, period_grain, period_index) "
                "DO UPDATE SET value = EXCLUDED.value, is_estimated = EXCLUDED.is_estimated;\n"
            )
            total_rows += len(chunk)
    out.write(f"\n-- Total metric_series rows seeded: {total_rows}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="Output SQL file (default: stdout)")
    args = ap.parse_args()
    out = open(args.out, "w", encoding="utf-8", newline="\n") if args.out else sys.stdout
    out.write("-- 0305_seed_metrics.sql\n")
    out.write("-- Seed metric_sources + metrics catalog + initial metric_series rows from\n")
    out.write("-- the 509dds-data long-form JSON extracts. Generated by\n")
    out.write("-- 509dds-data/scripts/generate-metrics-seed-migration.py — do not hand-edit;\n")
    out.write("-- regenerate after upstream JSON refresh.\n\n")
    out.write("BEGIN;\n\n")
    emit_sources(out)
    emit_metrics(out)
    emit_series(out)
    out.write("\nCOMMIT;\n")
    out.write("\n-- Refresh the materialized YoY view after seeding\n")
    out.write("REFRESH MATERIALIZED VIEW public.metric_yoy;\n")
    if args.out:
        out.close()


if __name__ == "__main__":
    main()
