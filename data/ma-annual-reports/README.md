# data/ma-annual-reports

Annual reports published by MassAbility (formerly the Massachusetts Rehabilitation
Commission, MRC) and its Statewide Rehabilitation Council (SRC), converted to
Markdown for machine consumption.

> **DDS = Disability Determination Services** (adjudicates SSI/SSDI claims), one of
> the agency's divisions — **not** the MA Department of Developmental Services.

## Machine-consumption conventions

Each data file is paired with a `<file>.meta.json` data card conforming to
[`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json).
The repo-wide index is [`../../catalog.json`](../../catalog.json) /
[`../../llms.txt`](../../llms.txt).

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `massability-fy24.md` | MD | ✅ | MassAbility agency annual report, FY2024 (first under the MassAbility name) |
| `massability-fy25.md` | MD | ✅ | MassAbility agency annual report, FY2025 |
| `mrc-fy23.md` | MD | ✅ | MRC annual report, FY2023 (last under the MRC name, pre-rebrand) |
| `src-fy22.md` | MD | ✅ | Statewide Rehabilitation Council (SRC) advisory report, FY2022 |
| `src-fy23.md` | MD | ✅ | Statewide Rehabilitation Council (SRC) advisory report, FY2023 |
| `src-fy24.md` | MD | ⚠️ | **Mislabeled duplicate** — byte-identical to `massability-fy24.md` (blob `1184fab3`); genuine SRC FY24 report not present |
| `_index.md` | MD | n/a | Underscore-prefixed internal index; excluded from normalization |

✅ sidecar present · ⚠️ present but flags a data issue · n/a excluded
