import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _cards import embedding_document  # noqa: E402


def test_embedding_document_composes_fields_in_order():
    card = {
        "title": "SSA Processing Time",
        "description": "Monthly national disability processing time.",
        "tags": ["ssa", "processing-time"],
        "columns": [{"name": "Month"}, {"name": "Days"}],
        "geographic_coverage": "United States (national)",
        "temporal_coverage": {"start": "FY2008", "end": "FY2015"},
    }
    doc = embedding_document(card)
    assert doc == (
        "SSA Processing Time\n"
        "Monthly national disability processing time.\n"
        "Tags: ssa, processing-time\n"
        "Columns: Month, Days\n"
        "Geography: United States (national)\n"
        "Coverage: FY2008–FY2015"
    )


def test_embedding_document_omits_absent_optional_fields():
    card = {"title": "T", "description": "D"}
    assert embedding_document(card) == "T\nD"


from _cards import load_cards  # noqa: E402


def test_load_cards_sweeps_and_sorts(tmp_path):
    (tmp_path / "data" / "z").mkdir(parents=True)
    (tmp_path / "data" / "a").mkdir(parents=True)
    (tmp_path / "data" / "z" / "f.csv.meta.json").write_text(
        '{"id":"z/f","path":"data/z/f.csv","title":"Z"}', encoding="utf-8")
    (tmp_path / "data" / "a" / "g.json.meta.json").write_text(
        '{"id":"a/g","path":"data/a/g.json","title":"A"}', encoding="utf-8")
    cards = load_cards(tmp_path)
    assert [c["path"] for _, c in cards] == ["data/a/g.json", "data/z/f.csv"]
    assert cards[0][0] == "data/a/g.json.meta.json"  # relative posix meta path
