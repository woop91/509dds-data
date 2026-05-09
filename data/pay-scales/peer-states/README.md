# Peer-State Pay Scales — DDS Examiners + First-Line Supervisors

> Comparable-state salary data for state Disability Determination Services
> (SSDI/SSI claims-examiner) roles. Built to sit alongside the existing
> Massachusetts pay-scale data in `../` and to support peer comparisons used in
> bargaining and policy memos.

## Peer sets — two of them

This folder now holds salary data for **two distinct peer sets**:

1. **Population peers** (workload-comparable): MA, TN, AZ, IN, MD, VA, WA, MO, WI
   — states within ~6–8M population, mirroring `../../docs/peer-states-comparison.json`.
2. **Bargaining peers** (CBA-comparable): MA, MD, WA, **NY, CA, OR, MN, NJ, CT, HI**
   plus PA, NV, IL, MI, AK, MT, ME, VT (latter eight not yet pulled).
   See [`_us-dds-union-landscape.md`](_us-dds-union-landscape.md) for which
   states have confirmed DDS examiner CBAs.

Use the **population set** when arguing about workload (claims processed per
examiner). Use the **bargaining set** when arguing about pay rates and
contract structure.

## Role scope

Per the **Tier 1+2, examiners + supervisors** scope chosen for this pull:

- **Line examiners** — the state classification analogous to MA's Vocational
  Disability Examiner (VDE) bargaining unit
- **First-line supervisors** — the lead/expert/supervisor classification
  immediately above the line examiner

Out of scope: medical/psychological consultants, agency leadership, hearing
officers. Add a separate folder if those become relevant.

## Data tiers

We had planned three tiers; **Tier 1** is currently deferred (BLS blocked the
fetch from three different paths in this session — see "Follow-up data gaps"
below). The data here is **Tier 2**: state-published class specs and
scheduled pay grades.

| Tier | Source | Status |
|---|---|---|
| 1 | BLS OEWS SOC 43-4061 (cross-state benchmark) | ⏸️ deferred — needs `api.bls.gov` registered key |
| 2 | State HR class specs + scheduled pay grades | ✅ this folder |
| 3 | State per-employee actual paid amounts | ⏸️ out of scope this session |

## Files

| Path | Contents |
|---|---|
| `peer-states-pay-summary.json` | Cross-state structured summary — all 9 states (MA + 8 peers), examiner + supervisor, scheduled or estimated ranges with data-quality flag |
| `<STATE>/research-notes.md` | Per-state agency mapping, class titles, class codes, source URLs, gaps |
| `<STATE>/scheduled-rates.json` | Per-state machine-readable scheduled rates (where extractable) |
| `_build_peer_scheduled_rates.py` | Reproducible parser for the four state PDFs cached at `C:/temp/pdfs/` |
| `_us-dds-union-landscape.md` | **National 50-state DDS examiner union representation map.** Identifies the bargaining peer set (vs. the population peer set used here). |
| `_us-dds-union-landscape-{NORTHEAST,MIDWEST-SOUTH,WEST}.md` | Regional source files behind the national landscape map |

## Comparison table — examiner pay

Sorted by data quality, then by examiner annual maximum. MA at top for reference.
"Source" column: 📄 = scheduled rate from state's official salary schedule;
≈ = third-party estimate (Glassdoor / ZipRecruiter / job postings); ◌ = bargaining
unit confirmed but pay schedule blocked this session — see
`peer-states-pay-summary.json → manual_fetch_workflow_for_blocked_states`.

