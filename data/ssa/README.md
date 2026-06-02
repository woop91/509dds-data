# data/ssa

Public Social Security Administration (SSA) datasets backing the DDS staffing,
workload, processing-time, accuracy, and budget analyses.

> **DDS = Disability Determination Services** (the SSA-funded state division that
> adjudicates SSI/SSDI claims), **not** the MA Department of Developmental
> Services. See [`../../docs/dds-det-vs-dds-dev.md`](../../docs/dds-det-vs-dds-dev.md).

## Machine-consumption conventions

Every dataset file in this folder is (being) paired with a `<file>.meta.json`
“data card” that conforms to [`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json):
title, description, per-column schema + units, temporal/geographic coverage,
source + retrieval date, confidence tier, and update cadence. Run
`python scripts/validate_catalog.py` from the repo root to check coverage and
validity. The repo-wide index is [`../../catalog.json`](../../catalog.json) /
[`../../llms.txt`](../../llms.txt).

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `periodic-cdr-backlog-fy14-fy18.csv` | CSV | ✅ | National CDR backlog by program, FY14–FY18 |
| `periodic-cdr-fy13-fy22.csv` | CSV | ✅ | CDRs processed, hierarchical program taxonomy, FY13–FY22 |
| `cdp-time-monthly-fy16-fy26.csv` | CSV | ✅ | Monthly avg processing time, FY16–FY26 |
| `cdp-time-monthly-fy08-fy15.csv` | CSV | ✅ | Monthly avg processing time, FY08–FY15 (historical) |
| `dds-net-accuracy-by-state-2007-2022.csv` | CSV | ✅ | DDS net accuracy by state, FY07–FY22 |
| `peer-states-timeseries-2010-2024.json` | JSON | ✅ | MA + 8 peer states, computed favorable-rate series |
| `dds-net-accuracy-by-state-2007-LATEST.csv` | CSV | ⏳ | `-LATEST` alias of the accuracy series |
| `ssa-sa-fywl-all-states-2001-2024.csv` | CSV | ⏳ | SSA state-agency FY workload (large, ~221 KB) |
| `ssa-sa-fywl-all-states-2001-LATEST.csv` | CSV | ⏳ | `-LATEST` alias of the workload series |
| `oig-audit-staffing-productivity-072309.md` | MD | ⏳ | OIG staffing/productivity audit (report) |
| `FETCH_REPORT.md` | MD | n/a | Provenance log for the 2026-05-05 SSA document fetch |
| `*.source.txt` | TXT | n/a | Source-URL provenance (folded into sidecars during rollout) |
| `allowance-rates/`, `budget/`, `claims/`, `foia/`, `oho/`, `performance/`, `staffing/`, `workload-data-total/` | dir | ⏳ | Sub-collections, queued for normalization |

✅ sidecar present · ⏳ queued for the rollout phase
