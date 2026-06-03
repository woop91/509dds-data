#!/usr/bin/env python3
"""compute_value_stats.py — enrich tabular cards with per-column value-stats.

For each csv/json data file whose card declares columns, compute per-column
distinct_count + sample_values (and min/max for numeric columns) plus a
card-level row_count, and merge them into the card. Only genuinely tabular data
is processed: CSV, and JSON that is a flat list-of-records. Non-tabular JSON is
SKIPPED and reported. Cards are written format-preservingly (only the columns
block + row_count change).

Usage:
  python scripts/compute_value_stats.py            # write stats into cards
  python scripts/compute_value_stats.py --check     # exit 1 if any card would change
"""
from __future__ import annotations

import argparse
import csv as csvmod
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cards import REPO, load_cards  # noqa: E402

NUMERIC = {"integer", "number", "percent"}
SAMPLE_CAP = 5


def _num(v):
    if isinstance(v, str):
        v = v.strip()
        if v.endswith("%"):
            v = v[:-1].strip()
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None


def column_stats(values, declared_type: str) -> dict:
    non_empty = [v for v in values if v not in (None, "")]
    # distinct over raw non-empty string cells
    seen, distinct = set(), []
    for v in non_empty:
        if v not in seen:
            seen.add(v)
            distinct.append(v)
    stats: dict = {"distinct_count": len(distinct)}
    if declared_type in NUMERIC:
        nums = [n for n in (_num(v) for v in non_empty) if n is not None]
        if nums:
            stats["min"] = min(nums)
            stats["max"] = max(nums)
        sample_nums = sorted({n for n in nums})[:SAMPLE_CAP]
        stats["sample_values"] = sample_nums
    else:
        stats["sample_values"] = distinct[:SAMPLE_CAP]
    return stats


def _csv_data_lines(text: str) -> list[str]:
    """Drop leading #-comment preamble lines (some repo CSVs carry a comment
    block before the real header); the first non-comment line is the header."""
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith(("#", '"#')):
        i += 1
    return lines[i:]


def stats_from_csv(path: Path, columns):
    try:
        # utf-8-sig strips a leading BOM so the first column name is not mangled.
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    rows = list(csvmod.DictReader(_csv_data_lines(text)))
    by_col = {c["name"]: column_stats([r.get(c["name"], "") for r in rows], c.get("type", "string"))
              for c in columns if c.get("name")}
    return by_col, len(rows)


def stats_from_json(path: Path, columns):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not (isinstance(data, list) and data and all(isinstance(r, dict) for r in data)):
        return None  # not a flat list-of-records -> not tabular
    def cell(r, name):
        v = r.get(name)
        return "" if v is None else str(v)
    by_col = {c["name"]: column_stats([cell(r, c["name"]) for r in data], c.get("type", "string"))
              for c in columns if c.get("name")}
    return by_col, len(data)


def merge_columns(columns, col_stats):
    out = []
    for c in columns:
        s = col_stats.get(c.get("name"), {})
        out.append({**c, **s})
    return out


def _render_value(v):
    return json.dumps(v, ensure_ascii=False)


def render_columns_block(columns) -> str:
    lines = ["  \"columns\": ["]
    rendered = []
    for c in columns:
        inner = ", ".join(f"{json.dumps(k)}: {_render_value(v)}" for k, v in c.items())
        rendered.append("    { " + inner + " }")
    return lines[0] + "\n" + ",\n".join(rendered) + "\n  ]"


def update_card_text(text: str, new_columns, row_count) -> str:
    # replace the columns block (2-indent key, closes at "\n  ]")
    block = render_columns_block(new_columns)
    new_text, n = re.subn(r'  "columns": \[.*?\n  \]', lambda _m: block, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit("could not locate a single columns block")
    if row_count is not None:
        if re.search(r'  "row_count": [^,\n]*', new_text):
            new_text = re.sub(r'  "row_count": [^,\n]*', f'  "row_count": {row_count}', new_text, count=1)
        else:
            # insert row_count immediately before the columns block
            new_text = new_text.replace('  "columns": [', f'  "row_count": {row_count},\n  "columns": [', 1)
    return new_text


def run(repo: Path, write: bool) -> dict:
    changed, skipped = [], []
    for rel_meta, card in load_cards(repo):
        if card.get("format") not in ("csv", "json") or not card.get("columns"):
            continue
        data_path = repo / card["path"]
        if card["format"] == "csv":
            result = stats_from_csv(data_path, card["columns"])
        else:
            result = stats_from_json(data_path, card["columns"])
        if result is None:
            skipped.append((card.get("id"), f"non-tabular or unreadable {card['format']}"))
            continue
        col_stats, row_count = result
        new_columns = merge_columns(card["columns"], col_stats)
        if new_columns == card["columns"] and card.get("row_count") == row_count:
            continue
        changed.append(rel_meta)
        if write:
            path = repo / rel_meta
            path.write_text(update_card_text(path.read_text(encoding="utf-8"), new_columns, row_count),
                            encoding="utf-8")
    return {"changed": changed, "skipped": skipped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    res = run(REPO, write=not args.check)
    if args.check:
        if res["changed"]:
            print(f"OUT OF DATE: {len(res['changed'])} tabular cards missing/stale value-stats — run scripts/compute_value_stats.py")
            sys.exit(1)
        print(f"value-stats current ({len(res['skipped'])} non-tabular cards skipped)")
        return
    print(f"wrote value-stats into {len(res['changed'])} cards; skipped {len(res['skipped'])} non-tabular")


if __name__ == "__main__":
    main()
