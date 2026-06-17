# data/ma-annual-reports

Annual reports published by MassAbility (formerly the Massachusetts Rehabilitation
Commission, MRC), converted to Markdown for machine consumption.

These are agency-wide reports kept here **only because each carries a Disability
Determination Services (DDS-Det) division section** — budget, claim volumes,
accuracy/allowance rates, examiner-vacancy narrative — that the chapter needs.
MassAbility-DB links to them rather than duplicating (see
[`docs/related-repos.md` in MassAbility-DB](https://github.com/Woop91/MassAbility-DB/blob/main/docs/related-repos.md)).

> **DDS = Disability Determination Services** (adjudicates SSI/SSDI claims), one of
> the agency's divisions — **not** the MA Department of Developmental Services, and
> **not** Vocational Rehabilitation (VR). See [`../../SCOPE.md`](../../SCOPE.md).

## Machine-consumption conventions

Each data file is paired with a `<file>.meta.json` data card conforming to
[`../../schemas/dataset.meta.schema.json`](../../schemas/dataset.meta.schema.json).
The repo-wide index is [`../../catalog.json`](../../catalog.json) /
[`../../llms.txt`](../../llms.txt).

## Inventory

| File | Type | Sidecar | Notes |
|---|---|---|---|
| `massability-fy24.md` | MD | ✅ | MassAbility agency annual report, FY2024 (first under the MassAbility name); carries DDS-Det section |
| `massability-fy25.md` | MD | ✅ | MassAbility agency annual report, FY2025; carries DDS-Det section |
| `mrc-fy23.md` | MD | ✅ | MRC annual report, FY2023 (last under the MRC name, pre-rebrand); carries DDS-Det section |
| `_index.md` | MD | n/a | Underscore-prefixed internal index (crawled mass.gov listing); excluded from normalization |

✅ sidecar present · n/a excluded

## Relocated out (2026-06-17)

The following were **removed from this chapter repo** because they are not DDS-Det /
Vocational Disability Examiner material:

- `src-fy22.md`, `src-fy23.md` — **State Rehabilitation Council (SRC)** reports. The
  SRC advises only MassAbility's **Vocational Rehabilitation (VR)** division (a
  different program); these carry zero DDS-Det content. **Relocated** to the umbrella
  repo at [`MassAbility-DB/data/annual-reports/`](https://github.com/Woop91/MassAbility-DB/tree/main/data/annual-reports).
- `src-fy24.md` — was a **mislabeled byte-identical duplicate** of `massability-fy24.md`
  (the genuine SRC FY24 report was never held here). Deleted as a duplicate; the
  in-scope content survives in `massability-fy24.md`.

See [`../../SCOPE.md`](../../SCOPE.md) for the keep-it-VDE-only rule that governs this.
