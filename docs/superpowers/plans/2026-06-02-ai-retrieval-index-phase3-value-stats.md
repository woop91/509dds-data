# AI-Retrieval Index — Phase 3 (Column Value-Stats) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Checkbox steps.

**Goal:** Enrich the 47 tabular cards (14 csv + 33 json) with per-column value-stats (min/max for numerics, distinct_count + sample_values for all) and card-level row_count, computed by opening the real data files — so an AI can answer "does this cover 2019?" / "what states are in here?" from the card. Then regenerate the catalog + embedding index.

**Architecture:** `compute_value_stats.py` computes stats from each data file (CSV via `csv.DictReader`; JSON only when it is a flat list-of-records — non-tabular JSON is SKIPPED and reported, never forced). Stats are merged into the existing `columns[]` objects and a `row_count` is set. Cards are written with a **format-preserving surgical writer**: only the `"columns": [ … ]` block (re-rendered in the existing inline-object style) and the `row_count` value change; all other fields stay byte-identical (lesson from Phase 2). `--check` gates drift. Re-run `build_catalog.py` + `build_embeddings.py`.

**Tech Stack:** Python 3 stdlib (`csv`, `json`, `re`), `pytest`. (xlsx not needed: 0 xlsx cards.)

**Spec:** `docs/superpowers/specs/2026-06-02-ai-retrieval-index-design.md` §6.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/compute_value_stats.py` (create) | Compute per-column stats from data files; surgical card writer; `--check` |
| `tests/test_compute_value_stats.py` (create) | Unit tests (hermetic tmp fixtures) |

**Shared interfaces:**
- `column_stats(values: list[str], declared_type: str) -> dict` — `{distinct_count, sample_values[, min, max]}` for one column's raw string cells
- `stats_from_csv(path: Path, columns: list[dict]) -> tuple[dict, int] | None` — `({col_name: stats}, row_count)`; None if unreadable
- `stats_from_json(path: Path, columns: list[dict]) -> tuple[dict, int] | None` — None if the JSON is not a flat list-of-records
- `merge_columns(columns: list[dict], col_stats: dict) -> list[dict]` — return new columns with stats merged per name (stats keys appended after existing keys)
- `render_columns_block(columns: list[dict]) -> str` — re-render the `"columns": [...]` block in the repo's inline-object style
- `update_card_text(text: str, new_columns: list[dict], row_count: int|None) -> str` — surgical replace of columns block + row_count
- `run(repo: Path, write: bool) -> dict` — sweep tabular cards; returns `{changed:[], skipped:[(id,reason)]}`

---

## Task 1: `column_stats()` (TDD)

**Files:** Create `scripts/compute_value_stats.py`; Test `tests/test_compute_value_stats.py`.

- [ ] **Step 1: failing test** `tests/test_compute_value_stats.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from compute_value_stats import column_stats  # noqa: E402


def test_numeric_column_stats():
    s = column_stats(["2010", "2015", "2023", "", "PRR"], "integer")
    assert s["min"] == 2010
    assert s["max"] == 2023
    assert s["distinct_count"] == 4  # 2010,2015,2023,PRR  (blank excluded)
    assert s["sample_values"] == [2010, 2015, 2023]  # numeric samples, sorted, <=5, non-numeric dropped from samples


def test_string_column_stats_caps_samples():
    s = column_stats(["a", "b", "c", "d", "e", "f", "a"], "string")
    assert s["distinct_count"] == 6
    assert s["sample_values"] == ["a", "b", "c", "d", "e"]  # first-seen, capped at 5
    assert "min" not in s and "max" not in s
```

- [ ] **Step 2: run → FAIL** (`ModuleNotFoundError`). `python -m pytest tests/test_compute_value_stats.py -v`

- [ ] **Step 3: implement** `scripts/compute_value_stats.py`:
```python
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
```

- [ ] **Step 4: run → 2 passed.**
- [ ] **Step 5: commit** `git add scripts/compute_value_stats.py tests/test_compute_value_stats.py && git commit -m "feat(ai-retrieval): add per-column value-stats computation"`

---

## Task 2: `stats_from_csv` / `stats_from_json` (TDD)

- [ ] **Step 1: append tests**:
```python
from compute_value_stats import stats_from_csv, stats_from_json  # noqa: E402


def test_stats_from_csv(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("year,state\n2010,MA\n2011,CA\n2011,MA\n", encoding="utf-8")
    cols = [{"name": "year", "type": "integer"}, {"name": "state", "type": "string"}]
    stats, n = stats_from_csv(p, cols)
    assert n == 3
    assert stats["year"]["min"] == 2010 and stats["year"]["max"] == 2011
    assert stats["state"]["distinct_count"] == 2


def test_stats_from_json_flat_records(tmp_path):
    p = tmp_path / "d.json"
    p.write_text('[{"year":2010,"v":1},{"year":2011,"v":2}]', encoding="utf-8")
    cols = [{"name": "year", "type": "integer"}, {"name": "v", "type": "integer"}]
    stats, n = stats_from_json(p, cols)
    assert n == 2 and stats["year"]["max"] == 2011


def test_stats_from_json_non_tabular_returns_none(tmp_path):
    p = tmp_path / "d.json"
    p.write_text('{"metricA": {"2010": 1, "2011": 2}}', encoding="utf-8")
    assert stats_from_json(p, [{"name": "metricA", "type": "string"}]) is None
```

- [ ] **Step 2: run → FAIL.**
- [ ] **Step 3: implement** — append:
```python
def stats_from_csv(path: Path, columns):
    try:
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csvmod.DictReader(fh))
    except (OSError, UnicodeDecodeError):
        return None
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
```

- [ ] **Step 4: run → 5 passed.**
- [ ] **Step 5: commit** `git add -A && git commit -m "feat(ai-retrieval): add csv/json tabular stats extractors with non-tabular skip"`

---

## Task 3: format-preserving writer `merge_columns` / `render_columns_block` / `update_card_text` (TDD)

- [ ] **Step 1: append tests**:
```python
from compute_value_stats import merge_columns, render_columns_block, update_card_text  # noqa: E402


