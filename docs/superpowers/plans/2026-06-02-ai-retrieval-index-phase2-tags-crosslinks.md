# AI-Retrieval Index — Phase 2 (Controlled Tags + Cross-Links) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Consolidate 783 free-form tags into a controlled, faceted vocabulary (canonicalizing 24 duplicate clusters) and densify `related` cross-links for the 86 zero-link cards — then regenerate the catalog + embedding index so the improvements flow through.

**Architecture:** Conservative + reversible. `schemas/tags.vocabulary.json` is a curated artifact: an objective `aliases` map (duplicate-cluster → canonical) plus `facets` grouping canonical tags (documentation + faceted-retrieval substrate). `normalize_tags.py` applies ONLY the alias map to cards (canonicalize + dedupe + sort), preserves unmapped tags, reports them, and is idempotent with `--check`. `suggest_related.py` proposes/auto-applies only high-confidence same-directory sibling edges and reports the rest. Card tags stay FLAT (no facet-prefix mangling). After each card change, `build_catalog.py` + `build_embeddings.py` are re-run.

**Tech Stack:** Python 3, `numpy`/`fastembed` (only for the re-run), `pytest`.

**Spec:** `docs/superpowers/specs/2026-06-02-ai-retrieval-index-design.md` §5.

---

## File Structure

| File | Responsibility |
|---|---|
| `schemas/tags.vocabulary.json` (create) | Curated controlled vocabulary: `aliases` (dup→canonical) + `facets` (canonical→category) |
| `scripts/normalize_tags.py` (create) | Apply aliases to all cards, dedupe+sort tags, report unmapped; `--check` |
| `scripts/suggest_related.py` (create) | Propose related edges for zero-link cards; auto-apply same-dir siblings; report rest |
| `tests/test_normalize_tags.py` (create) | Unit tests (hermetic tmp fixtures) |
| `tests/test_suggest_related.py` (create) | Unit tests (hermetic tmp fixtures) |
| `reports/related-suggestions.json` (generated) | Lower-confidence related suggestions for human review |

**Shared interfaces:**
- `normalize_tags.load_vocab(path) -> dict`
- `normalize_tags.canonicalize(tags: list[str], aliases: dict) -> list[str]` — map via aliases, dedupe preserving first occurrence, then sort
- `normalize_tags.normalize_card(card: dict, aliases: dict) -> tuple[dict, list[str]]` — returns (possibly-updated card, unmapped tags)
- `normalize_tags.run(repo, aliases, write: bool) -> dict` — sweep cards; returns `{changed:[paths], unmapped:{tag:count}}`
- `suggest_related.collection_dir(path) -> str` — immediate parent dir of the data file
- `suggest_related.propose(cards) -> dict` — returns `{auto:[(idA,idB)...], review:[...]}`

---

## Task 1: `tags.vocabulary.json` (curated artifact)

**Files:** Create `schemas/tags.vocabulary.json`.

- [ ] **Step 1: Write the vocabulary file**

`schemas/tags.vocabulary.json` — EXACT content:
```json
{
  "$comment": "Controlled tag vocabulary for 509dds-data. 'aliases' canonicalize duplicate tag variants (frequency-wins, cleaner-form tie-break). 'facets' group canonical tags for faceted retrieval. Card tags stay FLAT; normalize_tags.py applies aliases only and preserves unmapped tags. Regenerate downstream with build_catalog.py + build_embeddings.py.",
  "aliases": {
    "ADA": "ada",
    "chapters": "chapter",
    "compassionate-allowances": "compassionate-allowance",
    "constitutions": "constitution",
    "CSC": "csc",
    "disability-examiner": "disability-examiners",
    "DOL": "dol",
    "EEOC": "eeoc",
    "filing-deadline": "filing-deadlines",
    "FLSA": "flsa",
    "FMLA": "fmla",
    "mcad": "MCAD",
    "NLRA": "nlra",
    "NLRB": "nlrb",
    "PFML": "pfml",
    "position-papers": "position-paper",
    "processing-times": "processing-time",
    "public-records": "public-record",
    "region": "regions",
    "SCADE": "scade",
    "seiu-509": "seiu509",
    "states": "state",
    "wait-times": "wait-time",
    "weingarten": "Weingarten"
  },
  "facets": {
    "agency": ["ssa", "dds", "mrc", "massability", "nade", "eeoc", "MCAD", "nlrb", "ssa-oig", "gao", "dol"],
    "geo": ["massachusetts", "national", "peer-states", "northeast-region", "southeast-region", "pacific-region", "southwest-region", "mid-atlantic-region", "great-lakes-region", "by-state", "state", "california", "washington"],
    "topic": ["pay-scales", "salary", "processing-time", "backlog", "wait-time", "staffing", "governance", "chapter-governance", "oversight", "disability-determination", "claims-processing", "reasonable-accommodation", "collective-bargaining", "labor-rights", "discrimination", "workload", "hearings", "allowance-rate", "payroll", "civil-service", "vocational-rehabilitation", "training", "advocacy"],
    "doc-type": ["bylaws", "constitution", "cba", "research-notes", "annual-report", "salary-chart", "position-paper", "public-record", "summary", "index", "stub", "leadership-research", "contacts"],
    "tier": ["authoritative", "computed", "browser-fetch-pending", "structurally-unavailable", "estimate", "blocked"],
    "entity": ["seiu509", "afscme", "vde", "dds-det", "unit-8", "union", "members", "disability-examiners", "public-sector", "MA-public-sector", "state-employees"]
  }
}
```

