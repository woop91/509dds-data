# Nevada DDS Examiner Salary Research

**Last Updated:** 2026-06-02 (AUTHORITATIVE — NV class spec + NV Pay Policy 01 Classified schedule)

## Administering Agency
- **Nevada Department of Employment, Training and Rehabilitation (DETR)**, Rehabilitation Division / Bureau of Disability Adjudication.

## Examiner / Supervisor Classification (VERIFIED — official NV class spec 12.457)
The NV Disability Adjudicator series and grades, verified from the official State of Nevada class specification (series doc 12.457):

| Class Title | Class Code | Grade | Level |
|---|---|---|---|
| Disability Adjudicator Trainee | 12.425 | 30 | trainee |
| Disability Adjudicator I | 12.426 | 31 | continuing trainee |
| Disability Adjudicator II | 12.428 | 32 | (advanced trainee/working) |
| Disability Adjudicator III | 12.456 | 33 | journey level |
| Disability Adjudication Supervisor | 12.457 | 35 | supervisory |

## Scheduled Rates (VERIFIED — NV Pay Policy 01 Classified EE/ER, effective July 7, 2025)
min = step 1, max = step 10 (annual):

| Class | Grade | Min (step 1) | Max (step 10) |
|---|---|---|---|
| Disability Adjudicator Trainee (12.425) | 30 | $52,200.00 | $76,608.72 |
| Disability Adjudicator I (12.426) | 31 | $54,434.16 | $80,053.92 |
| Disability Adjudicator II (12.428) | 32 | $56,689.20 | $83,666.16 |
| Disability Adjudicator III (12.456) | 33 | $59,257.44 | $87,570.72 |
| Disability Adjudication Supervisor (12.457) | 35 | $64,414.80 | $95,630.40 |

Both the grade assignment AND the dollar figures are from official NV sources → Authoritative.

## Pay-plan caveat (important)
NV publishes MULTIPLE compensation schedules by retirement-contribution election:
- **Pay Policy 01 — Employee/Employer Contribution (EE/ER)** — the standard/higher base, used here.
- **Pay Policy 02 — Employer Paid Contribution (EPC)** — lower base salaries.
- Several CBU-specific variants (01A/E/F/I, 01C/L/M/N/O, 01G, 01H/K) with slightly different rates.
The base statewide Pay Policy 01 EE/ER schedule was used. The grade-32 min/max here ($56,689.20–$83,666.16) **exactly matches** an official NEATS Disability Adjudicator 3 job announcement, confirming the plan choice and the extraction.

## Methodology note (anti-fabrication)
The NV schedule is a "diagonal" matrix where one row holds many grade-step cells sharing the same Annual. A naive parser ("last number in the row = this grade's annual") mis-assigned values; an early run gave grade-32 max = $86,944 which was WRONG. The correct figures were read by locating the exact 'GG-01' and 'GG-10' tokens and taking that row's Annual, then cross-checked against the official job announcement. Curl initially returned an HTML error page; the PDF was obtained with a browser User-Agent and parsed locally with pypdf. Evidence: `.firecrawl/NV-classified-fy26-v2.pdf`, `.firecrawl/NV-adjudicator-spec.md`, scripts `_nv_exact.py`.

## Bargaining Unit
- **AFSCME Local 4041 (NSEA)** — first formal NV public-sector DDS CBA ratified Aug 2024 (enabled by AB 271, 2019). The exact CBA wage effect vs the statewide schedule was not separately verified (cba_terms_verified false); the official NV classified schedule is authoritative for the posted ranges.

## Sources (official, retrieved 2026-06-02)
- Class spec (grade mapping): https://hr.nv.gov/uploadedFiles/hrnvgov/Content/Resources/ClassSpecs/12/12-457spc(2).pdf
- Compensation schedules (Pay Policy 01, eff 2025-07-07): https://hr.nv.gov/Sections/Compensation/Compensation_Schedules/ → `Classified FY26 - 7.7.2025.pdf`
- Cross-check: official NEATS Disability Adjudicator 3 announcement (grade 32 = $56,689.20–$83,666.16).
