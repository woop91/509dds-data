# Design: AI-retrieval index for 509dds-data (`ai-retrieval-index`)

- **Branch:** `ai-retrieval-index`, forked from `ai-normalization` (base `f47963d` = `origin/main` + 13 normalization commits, unmerged).
- **Date:** 2026-06-02
- **Status:** Approved design — pending implementation plan.

## 1. Purpose

The `ai-normalization` branch gave every dataset a machine-readable `.meta.json`
data card (277 cards) plus two generated indexes (`catalog.json`, `llms.txt`).
Today an AI agent finds a dataset by *reading the index* — a lexical, O(N) scan
that requires loading the whole catalog and often opening individual cards.

This branch adds the next layer of retrieval capability, in four impact-ordered
phases:

1. **Semantic/embedding index** — retrieve cards by *meaning* (top-k vector
   search), not lexical scan. The biggest lever.
2. **Controlled tag vocabulary + denser cross-links** — faceted retrieval and
   traversable `related` edges.
3. **Column value-stats on tabular datasets** — min/max/distinct/sample so an AI
   can answer "does this cover 2019?" / "what states are in here?" from the card.
4. **Fill the 16 `Browser-fetch pending` datasets** — data acquisition for the 8
   peer-state DDS-examiner pay scales.

### Strategic framing: repo-as-database

The embedding index is deliberately built to let **509dds.com use this repo as a
self-contained database for its public reference-data layer**, as an alternative
to hosting that layer in Supabase. "Repo-as-database" means: clone (or fetch) the
repo and semantic search works with **no external service and no API key** — the
repo carries its own vectors, and a query is embedded locally (browser or Vercel
edge) with the identical model. This is the layer of *public reference data* (SSA
stats, pay scales, contract text, oversight reports), not the app's transactional
data (grievances, cases, users), which stays in Supabase regardless.

## 2. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Scope | All four phases on one branch | User directive; impact-ordered commits |
| Serving target | Optimize for repo-as-database (self-contained) | User choice |
| Embedding posture | Offline, **dual-runtime** | No API key; query embeddable in browser/edge; repo stays portable |
| Embedding model | `BAAI/bge-small-en-v1.5` (384-dim, ONNX) | Runs in both `fastembed` (Python build) and `@xenova/transformers` (JS query); strong small-model retrieval quality |
| Vector store | Committed dense vectors + brute-force cosine | 277×384 is ~0.4 MB; instant; runs anywhere; no native ANN deps |
| Query interface | Python CLI + documented protocol (+ JS reference snippet) | User choice; mirrors `build_catalog.py` |

## 3. Architecture

### 3.1 Guiding pattern (existing, to mirror)

`scripts/build_catalog.py` is the template: sweep **all** `*.meta.json` cards →
regenerate index artifacts → offer `--check` (exit 1 if a rebuild would differ).
`scripts/validate_catalog.py --strict` validates cards + catalog consistency.
Every new phase follows the same discipline: **generated artifacts are never
hand-edited; they are regenerated from the cards, and a `--check` mode prevents
drift.**

> Note: the husky pre-commit + Semgrep/Gitleaks CI harness lives on the *sibling*
> `security-tooling-baseline` branch, **not** on `ai-normalization`. Therefore the
> new gates on this branch are made **self-contained**: each script ships its own
> `--check`, and a standalone GitHub Actions workflow runs the checks. If the two
> branches are later merged, the workflow composes with the existing harness.

### 3.2 Dependency order

Phase 1 embeds card text *as it exists today*. Phases 2–3 enrich card text
(better tags, value-stats). So the **build is re-run after 2–3** and the index is
*regenerated*, not rewritten. Phase 4 adds new cards, which the build also picks
up. The embedding build is the single chokepoint that makes later phases cheap.

## 4. Phase 1 — Semantic/embedding index (core)

### 4.1 Components (all new, additive)

