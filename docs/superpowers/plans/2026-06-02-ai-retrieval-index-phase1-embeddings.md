# AI-Retrieval Index — Phase 1 (Semantic/Embedding Index) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a self-contained semantic search layer over the 277 `.meta.json` data cards — a committed vector index plus a Python query CLI — so an AI (or the 509dds.com site, repo-as-database) retrieves datasets by meaning with no API key.

**Architecture:** Mirror the existing `build_catalog.py` pattern: sweep all cards → compose a deterministic per-card "embedding document" → embed offline with `BAAI/bge-small-en-v1.5` (ONNX via `fastembed`) → write `embeddings/index.bin` (packed Float32, L2-normalized) + `embeddings/manifest.json`. A `search.py` CLI embeds a query and ranks by cosine (== dot product on normalized vectors). The embedder is dependency-injected so all logic is unit-tested with a stub; one guarded integration test runs the real model. A `--check` mode prevents drift, gated in CI.

**Tech Stack:** Python 3, `fastembed` (ONNX, no PyTorch), `numpy`, `pytest`. Reference-only for the website consumer (not installed here): `@xenova/transformers`.

**Spec:** `docs/superpowers/specs/2026-06-02-ai-retrieval-index-design.md` (§4).

**Scope of THIS plan:** Phase 1 only. Phases 2 (controlled tags + cross-links), 3 (value-stats), 4 (peer-state acquisition) get their own plans authored after Phase 1 lands, so they can target the real `build_embeddings.py` interfaces and re-run the build.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/_cards.py` (create) | Shared card loading + the deterministic `embedding_document(card)` composer |
| `scripts/build_embeddings.py` (create) | Build the vector artifact from cards; `--check`; real `fastembed` embedder |
| `scripts/search.py` (create) | Query CLI: embed query → cosine → top-k card hits |
| `scripts/requirements.txt` (create) | `fastembed`, `numpy` (build/CLI deps) |
| `embeddings/index.bin` (generated, committed) | `N×384` packed Float32 LE vectors, manifest order |
| `embeddings/manifest.json` (generated, committed) | model/dim/instruction + per-vector `{id,path,title,tags}` |
| `embeddings/README.md` (create) | Retrieval protocol + JS (`@xenova/transformers`) reference snippet |
| `tests/test_cards.py` (create) | Unit tests for `_cards` |
| `tests/test_build_embeddings.py` (create) | Unit tests (stub embedder) + 1 guarded integration test |
| `tests/test_search.py` (create) | Unit tests (stub) + 1 guarded integration test |
| `scripts/build_catalog.py` (modify) | Add one-line semantic-retrieval pointer to `LLMS_HEADER` |
| `.github/workflows/ai-index-check.yml` (create) | Self-contained gate: validate + all `--check`s |

**Shared interfaces (defined once, used across tasks):**
- `_cards.load_cards(repo: Path) -> list[tuple[str, dict]]` — sorted `(rel_meta_path, card)`
- `_cards.embedding_document(card: dict) -> str`
- `build_embeddings.embed_texts(texts: list[str]) -> np.ndarray` — passages, real model, `(n,384)` normalized
- `build_embeddings.embed_query(query: str) -> np.ndarray` — `(384,)`, real model, query-instruction prefix
- `build_embeddings.build(cards, embedder=embed_texts) -> tuple[np.ndarray, dict]`
- `build_embeddings.pack(vecs) -> bytes` / `unpack(blob, dim) -> np.ndarray`
- `build_embeddings.write_artifact(vecs, manifest, out_dir: Path) -> None`
- `build_embeddings.load_artifact(out_dir: Path) -> tuple[np.ndarray, dict]`
- `build_embeddings.check(cards, out_dir, embedder=embed_texts, atol=1e-5) -> list[str]`
- `search.search(query, vectors, manifest, embedder, k=8) -> list[dict]`

Constants in `build_embeddings.py`: `MODEL = "BAAI/bge-small-en-v1.5"`, `MODEL_JS = "Xenova/bge-small-en-v1.5"`, `DIM = 384`, `QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "`, `OUT_DIR = REPO / "embeddings"`.