| State | Title | Class | Pay grade | Annual min | Annual max | Source | Bargaining |
|---|---|---|---|---:|---:|---|---|
| **MA** | Vocational Disability Examiner I→III | (BU 8) | Grades 20 / 21 / 23 | $73,555 | **$115,429** | 📄 SEIU 509 chart eff 2026-07-12 | SEIU 509 Local 509 Unit 8 |
| MD | Disability Claims Examiner I | 5260 | Grade 14 ASTD | $62,220 | $96,790 | 📄 DBM std schedule eff 2025-07-01 | AFSCME |
| WA | DDS Adjudicator 3 (senior) | 954 | Range 56 | $63,252 | $84,984 | 📄 OFM GS schedule eff 2025-07-01 | WFSE GG (CBA 2025-27) |
| MN | Disability Examiner | 0871 | grid 14G | $51,140 | $74,174 | 📄 MMB MAPE plan eff 2025-07-01 | **MAPE Unit 214** (independent) |
| VA | DDS Analyst — Junior | ARSD0436 | Pay Band 4 | (start) $69,479 | $117,360¹ | 📄 DHRM eff 2025-06-10 | none |
| OR | Disability Analyst 1 / 2 | 5926 / 5927 | OPEU range | ≈$50,000 | ≈$75,000 | ≈ ZipRecruiter (codes confirmed) | SEIU 503 / OPEU |
| NJ | Claims Adjudicator | #64947 | NJ Range/Step | ≈$53,560 | ≈$68,777 | ≈ Glassdoor (spec confirmed) | CWA Local 1036 (likely) |
| PA | Disability Examiner I / II | TBD | est SC-09 / SC-10 | ≈$52,000 | ≈$76,000 | ≈ agent-inferred grades | SEIU 668 (PA Social Services Union) |
| TN | Disability Claims Examiner | n/a | n/a | ≈$75,813 | ≈$79,699 | ≈ Glassdoor / Salary.com | none (right-to-work) |
| AZ | Disability Determination Specialist | n/a | n/a | ≈$53,152 | ≈$82,282 | ≈ Glassdoor | none |
| WI | Disability Determination Specialist | 49201 | TBD | ≈$48,400 | ≈$65,600 | ≈ ZipRecruiter | none (post-Act 10) |
| IN | Disability Claims Adjudicator | n/a | broadband ~28-29 | ≈$53,559 | ≈$68,777 | ≈ private aggregators | none (since 2005) |
| **NY** | Disability Analyst Trainee/1/2 | TBD SG | TBD | — | — | ◌ PEF chart not pulled | **PEF Unit 5** (PS&T) |
| **CA** | Disability Evaluation Analyst I/II/III | TBD | TBD | — | — | ◌ CalHR blocked | **SEIU 1000 Unit 4** |
| **CT** | Disability Determination Examiner | TBD | est SG-21–23 | — | — | ◌ CT DAS blocked | **AFSCME 714 / SEBAC P-2** |
| **HI** | Disability Determination Examiner | TBD | BU 13 SR | — | — | ◌ DHRD blocked | **HGEA Unit 13** |
| **NV** | Disability Adjudicator | TBD | NV pay grade | — | — | ◌ hr.nv.gov is JS-only | **AFSCME Local 4041** (Aug 2024 — newest CBA in country) |
| **IL** | Disability Adjudicator (multi-level) | TBD | TBD | — | — | ◌ council31.org timeout | **AFSCME Council 31** (likely RC-62) |
| **MI** | Disability Examiner | TBD | P-grade | — | — | ◌ MDCS + SEIU 517M blocked | **SEIU Local 517M / HSS** |
| MO | (not located in public records) | n/a | n/a | n/a | n/a | — | limited |

¹ VA pay band max is misleading on its own — VA's bands are very wide. The
DARS DDS internal "starting salary" model is more informative: $54,106
Trainee 1 → $69,479 Junior, with the Supervisor — Line Unit at $105,212.

## Comparison table — first-line supervisor pay

