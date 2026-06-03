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