---

## Task 0: Scaffolding (deps + dirs)

**Files:**
- Create: `scripts/requirements.txt`
- Create: `embeddings/` (dir, via the artifact later)

- [ ] **Step 1: Write requirements file**

`scripts/requirements.txt`:
```
fastembed>=0.3.0
numpy>=1.24
```

- [ ] **Step 2: Install deps into the working environment**

Run: `pip install -r scripts/requirements.txt pytest`
Expected: installs succeed (fastembed pulls `onnxruntime`; no PyTorch).

- [ ] **Step 3: Commit**

```bash
git add scripts/requirements.txt
git commit -m "chore(ai-retrieval): add fastembed+numpy requirements for embeddings"
```

---

## Task 1: `embedding_document(card)` — deterministic text per card

**Files:**
- Create: `scripts/_cards.py`
- Test: `tests/test_cards.py`

- [ ] **Step 1: Write the failing test**

`tests/test_cards.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cards.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named '_cards'`.

- [ ] **Step 3: Write minimal implementation**

`scripts/_cards.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cards.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/_cards.py tests/test_cards.py
git commit -m "feat(ai-retrieval): add embedding_document card-text composer"
```

---

## Task 2: `load_cards(repo)` — sweep + sort sidecars

**Files:**
- Modify: `scripts/_cards.py`
- Test: `tests/test_cards.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cards.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cards.py::test_load_cards_sweeps_and_sorts -v`
Expected: FAIL — `ImportError: cannot import name 'load_cards'`.

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/_cards.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cards.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/_cards.py tests/test_cards.py
git commit -m "feat(ai-retrieval): add load_cards sidecar sweep"
```

---

## Task 3: `build()` + `pack()`/`unpack()` (stub embedder)

**Files:**
- Create: `scripts/build_embeddings.py`
- Test: `tests/test_build_embeddings.py`

- [ ] **Step 1: Write the failing test**

`tests/test_build_embeddings.py`:
```python
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_embeddings as be  # noqa: E402

DIM = be.DIM


def _stub(texts):
    """Deterministic fake embedder: vector seeded by text length, normalized."""
    out = np.zeros((len(texts), DIM), dtype=np.float32)
    for i, t in enumerate(texts):
        out[i, len(t) % DIM] = 1.0  # unit vector along one axis
    return out


def _cards():
    return [
        ("data/a.csv.meta.json", {"id": "a", "path": "data/a.csv", "title": "Alpha",
                                  "description": "first", "tags": ["x"]}),
        ("data/b.csv.meta.json", {"id": "b", "path": "data/b.csv", "title": "Beta",
                                  "description": "second", "tags": ["y"]}),
    ]


def test_build_returns_vectors_and_manifest_in_card_order():
    vecs, manifest = be.build(_cards(), embedder=_stub)
    assert vecs.shape == (2, DIM)
    assert vecs.dtype == np.float32
    assert manifest["count"] == 2
    assert manifest["dim"] == DIM
    assert manifest["model"] == be.MODEL
    assert [v["id"] for v in manifest["vectors"]] == ["a", "b"]
    assert manifest["vectors"][0]["path"] == "data/a.csv"
    assert manifest["vectors"][0]["tags"] == ["x"]


