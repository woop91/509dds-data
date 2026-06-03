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
