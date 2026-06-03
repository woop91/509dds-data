# Connecticut (CT) DDS Salary Research

**Last Updated:** 2026-06-02 (AUTHORITATIVE — CT DAS JobAps class specs + official P-3B pay plans)

## Administering Agency
**Connecticut Department of Aging and Disability Services (ADS), Bureau of Disability Determination Services** — performs SSA disability determinations under cooperative agreement. (Correction: earlier notes said DSS; the current class specs cite the Department of Aging and Disability Services, Bureau of Disability Determination Services.)

## Examiner / Supervisor Classification (VERIFIED — CT DAS JobAps class specs)
CT's disability adjudication series and their Salary Groups, verified from the official CT DAS JobAps class specifications:

| Class Title | Class # | Salary Group | Pay Plan |
|---|---|---|---|
| Disability Claims Examiner Assistant (35 Hour) | 7102EB | EB 21 | P-3B EB 35-hour |
| Disability Claims Examiner (40 Hour) | 7103EH | EH 23 | P-3B EH 40-hour |
| Disability Claims Specialist (40 Hour) | 7104EQ | EQ 25 | P-3B EQ 40-hour |
| Disability Claims Supervisor (40 Hour) | 7105EH | EH 28 | P-3B EH 40-hour |

The class number encodes the pay-plan code (EB/EH/EQ); the spec's Salary Group number indexes into that plan's grid.

## Scheduled Rates (VERIFIED — official P-3B pay plans, effective 2025-07-01)
Step 1 = minimum, top step = maximum. Annual figures:

| Class | Salary Group | Min (Step 1) | Max (top step) | Steps |
|---|---|---|---|---|
| Disability Claims Examiner Assistant (7102EB) | EB 21 | $65,190 | $84,765 | 10 |
| Disability Claims Examiner (7103EH) | EH 23 | $80,168 | $106,733 | 10 |
| Disability Claims Specialist (7104EQ) | EQ 25 | $88,127 | $118,740 | 11 |
| Disability Claims Supervisor (7105EH) | EH 28 | $101,964 | $135,709 | 11 |

Both the grade assignment AND the dollar grids are from official CT DAS sources → Authoritative.

## Methodology note (anti-fabrication)
The Firecrawl markdown/PDF-table conversion of the P-3B pay-plan PDFs DROPPED several middle groups (EH/EQ jumped 23 → 31 in the markdown), and the Firecrawl page-`--query` mode returned a HALLUCINATED "EQ 25" that simply duplicated the EQ-22 row. Both were caught and rejected. The authoritative dollar figures were extracted directly from the downloaded PDF text using local `pypdf` (5-page PDFs, all groups present). Evidence: `.firecrawl/CT-plan-EB.pdf`, `CT-plan-EH.pdf`, `CT-plan-EQ.pdf` and the extraction scripts `_ct_extract.py` / `_ct_grids.py`.

## Bargaining Unit
- The EB/EH/EQ pay plans are filed under **P-3B** in the CT DAS compensation-plan directory.
- The P-3B unit contract is hosted/administered by **CSEA SEIU Local 2001** (apparent representing union; identity not deeply re-verified). The earlier "AFSCME Local 714 / SEBAC P-2" attribution was incorrect.
- 9-11 step annual progression per group.

## Sources (official, retrieved 2026-06-02)
- Class specs (Salary Group mapping): CT DAS JobAps —
  - 7102EB Examiner Assistant: https://www.jobapscloud.com/CT/specs/classspecdisplay.asp?ClassNumber=7102EB (evidence `.firecrawl/CT-7102EB-spec.md`)
  - 7103EH Examiner: https://www.jobapscloud.com/CT/specs/classspecdisplay.asp?ClassNumber=7103EH (evidence `.firecrawl/CT-7103EH-spec.md`)
  - 7104EQ Specialist: https://www.jobapscloud.com/CT/specs/classspecdisplay.asp?ClassNumber=7104EQ (evidence `.firecrawl/CT-dcs-spec.md`)
  - 7105EH Supervisor: https://www.jobapscloud.com/CT/specs/classspecdisplay.asp?ClassNumber=7105EH (evidence `.firecrawl/CT-7105EH-spec.md`)
- Pay plans (dollar grids), CT DAS Compensation Plans, eff 2025-07-01:
  - EB 35-hour: https://portal.ct.gov/das/-/media/das/statewide-hr/comp-plans-pdfs/2025-comp-plans-pdf/2025-pay-plans-website/p-3b/eb-2025-07-01-updated.pdf
  - EH 40-hour: https://portal.ct.gov/das/-/media/das/statewide-hr/comp-plans-pdfs/2025-comp-plans-pdf/2025-pay-plans-website/p-3b/eh-2025-07-01.pdf
  - EQ 40-hour: https://portal.ct.gov/das/-/media/das/statewide-hr/comp-plans-pdfs/2025-comp-plans-pdf/2025-pay-plans-website/p-3b/eq-2025-07-01.pdf
- Compensation-plan index: https://portal.ct.gov/das/services-for-state-employees/statewide-human-resources/compensation-plans (evidence `.firecrawl/CT-comp-plans.json`)

## Minor remaining gap
- The exact union/CBA identity for P-3B (CSEA SEIU Local 2001 appears to host the P-3B contract) was not deeply re-verified; it does not affect the pay figures, which are authoritative.