def test_pack_unpack_roundtrip():
    vecs, _ = be.build(_cards(), embedder=_stub)
    blob = be.pack(vecs)
    assert len(blob) == 2 * DIM * 4  # float32
    back = be.unpack(blob, DIM)
    assert np.array_equal(back, vecs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build_embeddings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_embeddings'`.

- [ ] **Step 3: Write minimal implementation**

`scripts/build_embeddings.py`:
```python
#!/usr/bin/env python3
"""build_embeddings.py — build the semantic vector index from data cards.

Sweeps every <file>.meta.json, composes a deterministic embedding document per
card, embeds it offline with BAAI/bge-small-en-v1.5 (ONNX via fastembed), and
writes embeddings/index.bin (packed Float32, L2-normalized) + manifest.json.

Usage:
  python scripts/build_embeddings.py            # write the artifact
  python scripts/build_embeddings.py --check     # exit 1 if it would change
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cards import REPO, embedding_document, load_cards  # noqa: E402

MODEL = "BAAI/bge-small-en-v1.5"
MODEL_JS = "Xenova/bge-small-en-v1.5"
DIM = 384
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
OUT_DIR = REPO / "embeddings"

_embedder = None  # lazy fastembed singleton


def _normalize(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vecs / norms).astype(np.float32)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed passages with the real model. Lazy-loads fastembed."""
    global _embedder
    if _embedder is None:
        from fastembed import TextEmbedding
        _embedder = TextEmbedding(model_name=MODEL)
    vecs = np.array(list(_embedder.embed(texts)), dtype=np.float32)
    return _normalize(vecs)


def build(cards, embedder=embed_texts):
    docs = [embedding_document(c) for _, c in cards]
    vecs = embedder(docs)
    vectors = [
        {"id": c.get("id"), "path": c.get("path"), "title": c.get("title"),
         "tags": c.get("tags") or []}
        for _, c in cards
    ]
    manifest = {
        "$comment": "Semantic index for 509dds-data. Generated by scripts/build_embeddings.py.",
        "model": MODEL,
        "model_js": MODEL_JS,
        "dim": DIM,
        "normalized": True,
        "query_instruction": QUERY_INSTRUCTION,
        "count": len(vectors),
        "vectors": vectors,
    }
    return vecs, manifest


def pack(vecs: np.ndarray) -> bytes:
    return vecs.astype("<f4").tobytes()


def unpack(blob: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(blob, dtype="<f4").reshape(-1, dim).copy()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_build_embeddings.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_embeddings.py tests/test_build_embeddings.py
git commit -m "feat(ai-retrieval): add build() + pack/unpack vector core"
```

---

## Task 4: `write_artifact()` + `load_artifact()`

**Files:**
- Modify: `scripts/build_embeddings.py`
- Test: `tests/test_build_embeddings.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build_embeddings.py`:
```python
def test_write_then_load_artifact_roundtrips(tmp_path):
    vecs, manifest = be.build(_cards(), embedder=_stub)
    be.write_artifact(vecs, manifest, tmp_path)
    assert (tmp_path / "index.bin").exists()
    assert (tmp_path / "manifest.json").exists()
    loaded_vecs, loaded_manifest = be.load_artifact(tmp_path)
    assert np.array_equal(loaded_vecs, vecs)
    assert loaded_manifest["count"] == 2
    assert loaded_manifest["vectors"][1]["id"] == "b"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build_embeddings.py::test_write_then_load_artifact_roundtrips -v`
Expected: FAIL — `AttributeError: module 'build_embeddings' has no attribute 'write_artifact'`.

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/build_embeddings.py`:
```python
def write_artifact(vecs: np.ndarray, manifest: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.bin").write_bytes(pack(vecs))
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_artifact(out_dir: Path):
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    vecs = unpack((out_dir / "index.bin").read_bytes(), manifest["dim"])
    return vecs, manifest
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_build_embeddings.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_embeddings.py tests/test_build_embeddings.py
git commit -m "feat(ai-retrieval): add write/load artifact helpers"
```

---

## Task 5: `check()` + CLI main

**Files:**
- Modify: `scripts/build_embeddings.py`
- Test: `tests/test_build_embeddings.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build_embeddings.py`:
```python
def test_check_clean_then_detects_drift(tmp_path):
    cards = _cards()
    vecs, manifest = be.build(cards, embedder=_stub)
    be.write_artifact(vecs, manifest, tmp_path)
    # clean: rebuild matches committed artifact
    assert be.check(cards, tmp_path, embedder=_stub) == []
    # drift: a card's text changes -> stub yields a different axis -> changed
    cards[0][1]["description"] = "first edited longer description text"
    changed = be.check(cards, tmp_path, embedder=_stub)
    assert "index.bin" in changed
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build_embeddings.py::test_check_clean_then_detects_drift -v`
Expected: FAIL — `AttributeError: ... has no attribute 'check'`.

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/build_embeddings.py`:
```python
def check(cards, out_dir=OUT_DIR, embedder=embed_texts, atol=1e-5):
    """Return list of artifact files that a rebuild would change ([] = up to date)."""
    new_vecs, new_manifest = build(cards, embedder=embedder)
    changed = []
    if not (out_dir / "index.bin").exists() or not (out_dir / "manifest.json").exists():
        return ["index.bin", "manifest.json"]
    old_vecs, old_manifest = load_artifact(out_dir)
    if old_vecs.shape != new_vecs.shape or not np.allclose(old_vecs, new_vecs, atol=atol):
        changed.append("index.bin")
    # compare manifest ignoring the float vectors (compared above)
    if json.dumps(old_manifest, sort_keys=True) != json.dumps(new_manifest, sort_keys=True):
        if "manifest.json" not in changed:
            changed.append("manifest.json")
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if the artifact would change")
    args = ap.parse_args()
    cards = load_cards()
    if args.check:
        changed = check(cards, OUT_DIR)
        if changed:
            print(f"OUT OF DATE: {', '.join(changed)} — run scripts/build_embeddings.py")
            sys.exit(1)
        print(f"up to date ({len(cards)} cards embedded)")
        return
    vecs, manifest = build(cards)
    write_artifact(vecs, manifest, OUT_DIR)
    print(f"wrote embeddings/index.bin + manifest.json ({manifest['count']} vectors, dim {DIM})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_build_embeddings.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/build_embeddings.py tests/test_build_embeddings.py
git commit -m "feat(ai-retrieval): add --check drift detection + CLI main"
```

---

## Task 6: Integration test — real `fastembed` embedder

**Files:**
- Modify: `scripts/build_embeddings.py` (add `embed_query`)
- Test: `tests/test_build_embeddings.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_build_embeddings.py`:
```python
import pytest


@pytest.mark.integration
def test_real_embedder_shape_norm_determinism():
    pytest.importorskip("fastembed")
    texts = ["disability examiner pay scale", "ssa processing time"]
    a = be.embed_texts(texts)
    assert a.shape == (2, be.DIM)
    assert np.allclose(np.linalg.norm(a, axis=1), 1.0, atol=1e-4)  # normalized
    b = be.embed_texts(texts)
    assert np.allclose(a, b, atol=1e-5)  # deterministic
    q = be.embed_query("how much do examiners earn")
    assert q.shape == (be.DIM,)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_build_embeddings.py::test_real_embedder_shape_norm_determinism -v`
Expected: FAIL — `AttributeError: ... has no attribute 'embed_query'` (downloads model on first import of fastembed; allow time).

- [ ] **Step 3: Write minimal implementation**

Append to `scripts/build_embeddings.py`:
```python
def embed_query(query: str) -> np.ndarray:
    """Embed a single search query (with the bge query instruction)."""
    vec = embed_texts([QUERY_INSTRUCTION + query])
    return vec[0]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_build_embeddings.py -v -m integration`
Expected: PASS (1 passed) — first run downloads ~130 MB ONNX model; subsequent runs are fast.
Also run full unit set: `pytest tests/test_build_embeddings.py -v -m "not integration"` → 4 passed.

- [ ] **Step 5: Register the marker + commit**

Create `pytest.ini`:
```ini
[pytest]
markers =
    integration: tests that load the real fastembed model (slow, network on first run)
```

```bash
git add scripts/build_embeddings.py tests/test_build_embeddings.py pytest.ini
git commit -m "feat(ai-retrieval): add embed_query + real-model integration test"
```

---

## Task 7: Generate + commit the real artifact

**Files:**
- Create (generated): `embeddings/index.bin`, `embeddings/manifest.json`

- [ ] **Step 1: Build the artifact against all 277 cards**

Run: `python scripts/build_embeddings.py`
Expected: `wrote embeddings/index.bin + manifest.json (277 vectors, dim 384)`.

- [ ] **Step 2: Verify --check is now clean**

Run: `python scripts/build_embeddings.py --check`
Expected: `up to date (277 cards embedded)`.

- [ ] **Step 3: Sanity-check artifact size + manifest count**

Run: `python -c "import json,os;m=json.load(open('embeddings/manifest.json'));print(m['count'],m['dim'],os.path.getsize('embeddings/index.bin'))"`
Expected: `277 384 425472` (= 277×384×4 bytes).

- [ ] **Step 4: Commit the generated artifact**

```bash
git add embeddings/index.bin embeddings/manifest.json
git commit -m "feat(ai-retrieval): generate committed 277-vector semantic index"
```

---

## Task 8: `search()` core (stub embedder)

**Files:**
- Create: `scripts/search.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: Write the failing test**

`tests/test_search.py`:
```python
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_embeddings as be  # noqa: E402
import search as srch  # noqa: E402

DIM = be.DIM


def test_search_ranks_by_cosine():
    # 3 unit vectors along axes 0,1,2
    vectors = np.zeros((3, DIM), dtype=np.float32)
    for i in range(3):
        vectors[i, i] = 1.0
    manifest = {"dim": DIM, "vectors": [
        {"id": "a", "path": "data/a", "title": "A"},
        {"id": "b", "path": "data/b", "title": "B"},
        {"id": "c", "path": "data/c", "title": "C"},
    ]}

    def stub_query(q):
        v = np.zeros(DIM, dtype=np.float32)
        v[1] = 1.0  # aligns with vector "b"
        return v

    hits = srch.search("anything", vectors, manifest, embedder=stub_query, k=2)
    assert [h["id"] for h in hits] == ["b", "a"] or [h["id"] for h in hits][0] == "b"
    assert hits[0]["id"] == "b"
    assert hits[0]["rank"] == 1
    assert abs(hits[0]["score"] - 1.0) < 1e-5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_search.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'search'`.

- [ ] **Step 3: Write minimal implementation**

`scripts/search.py`:
```python
#!/usr/bin/env python3
"""search.py — semantic search over the 509dds-data card index.

Usage:
  python scripts/search.py "examiner burnout evidence"
  python scripts/search.py -k 5 --json "peer state pay scales"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_embeddings as be  # noqa: E402


def search(query, vectors, manifest, embedder=be.embed_query, k=8):
    q = embedder(query)
    scores = vectors @ q  # cosine == dot on normalized vectors
    top = np.argsort(-scores)[:k]
    hits = []
    for rank, idx in enumerate(top, start=1):
        v = manifest["vectors"][int(idx)]
        hits.append({"rank": rank, "score": float(scores[idx]),
                     "id": v["id"], "path": v["path"], "title": v["title"]})
    return hits
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_search.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/search.py tests/test_search.py
git commit -m "feat(ai-retrieval): add search() cosine ranking core"
```

---

## Task 9: `search.py` CLI + real integration test

**Files:**
- Modify: `scripts/search.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_search.py`:
```python
import pytest


@pytest.mark.integration
def test_real_search_finds_payscale_card():
    pytest.importorskip("fastembed")
    repo = Path(__file__).resolve().parents[1]
    vectors, manifest = be.load_artifact(repo / "embeddings")
    hits = srch.search("disability examiner salary pay scale", vectors, manifest, k=10)
    paths = " ".join(h["path"] for h in hits)
    assert "pay-scales" in paths  # a pay-scale dataset surfaces in top-10
```

- [ ] **Step 2: Run test to verify it fails (CLI not wired)**

Run: `python scripts/search.py "test"`
Expected: FAIL — no CLI entrypoint yet (no output / error). The integration test itself should PASS already (uses `search()` + committed artifact); run it to confirm retrieval quality:
Run: `pytest tests/test_search.py -m integration -v` → expect PASS.

- [ ] **Step 3: Add the CLI main**

Append to `scripts/search.py`:
```python
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="natural-language search query")
    ap.add_argument("-k", type=int, default=8, help="number of results")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    vectors, manifest = be.load_artifact(be.OUT_DIR)
    hits = search(args.query, vectors, manifest, k=args.k)
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return
    for h in hits:
        print(f"{h['rank']:2d}. {h['score']:.3f}  {h['path']}\n    {h['title']}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Verify the CLI works end-to-end**

Run: `python scripts/search.py -k 5 "examiner pay across peer states"`
Expected: 5 ranked lines, at least one `data/pay-scales/...` path near the top.
Run full unit suite: `pytest tests/ -v -m "not integration"` → all pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/search.py tests/test_search.py
git commit -m "feat(ai-retrieval): add search CLI entrypoint"
```

---

## Task 10: Docs — `embeddings/README.md` + `llms.txt` pointer

**Files:**
- Create: `embeddings/README.md`
- Modify: `scripts/build_catalog.py` (LLMS_HEADER) + regenerate `llms.txt`

- [ ] **Step 1: Write `embeddings/README.md`**

`embeddings/README.md`:
````markdown
# Semantic retrieval index

`index.bin` + `manifest.json` are a committed vector index over every data card,
generated by `scripts/build_embeddings.py`. They let an AI retrieve datasets by
meaning with **no API key** (repo-as-database).

## Protocol
- Model: `BAAI/bge-small-en-v1.5` (Python/`fastembed`) ≡ `Xenova/bge-small-en-v1.5` (JS/`@xenova/transformers`).
- `index.bin`: `count × 384` Float32 little-endian, L2-normalized, in `manifest.vectors` order.
- Query: prepend `manifest.query_instruction`, embed, then cosine = dot product. Top-k rows → `manifest.vectors[i].path`.

## Python
```bash
python scripts/search.py "examiner burnout evidence"
```

## JavaScript (browser or Vercel edge) — reference
```js
import { pipeline } from "@xenova/transformers";
const manifest = await (await fetch("/embeddings/manifest.json")).json();
const buf = await (await fetch("/embeddings/index.bin")).arrayBuffer();
const vectors = new Float32Array(buf); // manifest.count * manifest.dim
const extractor = await pipeline("feature-extraction", manifest.model_js);
const out = await extractor(manifest.query_instruction + query,
                            { pooling: "mean", normalize: true });
const q = out.data; // Float32Array(dim)
const { dim, vectors: meta } = manifest;
const scored = meta.map((m, i) => {
  let dot = 0;
  for (let d = 0; d < dim; d++) dot += vectors[i * dim + d] * q[d];
  return { ...m, score: dot };
});
scored.sort((a, b) => b.score - a.score);
const topK = scored.slice(0, 8); // -> [{ id, path, title, score }]
```
> Note: the in-browser model is ~30 MB (cached after first load). To avoid
> shipping it to every visitor, run the query embedding in a Vercel edge function.
````

- [ ] **Step 2: Add the pointer to `LLMS_HEADER`**

In `scripts/build_catalog.py`, modify `LLMS_HEADER` (the closing lines) to append:
```python
LLMS_HEADER = """# 509dds-data

> Open data, source documents, and analysis for SEIU Local 509's Disability
> Determination Services (DDS) chapter in Massachusetts. DDS = Disability
> Determination Services (adjudicates SSI/SSDI claims), NOT the Department of
> Developmental Services. Audience: union stewards, bargaining-team negotiators,
> 509dds.com developers, and researchers.

Every dataset has a `<file>.meta.json` data card (schema: `schemas/dataset.meta.schema.json`).
The full machine index is `catalog.json`. Confidence tiers: Authoritative,
Computed, Browser-fetch pending, PRR-pending, Structurally unavailable.
This file and catalog.json are generated by `scripts/build_catalog.py`.

Semantic search: a committed vector index (`embeddings/index.bin` + `manifest.json`,
model BAAI/bge-small-en-v1.5) enables meaning-based retrieval with no API key —
see `embeddings/README.md`. Query it with `python scripts/search.py "<query>"`.
"""
```

- [ ] **Step 3: Regenerate llms.txt and confirm catalog still clean**

Run: `python scripts/build_catalog.py`
Expected: `wrote catalog.json + llms.txt (277 datasets)`.
Run: `python scripts/build_catalog.py --check`
Expected: `up to date (277 datasets)`.

- [ ] **Step 4: Commit**

```bash
git add embeddings/README.md scripts/build_catalog.py llms.txt catalog.json
git commit -m "docs(ai-retrieval): document semantic retrieval protocol + JS reference"
```

---

## Task 11: CI gate — `ai-index-check.yml`

**Files:**
- Create: `.github/workflows/ai-index-check.yml`

- [ ] **Step 1: Write the workflow**

`.github/workflows/ai-index-check.yml`:
```yaml
name: AI index check
on:
  pull_request:
  push:
    branches: [ai-retrieval-index, ai-normalization, main]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r scripts/requirements.txt
      - run: python scripts/validate_catalog.py --strict
      - run: python scripts/build_catalog.py --check
      - run: python scripts/build_embeddings.py --check
```

- [ ] **Step 2: Verify the same commands pass locally**

Run: `python scripts/validate_catalog.py --strict && python scripts/build_catalog.py --check && python scripts/build_embeddings.py --check`
Expected: all three succeed (validation OK; both indexes up to date).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ai-index-check.yml
git commit -m "ci(ai-retrieval): self-contained validate + index drift gate"
```

---

## Task 12: Final verification

- [ ] **Step 1: Full unit suite green**

Run: `pytest tests/ -v -m "not integration"`
Expected: all pass (test_cards 3, test_build_embeddings 4, test_search 1).

- [ ] **Step 2: Integration suite green**

Run: `pytest tests/ -v -m integration`
Expected: 2 passed (real-model determinism; real search finds a pay-scale card).

- [ ] **Step 3: All gates clean**

Run: `python scripts/validate_catalog.py --strict && python scripts/build_catalog.py --check && python scripts/build_embeddings.py --check`
Expected: all clean.

- [ ] **Step 4: Smoke the CLI**

Run: `python scripts/search.py -k 8 "evidence of examiner burnout and turnover"`
Expected: 8 ranked, plausibly-relevant card paths.

- [ ] **Step 5: Push the branch**

```bash
git push -u origin ai-retrieval-index
```

---

## Self-Review (author checklist — completed)

**Spec coverage (§4 Phase 1):** embedding doc (Task 1), card sweep (Task 2), `build_embeddings.py` + artifact (Tasks 3–5,7), determinism/`--check` (Tasks 5–6), `search.py` CLI (Tasks 8–9), `llms.txt` section + JS reference (Task 10), CI gate (Task 11), tests throughout. Phases 2–4 are explicitly deferred to their own plans.

**Placeholder scan:** none — every code/test step shows complete code; no TBD/"handle errors"/"similar to".

**Type consistency:** `embed_texts`/`embed_query`/`build`/`pack`/`unpack`/`write_artifact`/`load_artifact`/`check`/`search` signatures match between definitions and call sites; manifest keys (`count`,`dim`,`model`,`model_js`,`query_instruction`,`vectors[{id,path,title,tags}]`) are consistent across build, search, and the JS reference.
