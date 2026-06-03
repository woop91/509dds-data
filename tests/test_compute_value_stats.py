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
