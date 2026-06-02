# data/cthru-staffing

DDS staffing counts derived from [CTHRU](https://cthru.data.mass.gov/), the Massachusetts Comptroller's public payroll transparency system. DDS = Disability *Determination* Services (SSI/SSDI adjudication within MassAbility/MRC), not Developmental Services.

**Machine consumption:** Each dataset is paired with a `.meta.json` sidecar conforming to [`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json). The full folder inventory is indexed in [`../../catalog.json`](../../catalog.json) and discoverable via [`../../llms.txt`](../../llms.txt).

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `dds-staff-totals.json` | json | ✅ | DDS division headcount by year (VDE, Medical Consultants, division total, MRC total); CY 2010–2023 |
| `vde-headcount-by-grade-and-year.json` | json | ✅ | VDE headcount by pay grade and year; alpha→roman reclassification in 2016; CY 2010–2023 |

## Subdirectories

| Directory | Status | Notes |
|---|---|---|
| `leadership-research/` | Queued for normalization | Individual-level CTHRU lookups for DDS leadership; sidecars not yet authored |
