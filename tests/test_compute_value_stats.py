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


from compute_value_stats import stats_from_csv, stats_from_json  # noqa: E402


def test_stats_from_csv(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("year,state\n2010,MA\n2011,CA\n2011,MA\n", encoding="utf-8")
    cols = [{"name": "year", "type": "integer"}, {"name": "state", "type": "string"}]
    stats, n = stats_from_csv(p, cols)
    assert n == 3
    assert stats["year"]["min"] == 2010 and stats["year"]["max"] == 2011
    assert stats["state"]["distinct_count"] == 2


def test_stats_from_csv_skips_comment_preamble(tmp_path):
    # Real repo CSVs (mgr/vde salary) carry leading #-comment lines before the header.
    p = tmp_path / "d.csv"
    p.write_text("# note line one\n\"# note line two\"\nyear,state\n2010,MA\n2011,CA\n", encoding="utf-8")
    cols = [{"name": "year", "type": "integer"}, {"name": "state", "type": "string"}]
    stats, n = stats_from_csv(p, cols)
    assert n == 2  # comment lines are NOT counted as data rows
    assert stats["year"]["min"] == 2010 and stats["year"]["max"] == 2011
    assert stats["state"]["distinct_count"] == 2  # column names align with the real header


def test_stats_from_csv_strips_utf8_bom(tmp_path):
    # Real repo CSV (ada-coordinator) has a UTF-8 BOM; first column must still align.
    p = tmp_path / "d.csv"
    p.write_bytes("year,state\n2010,MA\n2011,CA\n".encode("utf-8-sig"))
    cols = [{"name": "year", "type": "integer"}, {"name": "state", "type": "string"}]
    stats, n = stats_from_csv(p, cols)
    assert n == 2
    assert stats["year"]["min"] == 2010  # first column name not mangled by BOM
    assert stats["year"]["distinct_count"] == 2


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
