# SCOPE — keep 509dds-data VDE-only

This repo is the **DDS-Det chapter** repo: the bargaining/data backbone for the
**Disability Determination Services (DDS-Det)** division of MassAbility and the
**Vocational Disability Examiners (VDEs)** who staff it as **SEIU Local 509
Units 8 & 10** (Boston + Worcester).

Its sibling, [`MassAbility-DB`](https://github.com/Woop91/MassAbility-DB), is the
**umbrella** repo for the whole MassAbility agency. The relationship is
**one-directional**:

- ✅ MassAbility-DB MAY reference/link **all** of this repo.
- ❌ This repo MUST NOT pull in broad-MassAbility content. Keep it pure.

## The rule

> **An artifact belongs in 509dds-data only if it is specifically about DDS-Det
> operations/budget/stats OR about VDEs as workers.** Everything else defaults to
> MassAbility-DB.

Decision shortcut: **"Would a Unit 8/10 steward or bargaining negotiator cite this
to argue a VDE staffing, pay, accuracy, or working-conditions point?"**
Yes → here. No → MassAbility-DB.

## Two disambiguations you must get right

1. **VDE ≠ VR.** "Vocational **Disability Examiner**" (VDE) adjudicates SSI/SSDI
   claims — IN scope. "Vocational **Rehabilitation**" (VR) is a separate MassAbility
   counseling/job-placement program — OUT of scope. They share the prefix
   "Vocational"; match on the **full term and the function**, never the prefix.
2. **DDS = Disability Determination Services, never DDS-Dev.** The Department of
   Developmental Services (CTHRU code `DMR`, ~5,500 staff) is a different agency and
   is out of scope for this repo's DDS content. A "DDS staff" pull returning ~5,500
   is mis-scoped — DDS-Det is ~200 staff. See [`docs/dds-det-vs-dds-dev.md`](docs/dds-det-vs-dds-dev.md).

## In scope (belongs here)

- DDS-Det claim-adjudication operations & statistics (initial claims, dispositions,
  allowance/favorable rates, accuracy/QA, processing time, CDRs/backlog) — national,
  MA, or peer-state as comparison.
- VDE compensation & classification (Unit 8/10 salary charts, VDE-grade pay,
  per-employee salary + overtime).
- VDE workforce metrics (headcount / vacancy / turnover by grade; the DDS-Det subset
  of MRC CTHRU payroll).
- VDE workload evidence (overtime authorizations, weekly intake caps, anonymized
  case-load memos for the Boston/Worcester DDS offices).
- The SEIU 509 Units 8 & 10 CBA (full text + excerpts).
- The reasonable-accommodation process applicable to these workers (state Executive
  Branch process, MassAbility DDS RA info, MOD guidance, RA-outcome counts).
- Labor-rights filing & reference material curated **for the chapter** (enforcement
  agencies, deadlines, statute index, steward/member guides).
- Economic comparables marshaled for VDE compensation arguments (BLS CPI-U national +
  Boston metro, BEA RPP, claims-examiner / peer-state DDS-examiner wages).
- Peer-state **DDS** comparisons (other states' DDS adjudication stats and examiner
  pay as benchmarks).
- SSA DDS funding/budget context (work-years, Congressional Justification extracts,
  OIG/GAO DDS staffing audits).
- Agency annual reports (MassAbility/MRC) **only to the extent they carry DDS-Det
  budget/headcount/operational stats**.
- PRR responses and PRR/FOIA templates targeting DDS-Det/VDE data gaps.
- The DDS-Det master statistics table + derived metrics, and the
  methodology/disambiguation docs for the above.

## Out of scope (send to MassAbility-DB)

- Vocational Rehabilitation (VR) / Career Services counseling & placement pages,
  eligibility, handbooks.
- Community Living / Statewide Head Injury Program (SHIP) / brain-injury content.
- Independent Living Center & peer-support content.
- Assistive Technology service/program pages.
- Pre-Employment Transition Services (pre-ETS) content.
- Employer-partner / business-services / job-development content.
- MassAbility field-office **service descriptions** and location directories (as
  service catalogs).
- General "what is MassAbility" / org chart / leadership bios not specific to DDS-Det.
- Crawled `mass.gov/orgs/massability/*` and `mass.gov/info-details/*` service-catalog
  pages.
- Press releases about MassAbility/MRC that are not about DDS-Det or VDEs.
- Annual-report sections covering only VR/SHIP/IL/AT outcomes with no DDS-Det
  budget/stats.
- **State Rehabilitation Council (SRC)** reports — the SRC by federal statute advises
  only the VR Division; SRC reports are VR governance, not DDS-Det.
- **Anything about the Department of Developmental Services (DDS-Dev / `DMR`)** — out
  of scope for both repos' DDS content.

## Edge cases (precedent)

- **Agency-wide annual reports (MassAbility/MRC FY23–FY25):** keep the canonical
  markdown copy HERE because it is the source of the DDS-Det budget/headcount/
  operational stats the chapter needs; do **not** split VR/SHIP/IL sections into
  standalone artifacts; MassAbility-DB **links** rather than duplicates.
- **SRC reports (FY22–FY24):** OUT — they advise the VR Division only and carry no
  DDS-Det stats. **Relocated 2026-06-17** to
  [`MassAbility-DB/data/annual-reports/`](https://github.com/Woop91/MassAbility-DB/tree/main/data/annual-reports).
  (The file once named `src-fy24.md` here was a byte-identical duplicate of the
  DDS-bearing `massability-fy24.md` — a filename data-quality issue, resolved as a
  dedupe, not as an SRC relocation.)
- **Shared labor-rights / RA references:** stay HERE even though they'd help any state
  worker — provenance/intended-audience (the chapter) governs, not generic
  usefulness. MassAbility-DB links if it needs them.
- **Economic comparables (CPI, RPP, peer/claims-examiner wages):** stay HERE because
  their **purpose-of-inclusion** is VDE compensation bargaining, even though the
  dataset's subject is generic. The same series added for an unrelated program would
  belong in MassAbility-DB.
- **Peer-state comparisons:** other states' **DDS** stats/examiner pay are in scope;
  other states' VR or developmental-services data are not.
- **CTHRU MRC payroll:** the full MRC payroll is umbrella-level; the **DDS-Det
  subset** (examiner-titled records filtered within `chris='MRC'`) is the in-scope
  slice carried in `data/cthru-staffing/`. An agency-wide manager pull is acceptable
  **only** as the documented source from which the DDS-Det subset is built.
- **Field-office data:** a field-office page as a **service description** is
  MassAbility-DB; **office-level VDE headcount/workload/overtime** for the
  Boston/Worcester DDS offices is HERE. Service-catalog content vs VDE workplace data.

## Adding new content — checklist

1. Is it about DDS-Det operations/budget/stats, or about VDEs as workers? If no →
   MassAbility-DB.
2. If it mentions "DDS", confirm it is **Disability Determination Services**, not
   DDS-Dev.
3. If it mentions "Vocational", confirm the **function** is claims adjudication (VDE),
   not counseling (VR).
4. If it is an agency-wide doc, confirm a **DDS-Det section/stat is the reason** it's
   here; otherwise link from MassAbility-DB instead.
5. Add a `.meta.json` sidecar (per [`schemas/`](schemas/)) with source URL,
   retrieved_at, confidence tier, and a DDS-relevance note.
6. If you relocate something out to MassAbility-DB, update
   [`MassAbility-DB/docs/related-repos.md`](https://github.com/Woop91/MassAbility-DB/blob/main/docs/related-repos.md).

## Known data-quality follow-ups (not leaks)

- `data/contract/README.md` + `.meta.json` mislabel "Supplemental Agreement O" as
  DDS — it actually covers **DDS-Dev** Human Service Coordinators. The real VDE
  provisions are the examiner-caseload supplemental agreement + Appendix C VDE titles.
  The combined statewide CBA is correctly in scope, but the DDS-Dev passages
  (~lines 2969–2989 of `seiu-509-cba-2024-2026.md`) should not be treated by
  retrieval as DDS-Det evidence.
- `data/cthru-staffing/leadership-research/massability-commissioners-staff-2026-05-08.md`
  is actually the **Permanent Commission on the Status of Persons with Disabilities**
  (a different body); kept only for one corroborating MRC-commissioner line. Consider
  renaming.
