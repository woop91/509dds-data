# Michigan DDS Salary Research

**Last Updated:** 2026-06-02 (AUTHORITATIVE — MI Civil Service job spec + MDCS Compensation Plan Section A)

## Administering Agency
- **Michigan Department of Health and Human Services (MDHHS), Disability Determination Services (DDS)** — confirmed via the MI Civil Service "Disability Examiner 9-P11 - DDS - Lansing" job posting.

## Examiner / Manager Classification (VERIFIED — MI Civil Service job spec)
MI's examiner class is **Disability Examiner** (levels 9 / 10 / P11 / 12) on pay schedule **W22**; the management class is **Disability Exam Manager** (levels 13 / 14 / 15). Verified from the official MI Civil Service Commission job specification:

| Class / Level | Core code | Pay schedule | Bargaining unit |
|---|---|---|---|
| Disability Examiner 9 (entry) | DISBEXME | W22-009 | SEIU 517M HSS |
| Disability Examiner 10 (intermediate) | DISBEXME | W22-009 | SEIU 517M HSS |
| Disability Examiner P11 (experienced) | DISBEXME | W22-009 | SEIU 517M HSS |
| Disability Examiner 12 (lead/senior) | DISBEXMA | W22-043 | SEIU 517M HSS |
| Disability Exam Manager-2 (13) | DISEMGR2 | Y51 / NERE-142 | NERE (exempt) |
| Disability Exam Manager-3 (14) | DISEMGR3 | Y51 / NERE-146 | NERE (exempt) |
| Disability Exam Manager-4 (15) | DISEMGR4 | Y98 / NERE-155 | NERE (exempt) |

## Scheduled Rates (VERIFIED — MDCS Compensation Plan Section A, effective 10/1/2025)
MI publishes hourly base min/max per level. Annual = hourly × 2080 (40 hr/week × 52 wk):

| Class / Level | Hourly min | Hourly max | Annual min | Annual max |
|---|---|---|---|---|
| Disability Examiner 9 | $25.89 | $32.19 | $53,851 | $66,955 |
| Disability Examiner 10 | $25.17 | $34.12 | $52,354 | $70,970 |
| Disability Examiner P11 | $28.03 | $38.36 | $58,302 | $79,789 |
| Disability Examiner 12 | $29.38 | $42.60 | $61,110 | $88,608 |
| Disability Exam Manager 13 | $31.72 | $48.07 | $65,978 | $99,986 |
| Disability Exam Manager 14 | $34.94 | $53.11 | $72,675 | $110,469 |
| Disability Exam Manager 15 | $39.27 | $58.49 | $81,682 | $121,659 |

Both the class/level AND the hourly rates are from official MI sources → Authoritative. The class-level full ranges (Disability Examiner $25.89–$42.60/hr; Disability Exam Manager $31.72–$58.49/hr) match the MCSC online job-spec pay-range page, cross-confirming the per-level extraction.

## Bargaining Unit
- **Disability Examiner (W22, levels 9-12):** SEIU Local 517M, Human Services Support (HSS) bargaining unit.
- **Disability Exam Manager (levels 13-15):** NERE (non-exclusively represented, exempt) — not in the HSS unit.
- The specific SEIU 517M HSS CBA wage-step terms were not separately verified (cba_terms_verified false); the official MDCS Compensation Plan Section A is authoritative for the published base min/max.

## Methodology note
The MI MDCS Compensation Plan Section A PDF was downloaded with a browser User-Agent (the bare curl is fine here; the hr.nv.gov-style HTML redirect did not occur) and parsed locally with pypdf. The hourly figures are the base minimum and maximum for each level row on pay schedule W22 (examiners) / Y51-Y98 (managers). Annual figures are derived (hourly × 2080) and flagged as derived. Evidence: `.firecrawl/MI-secA-100125.pdf`, `.firecrawl/MI-jobspec-main.md`, `.firecrawl/MI-disexam-spec.md`, script `_mi_secA.py`.

## Sources (official, retrieved 2026-06-02)
- MDCS Compensation Plan Section A (eff 10/1/2025): https://www.michigan.gov/mdcs/-/media/Project/Websites/mdcs/COMP/2025/SecAReport-100125.pdf
- MCSC online job-spec pay ranges: https://mcsc.state.mi.us/MCSCJobSpecifications/JobSpecMain.aspx (Disability Examiner 9-12 $25.89-$42.60; Disability Examiner Manager 13-15 $31.72-$58.49)
- Disability Examiner job specification: https://www.michigan.gov/mdcs/-/media/Project/Websites/mdcs/JOBSPECS/D/DisabilityExaminer.pdf
- Disability Examiner Manager job specification: https://www.michigan.gov/mdcs/-/media/Project/Websites/mdcs/JOBSPECS/D/DisabilityExaminerManager.pdf
