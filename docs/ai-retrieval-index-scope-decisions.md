# AI-Retrieval Index — Deliberate Scope Decisions & Anti-Fabrication Record

**Branch:** `ai-retrieval-index` ("branch 2") · **Date:** 2026-06-02 → 2026-06-03

This document records three places where the implementation **deliberately chose
correctness/honesty over a fuller-looking result**. Each was a conscious decision,
not an oversight. If a future maintainer wonders "why isn't X auto-filled?", the
answer is here.

---

## Decision 1 — `related` cross-links ship as a *review report*, not auto-applied edges

**What the spec asked for:** denser `related` cross-links across the 277 cards
(86 of which had zero links).

**What we did instead:** generated `reports/related-suggestions.json` — a curated,
human-review artifact (17 small-cluster sibling pairs suggested; 15 large clusters
*flagged* for topical curation) — and did **not** mutate any card's `related` field.

**Why (the data made the crude approach harmful):**
- The obvious heuristic — "link cards that share a directory" — would have created
  **~1,651 edges, ~1,560 of them inside a single folder**:
  `data/external/nade/state-bylaws/` holds ~60 cards, and pairwise-linking them is a
  near-complete **clique**. Every state bylaw "related" to every other state bylaw
  is *noise*, not useful traversal — it would make `related` actively worse for an
  AI navigating the graph. Co-location is a poor relatedness signal for large
  reference collections.
- Additionally, **all 86 zero-link cards lack a `related` key entirely** (none had
  an empty `[]`). Auto-applying would have required format-preserving *key
  insertion* into the cards' compact JSON — extra risk for a heuristic already
  shown to be low-quality on the big clusters.

**How to act on it later:**
- Curate `reports/related-suggestions.json` by hand — the 17 small-cluster pairs
  (e.g. a peer state's `research-notes` ↔ `scheduled-rates`) are genuinely related
  and safe to apply.
- For the large flagged clusters, link **topically** (shared specific tags /
  `derived_from` chains), not by mere co-location.
- The clean peer-state pairs are good candidates to link in-context whenever those
  cards are next edited.

---

## Decision 2 — value-stats cover the 14 CSV cards; the 33 JSON cards were *skipped, not forced*

**What the spec asked for:** per-column value-stats (min/max, distinct, samples)
on the 47 tabular cards.

**What we did:** computed stats for all **14 CSV** cards (and any flat-record JSON).
The **33 JSON cards were skipped** — and the skip count is reported by
`compute_value_stats.py --check` ("33 non-tabular cards skipped").

**Why (forcing stats would have been fabrication):**
- Many JSON *data files* are **not flat tables**. Examples:
  `dds-statistics-master-table.json` is 17 metrics, each a year-keyed series, with
  sentinel values like `'PRR'` (retrievable only via public-records request) and
  `'TBD'`; others are per-state nested structures. There is no clean row×column
  mapping, so a "min/max" would be meaningless or misleading.
- `stats_from_json()` therefore returns `None` for anything that isn't a list of
  flat record-dicts, and `run()` records it as skipped rather than emitting bogus
  numbers.

**How to extend later:** write **per-shape JSON extractors** (one per distinct
structure — keyed-series, nested-by-state, etc.) if value-stats on those datasets
become worth the bespoke effort. That is real, structure-specific work, not
generic normalization.

---

## Anti-fabrication discipline — Phase 4 (peer-state pay scales)

Phase 4 filled 8 states' DDS-examiner pay scales (CA/CT/HI/IL/MI/NV/NY/PA) from the
open web. This is the phase where invented-but-plausible numbers were the biggest
risk, so the rule was absolute: **every salary figure must trace to a live official
source; anything unverifiable stays `null`/`candidate`.**

**What "verified" meant here:**
- **50 filled numbers were evidence-traced** to saved scrapes (100% hit), and **at
  least one class per state was independently re-fetched live** from an official
  `.gov` / state-civil-service domain (calcareers.ca.gov, portal.ct.gov,
  dhrd.hawaii.gov, cms.illinois.gov, michigan.gov, hr.nv.gov, oer.ny.gov,
  careers.employment.pa.gov).
- Both halves were required: the **dollar schedule** *and* the **class→pay-grade
  mapping** (e.g. PA "Disability Claims Adjudicator" → pay group ST07, confirmed on
  the PayExp page itself; NY title→SG from the Open Data Title & Salary listing).

**Traps that were caught and rejected (not trusted):**
- A Firecrawl PDF→markdown conversion **hallucinated a CT "EQ-25" row** (duplicated
  EQ-22) — rejected; real figures read via local `pypdf`.
- A naive NV diagonal-matrix parser **mis-assigned grade-32's max** — corrected to
  the exact `32-10` cell and cross-checked against an official NEATS announcement.
- Garbled CA/PA salary PDFs were **not** used for figures; structured
  PayExp/ExamBulletin pages were used instead.

**Honest residual gaps (left `null`/`candidate`, NOT invented):**
- **CA**: Disability Evaluation Analyst II and the SSM-I supervisor → `null`
  (CalHR cross-reference is JS-gated).
- **NY**: DA5 supervisor (SG62 → M/C M-1 crosswalk) → `candidate` (crosswalk not
  published).
- **HI**: DCS IV working-supervisor (SR-22) → `candidate` (series pattern, not
  officially confirmed).

**Net result:** all 8 states moved `Browser-fetch pending → Authoritative`; **0
"Browser-fetch pending" cards remain repo-wide**; zero fabricated figures.

---

## The cross-cutting lesson (why diffs stayed clean)

The cards use a **compact JSON style** (inline nested objects/arrays), so a naive
`json.dumps(indent=2)` re-serialization reformats hundreds of cards cosmetically.
Every card-mutating tool therefore **surgically replaces only the target field**
(`tags` / `related` / `columns` span) and leaves all other bytes identical. This is
what kept the tag-normalization diff to clean one-line-per-card changes and made
"only the intended field changed" independently verifiable.
