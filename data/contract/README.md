# data/contract

Executed collective bargaining agreement text for SEIU Local 509 Units 8 & 10
(Commonwealth of Massachusetts). This is the **statewide combined** Units 8 & 10
agreement; it governs the **Vocational Disability Examiner (VDE)** job class at
DDS-Det (the in-scope reason this file is here) alongside other Unit 8/10 titles at
unrelated agencies.

> **DDS = Disability Determination Services** (the SSA-funded state division that
> adjudicates SSI/SSDI claims at MassAbility), **not** the MA Department of
> Developmental Services.

## Machine-consumption conventions

Every dataset file in this folder is paired with a `<file>.meta.json` data card
conforming to [`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json).
The repo-wide index is [`../../catalog.json`](../../catalog.json) /
[`../../llms.txt`](../../llms.txt).

**AI consumers:** `seiu-509-cba-2024-2026.md` contains readable contract text up to
~character 384,600, then a trailing inline PNG/base64 binary artifact from the PDF
conversion. Truncate at that boundary; do not ingest the binary tail. See the
sidecar `notes` for detail.

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `seiu-509-cba-2024-2026.md` | MD | ✅ | Full CBA text, Jan 1 2024 – Dec 31 2026; articles + appendices + Supplemental Agreements + MOUs; ~384,600 chars readable. **VDE provisions** are the examiner-caseload supplemental agreement + Appendix C examiner titles. **Note:** "Supplemental Agreement O" (~lines 2969–2989) covers **DDS-Dev** (Dept. of Developmental Services) Human Service Coordinators — a *different* agency; do not treat those passages as DDS-Det/VDE evidence. |
| `dds-cba-2024-2026.source.pdf` | PDF | n/a | Raw source PDF (5.6 MB); excluded from normalization — the .md was converted from this file |

✅ sidecar present · n/a excluded raw source
