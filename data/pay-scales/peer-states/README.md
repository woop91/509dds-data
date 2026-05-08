# Peer-State Pay Scales — DDS Examiners + First-Line Supervisors

> Comparable-state salary data for state Disability Determination Services
> (SSDI/SSI claims-examiner) roles. Built to sit alongside the existing
> Massachusetts pay-scale data in `../` and to support peer comparisons used in
> bargaining and policy memos.

## Peer set

Same population-peer set used in [`../../docs/peer-states-comparison.json`](../../docs/peer-states-comparison.json):
**MA, TN, AZ, IN, MD, VA, WA, MO, WI** — states within roughly 6–8M
population. The peer set was chosen for workload comparability (avoiding the
distortion of comparing MA to CA at 39M or RI at 1M); we re-use it here for
salary so that the workload and pay analyses can be cross-walked.

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

## Comparison table — examiner pay

Sorted by examiner annual maximum (high → low). MA at top for reference.
"Source" column: 📄 = scheduled rate from state's official salary schedule;
≈ = third-party estimate (Glassdoor / ZipRecruiter / job postings).

| State | Title | Class | Pay grade | Annual min | Annual max | Source | Bargaining |
|---|---|---|---|---:|---:|---|---|
| **MA** | Vocational Disability Examiner I→III | (BU 8) | Grades 20 / 21 / 23 | $73,555 | **$115,429** | 📄 SEIU 509 chart eff 2026-07-12 | SEIU 509 Local 509 Unit 8 |
| MD | Disability Claims Examiner I | 5260 | Grade 14 ASTD | $62,220 | $96,790 | 📄 DBM std schedule eff 2025-07-01 | AFSCME |
| WA | DDS Adjudicator 3 (senior) | 954 | Range 56 | $63,252 | $84,984 | 📄 OFM GS schedule eff 2025-07-01 | WFSE GG (CBA 2025-27) |
| VA | DDS Analyst — Junior | ARSD0436 | Pay Band 4 | (start) $69,479 | $117,360¹ | 📄 DHRM eff 2025-06-10 | none |
| TN | Disability Claims Examiner | n/a | n/a | ≈$75,813 | ≈$79,699 | ≈ Glassdoor / Salary.com | none (right-to-work) |
| WI | Disability Determination Specialist | 49201 | TBD | ≈$48,400 | ≈$65,600 | ≈ ZipRecruiter | none (post-Act 10) |
| IN | Disability Claims Adjudicator | n/a | broadband ~28-29 | ≈$53,559 | ≈$68,777 | ≈ private aggregators | none (since 2005) |
| AZ | Disability Determination Specialist | n/a | n/a | ≈$53,152 | ≈$82,282 | ≈ Glassdoor | none |
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
