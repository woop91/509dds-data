# data/contract

Executed collective bargaining agreement text for SEIU Local 509 Units 8 & 10
(Commonwealth of Massachusetts), covering DDS (Disability Determination Services)
and related state-agency bargaining units.

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
| `seiu-509-cba-2024-2026.md` | MD | ✅ | Full CBA text, Jan 1 2024 – Dec 31 2026; articles + appendices + Supplemental Agreements (incl. DDS Supp. O) + MOUs; ~384,600 chars readable |
| `dds-cba-2024-2026.source.pdf` | PDF | n/a | Raw source PDF (5.6 MB); excluded from normalization — the .md was converted from this file |

✅ sidecar present · n/a excluded raw source
