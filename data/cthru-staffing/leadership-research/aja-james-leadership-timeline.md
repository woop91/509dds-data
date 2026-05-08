# Aja James — DDS-Det Leadership Timeline

**Captured:** 2026-05-08 via Firecrawl scrapes of mass.gov + bhclearinghouse.org + state audit reports.

This document consolidates publicly-available evidence on Aja James's career at MA DDS-Det (Disability Determination Services) and the surrounding leadership chain. It addresses Section 1 of the data-gap punch list. Sources are linked inline; primary captures live in this folder.

> ⚠ **Agency disambiguation:** all "DDS" references below are **Disability Determination Services** (the SSI/SSDI adjudication division within MassAbility/MRC). They are NOT the Department of Developmental Services (DDS-Dev), which is a separate ~5,500-staff agency outside scope. See [`docs/dds-det-vs-dds-dev.md`](../../../docs/dds-det-vs-dds-dev.md).

## Aja James — career timeline

| Year(s) | Role | Source |
|---|---|---|
| ~2002 | Started at DDS as a **Vocational Disability Examiner (VDE)**, encouraged by her mother (Juanita Taylor, then a DDS employee). Recent graduate of Saint Paul's College (HBCU, Lawrenceville VA), relocated from Connecticut. | [Mass.gov press release 2/25/2021](aja-james-mass-gov-press-release-2021-02-25.md) |
| 2002–~2015 | Multiple VDE-track promotions ("promoted numerously throughout her tenure"). CTHRU payroll snapshots place her at **Grade D** (a senior VDE grade) in 2013 and 2015 with annual rates of $73,936 (2013) and $84,508 (2015). | [`vde-annual-salary-aggregates.json`](../vde-annual-salary-aggregates.json) |
| ~2015–March 2021 | Moved into **management ranks** (out of the VDE bargaining unit), so she drops out of the existing VDE-only CTHRU payroll dataset. **Most recent role before promotion: Director of Statewide Support Operations.** | [Mass.gov press release 2/25/2021](aja-james-mass-gov-press-release-2021-02-25.md) |
| March 7, 2021 | Took office as **Assistant Commissioner, Disability Determination Services** (DDS-Det), MRC. Announced 2/25/2021 by MRC Commissioner Toni Wolf. | [Mass.gov press release 2/25/2021](aja-james-mass-gov-press-release-2021-02-25.md) |
| Sept 2023 → present (verified) | Still listed as **Assistant Commissioner of DDS** in MassAbility-prepared materials. | [BH Clearinghouse MRC Behavioral Health presentation, Sept 2023](https://www.bhclearinghouse.org/siteassets/uploads//2023/09/MRC_Behavioral-Health-presentation.pdf) |

### Concurrent / ancillary roles (career-long)

- **SEIU Local 509 union steward** (during her VDE/staff years; pre-management)
- Elected to **SEIU Local 509 Chapter Board**
- Elected to **SEIU Local 509 Joint Executive Board**
- **Co-Chair, Black Managers Committee** (state employee affinity group)
- **MPA, Suffolk University** — earned at night while working at DDS

## DDS-Det leadership chain at three reference points

### SFY 2012 — MRC Senior Management Team (full org from MRC AR 2012)

| Role | Holder |
|---|---|
| Commissioner, MRC | **Charles Carr** |
| Deputy Commissioner | Kasper Goshgarian |
| General Counsel | Richard Arcangeli |
| Chief Financial Officer | Robert Perry |
| Asst Comm, Community Living | Debra Kamen |
| Asst Comm, Vocational Rehabilitation | Joan Phillips |
| **Asst Comm, Disability Determination Services** | **Barbara Kinney** |

Source: [MRC Annual Report 2012](mrc-annual-report-2012.md) (mass.gov DOC). The same report indicates the Asst Comm DDS position has been held continuously since **September 2008** (so Kinney's tenure began Sept 2008). The follow-up FY13 annual report URL on mass.gov returns 404 today — likely a URL rotation, not removal.

### July 2018 — partial (audit-letter scope only)

| Role | Holder | Source |
|---|---|---|
| Commissioner, MRC | **Toni Wolf** | [State Auditor performance audit 2018-0054-3S, addressed to "Ms. Toni Wolf, Commissioner", dated July 3, 2018](state-audit-2018-0054-3s-mrc.md) |
| Asst Comm, DDS-Det | *(not extractable from this scrape — see gaps below)* | — |

The transition from Charles Carr → Toni Wolf at the Commissioner level happened **circa 2015**: a separate biographical sketch of Carr (captured in the volunteer Permanent Commission roster page) describes him as "commissioner of the Massachusetts Rehabilitation Commission until 2015." Exact date and immediate successor (interim?) not confirmed in this pull.

### September 2023 — DDS-Det inner ring (BH Clearinghouse deck)

| Role | Holder |
|---|---|
| Commissioner, MRC/MassAbility | **Toni Wolf** *(per current `mass.gov/orgs/massability` page)* |
| Asst Comm, DDS-Det | **Aja James** |
| Director, Statewide Support Operations (DDS-Det) | **Karen Sampson Johnson** *(email: Karen.Sampson@ssa.gov)* |

Note Sampson Johnson uses an `ssa.gov` email despite being a state employee — DDS-Det staff are issued federal SSA email accounts because the agency is fully SSA-funded under a federal–state agreement, even though personnel are MA state employees. This is a non-obvious detail relevant to records requests (some files may live on federal systems and require FOIA, others on state systems and require PRR).

## Persistent gaps after this pull

1. **Aja James's full pay history 2016–2024.** The existing CTHRU dataset is filtered to VDE classifications only, so it omits her Director and Asst Commissioner years. Resolving this requires re-querying CTHRU without the VDE-class filter (an exec-branch employee lookup, not a Firecrawl task). The `data/pay-scales/_build_vde_pay.py` script's input filter is the bottleneck.

2. **Asst Comm DDS between Barbara Kinney (FY12) and Aja James (Mar 2021).** No primary source recovered in this pull names the holder(s) for FY14–FY20. Possible avenues:
   - Internet Archive Wayback snapshots of `mass.gov/orgs/mrc/about/leadership` from 2015, 2017, 2019
   - PRR for "MRC Asst Commissioner DDS appointment letters 2013–2021"
   - LinkedIn searches for "Assistant Commissioner Disability Determination Massachusetts" (likely yields a name; cached profiles)

3. **Full DDS-Det internal org chart for 2018, 2020, 2024.** Sept 2023 captured (Aja + Karen Sampson Johnson). 2018 has only the MRC Commissioner (Toni Wolf). 2020 and 2024 not captured. Same Wayback / PRR avenues apply.

4. **Charles Carr → Toni Wolf transition exact date.** Approximate: late 2015 to early 2016 based on Carr's "until 2015" biographical note. Press release likely exists on mass.gov and could be searched directly if needed.

## What this pull rules out

- The **MRC Presentation deck** at `mass.gov/doc/mrc-presentation/download` returns its raw `.pptx` ZIP container to Firecrawl, not extracted slide text. PPTX server-side extraction is not supported by Firecrawl scrape; the file would have to be downloaded to disk and run through `firecrawl parse` locally to recover the org chart slide content.
- The historical MRC annual report URLs (`mass.gov/doc/mrc-2016-annual-report/download`, etc.) all 404 today — Google's index still points at the old `/doc/.../download` scheme that mass.gov has since rotated. These reports may still exist under different URLs but were not findable via firecrawl `search` on this pass.

## Captures in this folder

| File | Source URL | Bytes |
|---|---|---|
| `aja-james-mass-gov-press-release-2021-02-25.md` | https://www.mass.gov/news/aja-james-named-assistant-commissioner-disability-determination-services | ~5.8KB |
| `mrc-annual-report-2012.md` | https://www.mass.gov/doc/annual-report-2012-1/download | ~7.9KB |
| `state-audit-2018-0054-3s-mrc.md` | https://www.mass.gov/doc/massachusetts-rehabilitation-commission-0/download | ~17KB |
| `massability-commissioners-staff-2026-05-08.md` | https://www.mass.gov/info-details/commissioners-staff-0 *(Permanent Commission — different body, includes one-line Carr biography only)* | ~42KB |