1. **`scripts/build_embeddings.py`**
   - Sweeps all cards under `data/` + `prr-templates/` (reuse `build_catalog.py`'s
     `load_cards`/`collection_of` helpers; refactor shared bits into a small
     `scripts/_cards.py` module if cleaner).
   - Composes a deterministic **embedding document** per card:
     `title` + `description` + `tags` (joined) + `columns[].name` (for tabular) +
     `geographic_coverage` + `temporal_coverage`. Documented + stable so the
     vector is reproducible.
   - Embeds with `fastembed` (`BAAI/bge-small-en-v1.5`, ONNX, CPU, no PyTorch).
   - Writes the artifact (4.2). `--check` mode: rebuild in-memory, compare to the
     committed artifact within a float tolerance (e.g. `atol=1e-5`); exit 1 if it
     would change. ONNX CPU inference is deterministic, so this is reliable.

2. **Artifact (`embeddings/`)**
   - `embeddings/index.bin` — packed Float32 little-endian, `N × 384`, rows in the
     same sorted order as the manifest. ~0.4 MB.
   - `embeddings/manifest.json` — `{ model, model_revision, dim, normalized:true,
     query_instruction, count, vectors: [{id, path, title, tags, byte_offset}] }`.
     Human-readable + diffable; carries everything needed to map a row back to a
     card and to embed a query identically.
   - Vectors are L2-normalized at build time so cosine == dot product.

3. **`scripts/search.py "<query>"`**
   - Embeds the query (with the bge query instruction) via `fastembed`, cosine vs
     all rows, prints top-k `{rank, score, id, path, title}` (default k=8; `-k`,
     `--json` flags).
   - This is the item-#1 "Interface" deliverable.

4. **Docs**
   - New `## Semantic retrieval` section in `llms.txt`: the protocol (model, dim,
     query instruction, artifact layout, how to map a hit → data file).
   - A **reference JS snippet** (in `docs/` and referenced from `llms.txt`) showing
     509dds.com embedding a query with `@xenova/transformers` (same bge ONNX) and
     doing cosine over `index.bin` — in-browser or at the Vercel edge.

### 4.2 Data flow

```
cards (*.meta.json) ──build_embeddings.py──▶ embeddings/index.bin + manifest.json
                                                      │
query string ──search.py / transformers.js──▶ query vector ──cosine──▶ top-k card paths ──▶ data files
```

### 4.3 Scope boundary

Branch 2 ships **artifacts + Python CLI + a documented JS reference**. It does
**not** modify the 509dds.com application. Website wiring is a separate repo's
work; this branch makes that wiring trivial and serving-target-neutral.

## 5. Phase 2 — Controlled tags + denser cross-links (#3)

Current state: 783 distinct tags / 2,417 uses, of which **436 are singletons**;
obvious near-duplicates (`disability-examiners` ×48 vs `disability-examiner` ×11).
**86 of 277 cards have zero `related` edges.**

1. **`schemas/tags.vocabulary.json`** — a curated, faceted controlled vocabulary
   (e.g. `agency:ssa`, `topic:processing-time`, `geo:massachusetts`,
   `tier:peer-state`, `doc-type:research-notes`). Consolidates the 783 free tags.
2. **`scripts/normalize_tags.py`** — maps each existing tag → a vocabulary term,
   rewrites the 277 cards, and **reports unmapped tags for human review** (never
   silently drops). Idempotent (running twice is a no-op). `--check` mode.
3. **Densify `related`** — `scripts/suggest_related.py` proposes edges for the 86
   zero-link cards using same-collection + shared-tag + temporal-neighbor
   heuristics, emitted as **suggestions** (written to a review file) that a human
   confirms before they land in cards. No blind edge-writing.

After this phase, `build_catalog.py` and `build_embeddings.py` are re-run.

## 6. Phase 3 — Column value-stats on tabular cards (#2)

