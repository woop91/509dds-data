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


import json as _json
from normalize_tags import run  # noqa: E402


def _write_card(d, rel, tags):
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json.dumps({"id": rel, "path": "data/" + rel.replace(".meta.json", ""),
                              "title": "t", "tags": tags}), encoding="utf-8")


def test_run_check_then_write(tmp_path):
    _write_card(tmp_path, "data/a.csv.meta.json", ["ADA", "ssa"])
    assert "data/a.csv.meta.json" in run(tmp_path, {"ADA": "ada"}, write=False)["changed"]
    run(tmp_path, {"ADA": "ada"}, write=True)
    card = _json.loads((tmp_path / "data/a.csv.meta.json").read_text(encoding="utf-8"))
    assert card["tags"] == ["ada", "ssa"]
    assert run(tmp_path, {"ADA": "ada"}, write=False)["changed"] == []
