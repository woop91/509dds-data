# New York DDS Salary Research Notes

**Last Updated:** 2026-06-02 (AUTHORITATIVE for the PEF examiner classes; supervisor row flagged)

## Administering Agency
**New York Office of Temporary and Disability Assistance (OTDA), Division of Disability Determinations (DDD)** — processes SSDI/SSI disability determinations for SSA.

## Examiner Classification (VERIFIED — NY Title & Salary Listing)
The disability examiner series in NY's classified civil service is the **Disability Analyst** series. Salary-grade (SG) assignments verified from the official **NY Title and Salary Listing** (Open Data NY dataset `t3vp-5tka`, the complete Title and Salary Plan):

| Title | Title Code | Salary Grade | Negotiating Unit |
|---|---|---|---|
| Disability Analyst 2 | 6884200 | SG 20 | PEF / PS&T |
| Disability Analyst 3 | 6884300 | SG 23 | PEF / PS&T |
| Disability Analyst 4 | 6884400 | SG 25 | PEF / PS&T |
| Disability Analyst 5 (supervisor) | 6884500 | SG 62 | Management/Confidential (M/C) |

**Correction to prior notes:** The earlier research guessed a "Disability Analyst (Trainee)" and "Disability Analyst 1". The current NY Title and Salary Plan has **no** such titles — the examiner series begins at Disability Analyst 2. Spanish-language parallel titles (6884210, 6884310) exist at the same grades.

Related higher-level titles (not in the examiner/first-line-supervisor mapping for this card): Chief of Disability Determinations Pgm Plcy & Plng (SG 27, PEF), Disability Determinations Program Manager (SG 64, M/C), Dir Disability Determinations Opertns (SG 65, M/C).

## Pay Grade Structure & Scheduled Rates (VERIFIED)
NY uses a Salary Grade (SG) system. The PEF PS&T schedule publishes a **Hiring Rate** (step 1 / minimum) and **Job Rate** (top step / maximum) per grade, with ~7 annual steps in between.

**PS&T salary schedule effective March 27, 2025 (Admin) / April 3, 2025 (Inst)** — official OER PDF:

| Grade | Hiring Rate (min) | Job Rate (max) |
|---|---|---|
| SG 20 (Disability Analyst 2) | $74,193 | $94,121 |
| SG 23 (Disability Analyst 3) | $86,681 | $109,650 |
| SG 25 (Disability Analyst 4) | $96,336 | $121,413 |

For these three PEF titles, BOTH the grade assignment AND the dollar figures are from official sources → Authoritative.

## Supervisor (Disability Analyst 5, SG 62 — M/C)
Disability Analyst 5 is the first-line supervisory class and sits in the **Management/Confidential** group at **SG 62** (verified from the Title & Salary Listing). SG 62 is NOT on the PEF/PS&T schedule; it is on the **M/C salary schedule**. The published M/C schedule (OSC payroll bulletin 2349, eff April 2025) lists rows `M/C 3`..`M/C 23` then `M 1`..`M 8`, and does not print a row literally labeled "62". Per NY's documented M/C convention SG 62 corresponds to the **M-1** band (OSC PayServ manual: "Management/Confidential grades 661 (M1) and higher"). The M-1 Hiring/Job rates are **$93,659 / $118,388** (eff April 2025) — recorded as the **candidate** figures for the supervisor, but flagged because an explicit published SG-62→M-1 crosswalk was not located in this session. So the supervisor row is recorded with `supervisor_schedule_row_verified: false`.

## Bargaining Unit
- **Examiners (DA 2/3/4):** PEF Bargaining Unit 5 — Professional, Scientific & Technical (PS&T). CBA April 2, 2023 – April 1, 2026. The 2025 schedule reflects the 3% increase (103% factor) in the CBA.
- **Supervisor (DA 5):** Management/Confidential (M/C), unrepresented.

## Sources (official, retrieved 2026-06-02)
- NY Title and Salary Listing (Open Data NY, dataset t3vp-5tka): https://data.ny.gov/es/es/Government-Finance/Title-and-Salary-Listing/t3vp-5tka — queried via SODA API for `title_name LIKE '%DISABILITY ANALYST%'`. Evidence: `.firecrawl/NY-titleplan-disabilityanalyst.json`, `.firecrawl/NY-titleplan-disability-all.json`.
- OER PEF PS&T Salary Schedule 2023-2026 (PDF): https://oer.ny.gov/system/files/documents/2024/01/pef-salary-schedules-2023-2026-final_0.pdf — evidence `.firecrawl/NY-pef-schedule.md` (full grade table, all three effective dates 2023/2024/2025).
- OSC M/C Salary Schedule eff April 2025 (PDF bulletin 2349): https://www.osc.ny.gov/files/state-agencies/payroll-bulletins/pdf/2349-april-2025-mc-salary-schedule-attachment.pdf — evidence `.firecrawl/NY-mc-schedule.md`.
- OMCE M/C salary schedule page: https://nysomce.org/page/SalarySchedule — evidence `.firecrawl/NY-omce-mc.md` (M-1 row corroborates $93,659/$118,388).

## Remaining minor gap
- Explicit published SG-62 → M-1 crosswalk for the Disability Analyst 5 supervisor (the M-level figures are the documented candidate, but the exact crosswalk row was not printed on the schedules located). All examiner-class data is fully authoritative.