Current state: **47** tabular cards (csv/json/xlsx), all already have `columns[]`,
**0** have value-stats. The schema already permits extra column properties
(`additionalProperties: true`).

1. **`scripts/compute_value_stats.py`** — opens each tabular file, computes per
   column `min` / `max` / `distinct_count` / `sample_values` (+ card-level
   `row_count`, `sample_rows`), and writes them into the existing `columns[]`
   slots. Skips/flags files it cannot parse. `--check` mode.
2. Stats are written back into the cards (cards remain the source of truth), then
   `build_catalog.py` + `build_embeddings.py` re-run.

Bounded work: 47 files, schema slots already exist.

## 7. Phase 4 — Fill the 16 `Browser-fetch pending` datasets (#4)

The 16 pending = **8 peer states × 2 files**: `research-notes.md` +
`scheduled-rates.json` for DDS-examiner pay scales — CA, CT, HI, IL, MI, NV, NY,
PA.

1. Firecrawl-driven acquisition of each state's published salary schedule for the
   DDS disability-examiner classification(s).
2. Fill `scheduled-rates.json` (+ research notes), flip tier
   `Browser-fetch pending → Authoritative` (official schedule) or `Computed`
   (derived/estimated), and add provenance (`source.url`, `retrieved_at`).
3. **Honest triage:** per-state report of what was obtained vs. what stays
   blocked. **No fabricated rates** — a state whose schedule is gated, PDF-only in
   an unparseable form, or published only as aggregates keeps its pending tier
   with a note explaining *why*.

New/updated cards are picked up by the catalog + embedding builds.

## 8. Cross-cutting: testing, gates, error handling

### Testing (TDD per script)
- `build_embeddings.py`: determinism (same input → same vectors within tolerance);
  `--check` detects a deliberately mutated artifact.
- `search.py`: a seed query returns a known-relevant card in top-k.
- `normalize_tags.py`: idempotent; unmapped tags reported, none dropped.
- `compute_value_stats.py`: stats math correct on a small fixture; unparseable
  file is flagged, not fatal.

### Gate
- `.github/workflows/ai-index-check.yml` (self-contained): runs
  `validate_catalog.py --strict`, `build_catalog.py --check`,
  `build_embeddings.py --check`, and `normalize_tags.py --check`.

### Error handling
- All builds fail loud on a card that doesn't parse or violates the schema.
- Acquisition (Phase 4) degrades gracefully: a failed fetch leaves the card
  pending with a recorded reason; it never invents data.

## 9. Dependencies introduced

- Python (build/CLI): `fastembed` (ONNX runtime; no PyTorch). Optional `openpyxl`
  for xlsx stats (Phase 3) if not already available.
- JS (reference only, not installed by this repo): `@xenova/transformers` —
  documented for the website consumer.

## 10. Risks / open questions

- **Model download size in-browser (~30 MB ONNX).** Mitigation documented: cache
  after first load, or embed queries in a Vercel edge function instead of shipping
  the model to every visitor. (Website-side concern; documented, not solved here.)
- **Phase 4 availability varies by state.** Some peer states may remain blocked;
  this is expected and reported honestly.
- **Artifact diffability.** `index.bin` is binary (not line-diffable); the
  manifest carries the human-readable metadata, and `--check` guarantees it always
  matches the cards. Accepted trade-off for browser-fetch efficiency.

## 11. Deliverables summary

- `scripts/build_embeddings.py`, `scripts/search.py` (+ optional `scripts/_cards.py`)
- `embeddings/index.bin`, `embeddings/manifest.json`
- `schemas/tags.vocabulary.json`, `scripts/normalize_tags.py`,
  `scripts/suggest_related.py`
- `scripts/compute_value_stats.py`
- Filled/triaged peer-state pay-scale cards (Phase 4)
- `llms.txt` semantic-retrieval section + JS reference snippet
- `tests/` for each script; `.github/workflows/ai-index-check.yml`
