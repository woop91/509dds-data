#!/usr/bin/env python3
"""normalize_tags.py — canonicalize card tags against schemas/tags.vocabulary.json.

Applies ONLY the vocabulary's `aliases` map (duplicate variant -> canonical),
dedupes, and sorts each card's tags. Unmapped tags are PRESERVED and reported
(never dropped). Idempotent. Card tags stay flat (no facet prefixes).

Usage:
  python scripts/normalize_tags.py            # rewrite cards
  python scripts/normalize_tags.py --check     # exit 1 if any card would change
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cards import REPO, load_cards  # noqa: E402

VOCAB_PATH = REPO / "schemas" / "tags.vocabulary.json"


def load_vocab(path: Path = VOCAB_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonicalize(tags: list[str], aliases: dict) -> list[str]:
    seen: list[str] = []
    for t in tags:
        c = aliases.get(t, t)
        if c not in seen:
            seen.append(c)
    return sorted(seen)


def normalize_card(card: dict, aliases: dict):
    tags = card.get("tags")
    if not tags:
        return card, []
    new_tags = canonicalize(tags, aliases)
    known = set(aliases.keys()) | set(aliases.values())
    unmapped = [t for t in new_tags if t not in known]
    if new_tags != tags:
        card = {**card, "tags": new_tags}
    return card, unmapped


def run(repo: Path, aliases: dict, write: bool) -> dict:
    changed = []
    unmapped_counts: dict[str, int] = {}
    for rel_meta, card in load_cards(repo):
        _new_card, unmapped = normalize_card(card, aliases)
        for t in unmapped:
            unmapped_counts[t] = unmapped_counts.get(t, 0) + 1
        new_tags = canonicalize(card.get("tags") or [], aliases) if card.get("tags") else None
        if new_tags is not None and new_tags != card.get("tags"):
            changed.append(rel_meta)
            if write:
                path = repo / rel_meta
                text = path.read_text(encoding="utf-8")
                new_arr = json.dumps(new_tags, ensure_ascii=False)
                new_text, n = re.subn(r'("tags"\s*:\s*)\[[^\]]*\]',
                                      lambda m: m.group(1) + new_arr, text, count=1)
                if n != 1:
                    raise SystemExit(f"could not locate a single tags array in {rel_meta}")
                path.write_text(new_text, encoding="utf-8")
    return {"changed": changed, "unmapped": unmapped_counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if any card would change")
    args = ap.parse_args()
    aliases = load_vocab()["aliases"]
    res = run(REPO, aliases, write=not args.check)
    if args.check:
        if res["changed"]:
            print(f"OUT OF DATE: {len(res['changed'])} cards have non-canonical tags — run scripts/normalize_tags.py")
            sys.exit(1)
        print(f"tags canonical ({len(res['unmapped'])} distinct unmapped tags preserved)")
        return
    print(f"normalized {len(res['changed'])} cards; {len(res['unmapped'])} distinct unmapped tags preserved")


if __name__ == "__main__":
    main()
