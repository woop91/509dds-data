import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from normalize_tags import canonicalize, normalize_card  # noqa: E402

ALIASES = {"disability-examiner": "disability-examiners", "seiu-509": "seiu509", "ADA": "ada"}


def test_canonicalize_maps_dedupes_sorts():
    out = canonicalize(["disability-examiner", "disability-examiners", "seiu-509", "ADA"], ALIASES)
    assert out == ["ada", "disability-examiners", "seiu509"]


def test_canonicalize_idempotent():
    once = canonicalize(["disability-examiner", "ADA"], ALIASES)
    assert canonicalize(once, ALIASES) == once


def test_normalize_card_reports_unmapped_and_updates():
    card = {"id": "x", "tags": ["ADA", "novel-tag", "seiu-509"]}
    new, unmapped = normalize_card(card, ALIASES)
    assert new["tags"] == ["ada", "novel-tag", "seiu509"]
    assert unmapped == ["novel-tag"]


def test_normalize_card_no_tags_is_noop():
    card = {"id": "y"}
    new, unmapped = normalize_card(card, ALIASES)
    assert new == {"id": "y"}
    assert unmapped == []