- [ ] **Step 2: Validate it parses + alias map has no cycles (canonical not itself an alias key)**

Run: `python -c "import json; v=json.load(open('schemas/tags.vocabulary.json')); a=v['aliases']; assert all(canon not in a for canon in a.values()), 'alias targets must be terminal'; print('aliases',len(a),'facets',sum(len(x) for x in v['facets'].values()))"`
Expected: `aliases 24 facets <N>` and no assertion error.

- [ ] **Step 3: Commit**

```bash
git add schemas/tags.vocabulary.json
git commit -m "feat(ai-retrieval): add curated controlled tag vocabulary"
```

---

## Task 2: `canonicalize()` + `normalize_card()` (TDD)

**Files:** Create `scripts/normalize_tags.py`; Test `tests/test_normalize_tags.py`.

- [ ] **Step 1: Write the failing test**

`tests/test_normalize_tags.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from normalize_tags import canonicalize, normalize_card  # noqa: E402

ALIASES = {"disability-examiner": "disability-examiners", "seiu-509": "seiu509", "ADA": "ada"}


def test_canonicalize_maps_dedupes_sorts():
    # 'disability-examiner' -> 'disability-examiners' which is already present -> dedupe
    out = canonicalize(["disability-examiner", "disability-examiners", "seiu-509", "ADA"], ALIASES)
    assert out == ["ada", "disability-examiners", "seiu509"]


def test_canonicalize_idempotent():
    once = canonicalize(["disability-examiner", "ADA"], ALIASES)
    assert canonicalize(once, ALIASES) == once


def test_normalize_card_reports_unmapped_and_updates():
    card = {"id": "x", "tags": ["ADA", "novel-tag", "seiu-509"]}
    new, unmapped = normalize_card(card, ALIASES)
    assert new["tags"] == ["ada", "novel-tag", "seiu509"]
    assert unmapped == ["novel-tag"]  # not in aliases, not a known canonical here -> reported, kept


def test_normalize_card_no_tags_is_noop():
    card = {"id": "y"}
    new, unmapped = normalize_card(card, ALIASES)
    assert new == {"id": "y"}
    assert unmapped == []
```

- [ ] **Step 2: Run test — expect FAIL** (`ModuleNotFoundError: normalize_tags`)

Run: `python -m pytest tests/test_normalize_tags.py -v`

- [ ] **Step 3: Implement**

`scripts/normalize_tags.py`:
```python
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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cards import REPO, load_cards  # noqa: E402

VOCAB_PATH = REPO / "schemas" / "tags.vocabulary.json"


def load_vocab(path: Path = VOCAB_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonicalize(tags: list[str], aliases: dict) -> list[str]:
    seen = []
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
    facet_terms = set()  # set by run(); here unmapped = canonical tags absent from any facet
    unmapped = [t for t in new_tags if t in _UNKNOWN] if _UNKNOWN else []
    if new_tags != tags:
        card = {**card, "tags": new_tags}
    return card, unmapped


_UNKNOWN: set | None = None
```

NOTE: the `_UNKNOWN`/`facet_terms` machinery is wired in Task 3 (run() sets the set of "known" canonical tags from the facets so unmapped reporting reflects the vocabulary). For THIS task's tests, `normalize_card` must report a tag as unmapped when it is neither an alias key nor a known canonical. Implement the minimal version that satisfies the tests: a tag is "unmapped" if it is not a value in `aliases` and not an alias key. Replace the `_UNKNOWN` lines above with:
```python
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
```
(Delete the `_UNKNOWN`/`facet_terms` stub lines.)

