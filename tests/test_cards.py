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