| State | Title | Class | Pay grade | Annual min | Annual max | Source |
|---|---|---|---|---:|---:|---|
| **MA** | Chief VDE / VDE IV | job code 20-947 | (BU 8) | $89,314 | $95,722 (2023 actual) | CTHRU CY 2023 actual-paid (n=16) |
| MD | Disability Claims Examiner Supervisor | 5263 | Grade 19 STD | $85,963 | **$133,951** | 📄 DBM std schedule eff 2025-07-01 |
| VA | DDS Supervisor — Line Unit | ARSD0252 | Pay Band 5 | (start) $105,212 | $148,455¹ | 📄 DHRM eff 2025-06-10 |
| WA | DDS Adjudicator 5 (lead/expert) | 953 | Range 62 (candidate) | ~$73,284 | ~$98,520 | 📄 OFM GS schedule + manual class-to-range lookup pending |
| TN | not identified | n/a | n/a | ≈$74,705 | ≈$74,705 | ≈ supervisor average |
| WI | Disability Determination Supervisor | 49220 | TBD | n/a | n/a | encoded PDF — extraction pending |
| IN | Lead Worker (informal) | n/a | n/a | n/a | n/a | — |
| AZ | not identified | n/a | n/a | n/a | n/a | — |
| MO | not located | n/a | n/a | n/a | n/a | — |

¹ Same NoVA caveat as above; statewide max is $148,455, NoVA max is $190,130
under the Expanded Range pay bands.

## Headline observations

`peer-states-pay-summary.json → data_quality_summary` documents the formal
data-quality split. Quick read:

1. **Massachusetts examiner peak ($115,429)** is the highest in the
   high-quality peer group (MA / MD / VA / WA) for line examiners — but only
   after the FY27 chart increases. MD examiner peak ($96,790) and MD
   supervisor peak ($133,951) demonstrate that a high-COL state with
   AFSCME representation can pay supervisors meaningfully more.
2. **Right-to-work and post-Act-10 states keep their pay-grade tables hidden.**
   TN, AZ, IN, WI, MO all blocked authoritative extraction — class specs are
   either gated behind PDF-encoded compensation plans or not publicly indexed
   at all. This is itself a data point: state transparency on examiner pay
   correlates with bargaining-unit presence.
3. **Virginia's wide pay bands** make the headline "max" figures misleading.
   The DDS-internal starting salaries ($54k–$69k for analysts, $105k for
   supervisors) are the realistic comparators.
4. **Washington's WFSE-bargained schedule** delivers a clean, machine-readable
   13-step grid with a premium "M*" step — easiest peer state to compare
   against MA's stepped CBA.

## Follow-up data gaps

In rough priority order — pick up on a future session:

1. **BLS OEWS SOC 43-4061** — registered `api.bls.gov` key needed; would let
   us build a single cross-state benchmark file independent of state HR
   transparency variance.
2. **MA Chief VDE chart-rate equivalent** — currently inferring supervisor
   pay from CTHRU 2023 actual-paid. The Unit 8 chart in
   `../effective-2026-07-12.md` does include a "20-947" job code line; needs
   one targeted extraction pass.
3. **WA class 953 → salary range mapping** — OFM class-spec page URL has
   rotted; confirm Range 62 vs. another via the OFM Class-by-Class Salary
   Schedule Excel download.
4. **WI class 49201 / 49220 → pay range** — 229-page Comp Plan PDF has
   encoded tables. Either a JCOER attachment or DPM direct-request resolves
   this.
5. **TN / AZ / IN / MO authoritative scheduled rates** — likely require state
   HR direct contact (FOIA-grade request) or finding an unencoded version of
   the comp plan PDFs.

## Methodology notes

- Effective dates: each state's most recent published schedule as of
  2026-05-08. Where multiple schedules exist (statewide vs. high-COL area),
  both are captured.
- "Estimate" rows use third-party aggregators (Glassdoor, ZipRecruiter,
  Salary.com) — clearly flagged with `≈` in tables and
  `_estimate_caveat` in the JSON. Do not treat estimate rows as
  bargaining-grade evidence; they exist to backfill states whose own HR
  systems do not publish their schedules.
- MA figures use the SEIU 509 Unit 8 chart for examiners (`../vde-grades-extracted.json`)
  and CTHRU 2023 actual-paid for supervisors (`../vde-annual-salary-aggregates.json`).
  Replace with chart-rate when the Chief VDE row gets parsed.
- Reproducibility: the four cached PDFs at `C:/temp/pdfs/{md,va,wa,wi}.pdf`
  drive `_build_peer_scheduled_rates.py`. Re-fetch from the URLs in each
  state's `scheduled-rates.json` then re-run the script to refresh.