- [ ] **Step 4: Run test — expect 4 passed**

Run: `python -m pytest tests/test_normalize_tags.py -v`

- [ ] **Step 5: Commit**

```bash
git add scripts/normalize_tags.py tests/test_normalize_tags.py
git commit -m "feat(ai-retrieval): add tag canonicalize + normalize_card"
```

---

## Task 3: `run()` sweep + `--check` + CLI (TDD)

**Files:** Modify `scripts/normalize_tags.py`; Test `tests/test_normalize_tags.py`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_normalize_tags.py`:
```python
import json as _json
from normalize_tags import run  # noqa: E402


def _write_card(d, rel, tags):
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json.dumps({"id": rel, "path": "data/" + rel.replace(".meta.json", ""),
                              "title": "t", "tags": tags}), encoding="utf-8")


def test_run_check_then_write(tmp_path):
    _write_card(tmp_path, "data/a.csv.meta.json", ["ADA", "ssa"])
    res_check = run(tmp_path, {"ADA": "ada"}, write=False)
    assert "data/a.csv.meta.json" in res_check["changed"]  # would change
    # write mode applies it
    run(tmp_path, {"ADA": "ada"}, write=True)
    card = _json.loads((tmp_path / "data/a.csv.meta.json").read_text(encoding="utf-8"))
    assert card["tags"] == ["ada", "ssa"]
    # now check is clean (idempotent)
    assert run(tmp_path, {"ADA": "ada"}, write=False)["changed"] == []