def test_merge_columns_appends_stats():
    cols = [{"name": "year", "type": "integer", "description": "Y"}]
    merged = merge_columns(cols, {"year": {"distinct_count": 2, "min": 2010, "max": 2011, "sample_values": [2010, 2011]}})
    assert merged[0]["name"] == "year" and merged[0]["description"] == "Y"  # original keys kept + order
    assert merged[0]["min"] == 2010 and merged[0]["distinct_count"] == 2


def test_render_columns_block_inline_style():
    block = render_columns_block([{"name": "a", "type": "integer", "min": 1}])
    assert block == '  "columns": [\n    { "name": "a", "type": "integer", "min": 1 }\n  ]'


def test_update_card_text_replaces_only_columns_and_rowcount():
    text = ('{\n  "id": "x",\n  "row_count": 0,\n'
            '  "columns": [\n    { "name": "a", "type": "integer" }\n  ],\n  "tags": ["t"]\n}\n')
    new = update_card_text(text, [{"name": "a", "type": "integer", "min": 1, "max": 9}], 3)
    assert '"row_count": 3' in new
    assert '{ "name": "a", "type": "integer", "min": 1, "max": 9 }' in new
    assert '"tags": ["t"]' in new  # untouched
    assert '"id": "x"' in new
```

- [ ] **Step 2: run → FAIL.**
- [ ] **Step 3: implement** — append:
```python
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
```

- [ ] **Step 4: run → 8 passed.**
- [ ] **Step 5: commit** `git add -A && git commit -m "feat(ai-retrieval): add format-preserving columns/row_count card writer"`

---

## Task 4: `run()` + `--check` + CLI (TDD)

- [ ] **Step 1: append test**:
```python
import json as _json
from compute_value_stats import run  # noqa: E402


def test_run_writes_csv_card_and_skips_nontabular(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "d.csv").write_text("year\n2010\n2011\n", encoding="utf-8")
    (tmp_path / "data" / "d.csv.meta.json").write_text(
        '{\n  "id": "d",\n  "path": "data/d.csv",\n  "format": "csv",\n'
        '  "columns": [\n    { "name": "year", "type": "integer" }\n  ]\n}\n', encoding="utf-8")
    res = run(tmp_path, write=True)
    assert "data/d.csv.meta.json" in res["changed"]
    card = _json.loads((tmp_path / "data" / "d.csv.meta.json").read_text(encoding="utf-8"))
    assert card["row_count"] == 2
    assert card["columns"][0]["max"] == 2011
    # idempotent
    assert run(tmp_path, write=False)["changed"] == []
```

- [ ] **Step 2: run → FAIL.**
- [ ] **Step 3: implement** — append:
```python
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
```

- [ ] **Step 4: run → 9 passed.**
- [ ] **Step 5: commit** `git add -A && git commit -m "feat(ai-retrieval): add compute_value_stats run() sweep + --check + CLI"`

---

## Task 5: Apply to real cards + verify + regenerate

- [ ] **Step 1:** dry-run `python scripts/compute_value_stats.py --check; echo exit=$?` → `OUT OF DATE: <N>...` exit 1.
- [ ] **Step 2:** apply `python scripts/compute_value_stats.py` → note changed + skipped counts. PASTE the skipped list (which JSON cards were non-tabular).
- [ ] **Step 3: integrity** — `python scripts/validate_catalog.py --strict` → errors: 0. Then prove only columns/row_count changed:
```bash
git diff -U0 -- '*.meta.json' | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | grep -vE '("columns"|row_count|"name":|"type":|"description":|"unit":|sample_values|distinct_count|"min"|"max")' | head -30
```
EXPECTED empty (every changed line is within columns/row_count). PASTE result. If non-empty, STOP/report.
Also spot-check 2 card diffs (`git diff <one csv card>`) show only stats added.
- [ ] **Step 4: regenerate** `python scripts/build_catalog.py && python scripts/build_embeddings.py`; then gates `python scripts/compute_value_stats.py --check && python scripts/build_catalog.py --check && python scripts/build_embeddings.py --check` → all clean.
- [ ] **Step 5:** full suite `python -m pytest tests/ -m "not integration" -q` → all pass.
- [ ] **Step 6:** add `compute_value_stats.py --check` to the CI workflow `.github/workflows/ai-index-check.yml` (append a run step after the build_embeddings check).
- [ ] **Step 7: commit** `git add -A && git commit -m "feat(ai-retrieval): compute value-stats across tabular cards; regenerate + gate"`

---

## Self-Review (author checklist — completed)
**Spec coverage §6:** per-column min/max/distinct/sample (Task 1-2) ✅; row_count (Task 4) ✅; opens real files, skips non-tabular JSON honestly (Task 2,4) ✅; writes into existing columns slots format-preservingly (Task 3) ✅; --check + CI gate (Task 4-5) ✅; re-run builds (Task 5) ✅. (sample_rows card-level deliberately omitted — per-column sample_values covers it without bulk; noted as a conscious scope trim.)
**Placeholder scan:** complete code in every step.
**Type consistency:** `column_stats`/`stats_from_csv`/`stats_from_json`/`merge_columns`/`render_columns_block`/`update_card_text`/`run` signatures consistent across tasks/tests.
**Risk controls:** surgical writer touches only columns block + row_count; non-tabular JSON skipped+reported not forced; validate --strict + grep gate after bulk write; idempotent --check.
