"""Shared helpers for loading 509dds-data data cards (*.meta.json)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ["data", "prr-templates"]


def embedding_document(card: dict) -> str:
    """Compose the deterministic text embedded for a card.

    Order is fixed (title, description, tags, columns, geography, coverage) so
    the resulting vector is reproducible. Absent/empty fields are omitted.
    """
    parts = [card.get("title") or "", card.get("description") or ""]
    tags = card.get("tags") or []
    if tags:
        parts.append("Tags: " + ", ".join(tags))
    cols = [c.get("name", "") for c in (card.get("columns") or []) if c.get("name")]
    if cols:
        parts.append("Columns: " + ", ".join(cols))
    geo = card.get("geographic_coverage")
    if geo:
        parts.append("Geography: " + geo)
    tc = card.get("temporal_coverage")
    if isinstance(tc, dict) and (tc.get("start") or tc.get("end")):
        parts.append(f"Coverage: {tc.get('start', '')}–{tc.get('end', '')}")
    return "\n".join(p for p in parts if p)


def load_cards(repo: Path = REPO) -> list[tuple[str, dict]]:
    """Return sorted [(relative_meta_path, card_dict)] for every sidecar."""
    cards: list[tuple[str, dict]] = []
    for d in SOURCE_DIRS:
        base = repo / d
        if not base.exists():
            continue
        for meta in base.rglob("*.meta.json"):
            data = json.loads(meta.read_text(encoding="utf-8"))
            cards.append((meta.relative_to(repo).as_posix(), data))
    cards.sort(key=lambda t: t[1].get("path") or t[0])
    return cards