```

- [ ] **Step 2: Run test — expect FAIL** (`ImportError: cannot import name 'run'`)

- [ ] **Step 3: Implement** — append to `scripts/normalize_tags.py`:
```python
def run(repo: Path, aliases: dict, write: bool) -> dict:
    changed = []
    unmapped_counts: dict[str, int] = {}
    for rel_meta, card in load_cards(repo):
        new_card, unmapped = normalize_card(card, aliases)
        for t in unmapped:
            unmapped_counts[t] = unmapped_counts.get(t, 0) + 1
        if new_card is not card and new_card.get("tags") != card.get("tags"):
            changed.append(rel_meta)
            if write:
                p = repo / rel_meta
                p.write_text(json.dumps(new_card, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    return {"changed": changed, "unmapped": unmapped_counts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if any card would change")
    args = ap.parse_args()
    vocab = load_vocab()
    aliases = vocab["aliases"]
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
```

IMPORTANT: card-writing must preserve the existing on-disk formatting style as closely as possible. The existing cards are pretty-printed JSON with 2-space indent. Using `json.dumps(..., indent=2) + "\n"` matches that. **However**, the original cards may have a specific key order and a leading `$schema` key — `load_cards` returns the parsed dict which preserves insertion order, and `{**card, "tags": ...}` keeps order while replacing tags in place only if `tags` already exists (it does for all 277). Verify on a real card in Task 4 before bulk write.

- [ ] **Step 4: Run test — expect 5 passed**

- [ ] **Step 5: Commit**

```bash
git add scripts/normalize_tags.py tests/test_normalize_tags.py
git commit -m "feat(ai-retrieval): add normalize_tags run() sweep + --check + CLI"
```

---

## Task 4: Apply normalization to real cards + regenerate + verify

**Files:** rewrites tag arrays in affected cards under `data/`, `prr-templates/`; regenerates `catalog.json`, `llms.txt`, `embeddings/*`.

- [ ] **Step 1: Dry-run check (see scope before writing)**

Run: `python scripts/normalize_tags.py --check; echo "exit=$?"`
Expected: `OUT OF DATE: <N> cards ...` exit 1 (N>0, the cards with dup-variant tags).

- [ ] **Step 2: Inspect ONE affected card's diff shape before bulk write**

Pick one card known to contain a dup variant (e.g. any with `disability-examiner`). Manually confirm `normalize_tags` would only change its `tags` array and preserve all other keys + ordering. Run a targeted python check:
```bash
python -c "import sys,json; sys.path.insert(0,'scripts'); from _cards import load_cards; from normalize_tags import load_vocab, normalize_card; a=load_vocab()['aliases']; \
import itertools; \
[print(rel, '\n OLD', c.get('tags'), '\n NEW', normalize_card(c,a)[0].get('tags')) for rel,c in load_cards() if normalize_card(c,a)[0].get('tags')!=c.get('tags')][:1]"
```
Confirm only tags change.

- [ ] **Step 3: Apply**

Run: `python scripts/normalize_tags.py`
Expected: `normalized <N> cards; <M> distinct unmapped tags preserved`.

- [ ] **Step 4: Verify card integrity (no key loss, valid JSON, schema still valid)**

Run: `python scripts/validate_catalog.py --strict`
Expected: `errors: 0` exit 0.
Run: `git diff --stat` — confirm ONLY `.meta.json` files changed and each change is within the `tags` array (spot-check 2-3 with `git diff <file>`).

- [ ] **Step 5: Regenerate downstream indexes**

Run: `python scripts/build_catalog.py && python scripts/build_embeddings.py`
Expected: `wrote catalog.json + llms.txt (277 datasets)` and `wrote embeddings/index.bin + manifest.json (277 vectors, dim 384)`.
Run all gates: `python scripts/normalize_tags.py --check && python scripts/build_catalog.py --check && python scripts/build_embeddings.py --check`
Expected: all clean.

- [ ] **Step 6: Run full test suite**

Run: `python -m pytest tests/ -m "not integration" -q` → all pass.

- [ ] **Step 7: Commit (cards + regenerated artifacts together)**

```bash
git add -A
git commit -m "feat(ai-retrieval): canonicalize tags across cards; regenerate catalog + index"
```

---

## Task 5: `suggest_related.py` — same-dir sibling densification (TDD)

**Files:** Create `scripts/suggest_related.py`; Test `tests/test_suggest_related.py`.

- [ ] **Step 1: Write the failing test**

`tests/test_suggest_related.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from suggest_related import collection_dir, propose  # noqa: E402


def test_collection_dir():
    assert collection_dir("data/pay-scales/peer-states/CA/scheduled-rates.json") == "data/pay-scales/peer-states/CA"


def test_propose_links_same_dir_siblings_only():
    cards = [
        ("m1", {"id": "a", "path": "data/x/a.json", "related": []}),
        ("m2", {"id": "b", "path": "data/x/b.json", "related": []}),
        ("m3", {"id": "c", "path": "data/y/c.json", "related": ["a"]}),
    ]
    res = propose(cards)
    # a and b are same-dir siblings, both zero-link -> auto bidirectional
    assert ("a", "b") in [tuple(sorted(p)) for p in res["auto"]]
    # c is in a different dir and already has a link -> not auto-linked to a/b
    assert all("c" not in pair for pair in res["auto"])
```

- [ ] **Step 2: Run test — expect FAIL** (`ModuleNotFoundError: suggest_related`)

- [ ] **Step 3: Implement**

`scripts/suggest_related.py`:
```python
#!/usr/bin/env python3
"""suggest_related.py — densify `related` edges for zero-link cards.

Auto-applies ONLY high-confidence same-directory sibling edges (cards whose data
files share an immediate parent directory). Lower-confidence suggestions (shared
tags across directories) are written to reports/related-suggestions.json for
human review — never auto-applied.

Usage:
  python scripts/suggest_related.py            # apply same-dir siblings + write report
  python scripts/suggest_related.py --check     # exit 1 if same-dir edges are missing
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cards import REPO, load_cards  # noqa: E402

REPORT_PATH = REPO / "reports" / "related-suggestions.json"


def collection_dir(path: str) -> str:
    return path.rsplit("/", 1)[0]


def propose(cards):
    by_id = {c.get("id"): c for _, c in cards}
    dirs: dict[str, list] = {}
    for _, c in cards:
        dirs.setdefault(collection_dir(c.get("path", "")), []).append(c.get("id"))
    auto = []
    review = []
    for d, ids in dirs.items():
        if len(ids) < 2:
            continue
        for a, b in combinations(sorted(ids), 2):
            ca, cb = by_id[a], by_id[b]
            a_links = b in (ca.get("related") or [])
            b_links = a in (cb.get("related") or [])
            # auto only when BOTH currently have no link to the other AND at least
            # one of them is a zero-link card (densify the sparse ones)
            zero = not (ca.get("related")) or not (cb.get("related"))
            if not (a_links and b_links) and zero:
                auto.append((a, b))
    return {"auto": auto, "review": review}
```

- [ ] **Step 4: Run test — expect 2 passed**

- [ ] **Step 5: Commit**

```bash
git add scripts/suggest_related.py tests/test_suggest_related.py
git commit -m "feat(ai-retrieval): add suggest_related same-dir sibling proposer"
```

---

## Task 6: Apply related edges + report + regenerate + verify

- [ ] **Step 1: Add apply + report + CLI to `scripts/suggest_related.py`**

Append:
```python
def apply_auto(repo: Path, cards, auto) -> list[str]:
    by_id = {c.get("id"): (rel, c) for rel, c in cards}
    changed = set()
    for a, b in auto:
        for x, y in ((a, b), (b, a)):
            rel, c = by_id[x]
            rel_list = list(c.get("related") or [])
            if y not in rel_list:
                rel_list.append(y)
                c["related"] = sorted(rel_list)
                changed.add(rel)
    for rel in changed:
        _, c = by_id[[i for i, (r, _c) in by_id.items() if r == rel][0]] if False else (None, None)
    # simpler: rewrite each changed card from by_id
    for x, (rel, c) in by_id.items():
        if rel in changed:
            (repo / rel).write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(changed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    cards = load_cards(REPO)
    res = propose(cards)
    if args.check:
        # check = no same-dir sibling edge missing
        missing = []
        by_id = {c.get("id"): c for _, c in cards}
        for a, b in res["auto"]:
            if b not in (by_id[a].get("related") or []) or a not in (by_id[b].get("related") or []):
                missing.append((a, b))
        if missing:
            print(f"OUT OF DATE: {len(missing)} same-dir related edges missing — run scripts/suggest_related.py")
            sys.exit(1)
        print("related edges up to date")
        return
    changed = apply_auto(REPO, cards, res["auto"])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps({"review": res["review"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"applied same-dir related edges to {len(changed)} cards; review file: {REPORT_PATH.relative_to(REPO)}")


if __name__ == "__main__":
    main()
```
NOTE: simplify `apply_auto` if the engineer sees a cleaner form — the contract is: for each auto pair (a,b), ensure a∈related(b) and b∈related(a), sorted+deduped, rewrite only changed cards, return changed rel-paths. The convoluted middle loop above is a stub — REPLACE it with the clean version:
```python
def apply_auto(repo: Path, cards, auto) -> list[str]:
    by_id = {c.get("id"): (rel, c) for rel, c in cards}
    changed = set()
    for a, b in auto:
        for x, y in ((a, b), (b, a)):
            rel, c = by_id[x]
            rel_list = list(c.get("related") or [])
            if y not in rel_list:
                c["related"] = sorted(rel_list + [y])
                changed.add(rel)
    for rel, c in by_id.values():
        if rel in changed:
            (repo / rel).write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sorted(changed)
```

- [ ] **Step 2: Apply + verify integrity**

Run: `python scripts/suggest_related.py`
Then: `python scripts/validate_catalog.py --strict` → `errors: 0`.
`git diff --stat` — confirm only `.meta.json` files + the new `reports/related-suggestions.json` changed; spot-check 2 card diffs show only `related` array growth.

- [ ] **Step 3: Regenerate + gates**

Run: `python scripts/build_catalog.py && python scripts/build_embeddings.py`
Run: `python scripts/build_catalog.py --check && python scripts/build_embeddings.py --check && python scripts/suggest_related.py --check && python scripts/normalize_tags.py --check`
Expected: all clean.

- [ ] **Step 4: Full suite**

Run: `python -m pytest tests/ -m "not integration" -q` → all pass.

- [ ] **Step 5: Commit + push**

```bash
git add -A
git commit -m "feat(ai-retrieval): densify same-dir related edges; regenerate catalog + index"
git push
```

---

## Self-Review (author checklist — completed)

**Spec coverage (§5):** controlled vocabulary (Task 1) ✅; normalize_tags map+rewrite+report-unmapped+idempotent (Tasks 2-4) ✅; densify related with human-review report (Tasks 5-6) ✅; re-run builds (Tasks 4,6) ✅.

**Placeholder scan:** Tasks 3 and 6 include explicit stub-replacement notes with the clean final code — the engineer must use the clean version (clearly marked). No TBD.

**Risk controls:** card writes preserve key order via `{**card,...}` / in-place dict mutation; only `tags`/`related` arrays change; unmapped tags preserved; validate_catalog --strict gates integrity after each bulk write; related auto-apply restricted to same-directory siblings; lower-confidence suggestions reported, not applied.

**Type consistency:** `load_vocab`/`canonicalize`/`normalize_card`/`run` and `collection_dir`/`propose`/`apply_auto` signatures consistent across tasks and tests.
