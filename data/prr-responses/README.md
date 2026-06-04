# data/prr-responses

Official Massachusetts Public Records Request (PRR) productions responsive to requests filed by or on behalf of SEIU Local 509's DDS chapter.

**Machine consumption:** Each dataset is paired with a `.meta.json` sidecar conforming to [`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json). The full folder inventory is indexed in [`../../catalog.json`](../../catalog.json) and discoverable via [`../../llms.txt`](../../llms.txt).

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `2025-06-06-vizcaino-responsive-materials.pdf` | pdf | ✅ | Official PRR production; MassAbility/MRC custodian; binary PDF, not text-extracted; ~220 KB |
| `2026-05-21-ehs-ra-requests-data.source.xlsx` | xlsx | n/a | Source workbook for MassAbility RA request outcome counts; raw PRR production; normalized by the CSV below |
| `2026-05-21-massability-ra-requests-monthly.csv` | csv | ✅ | Normalized monthly MassAbility reasonable-accommodation request counts by outcome, Jan 2023-May 2026; 41 monthly rows; grand total 371 |
