# FY22 % Allowed reconciliation — MA report vs SSA FYWL

**Resolved 2026-05-08 (partial).** This document addresses §7.1 of the data-gap punch list: the discrepancy between MA's stated FY22 allowance rate (57.0%) and the SSA FYWL all-state file's MA FY22 figure (46.76%).

## What the SSA CSV actually contains for MA FY22

From `data/ssa/ssa-sa-fywl-all-states-2001-2024.csv` (verified 2026-05-08 against the upstream SSA URL — same content, no FY23/FY24 yet published):

| Field (column) | Value |
|---|---|
| Region Code | BOS |
| State Code | MA |
| Date Type | FY |
| Date | 2022 |
| Adult Receipts | 32,079 |
| Favorable Adult Determinations | 10,354 |
| All Adult Determinations | 23,418 |
| **Adult Favorable Determination Rate** | **44.21%** |
| SSI Disabled Child (DC) Receipts | 4,347 |
| Favorable SSI Child (DC) Determinations | 2,059 |
| All SSI Disabled Child Determinations | 3,130 |
| SSI Disabled Child Allowance Rate | 65.78% |
| All Determinations (adult + child combined) | 26,548 |
| All Favorable Determinations | 12,413 |
| **Favorable Determination Rate (combined)** | **46.76%** |

So the SSA "46.76%" the user cited is the **combined adult + child** favorable rate (column 28). The adult-only rate is 44.21% (column 17). Both are reasonable to cite depending on whether you're talking about all SSDI/SSI claims or only the adult sub-population.

## Where does the MA "57.0%" figure come from?

The FY22 MRC Annual Report is **not currently in the repo** (only FY23, FY24, FY25 are present — see `data/ma-annual-reports/`). Without the source document, the 57% figure can't be located directly. However, an 11-point divergence between a state agency's reported allowance rate and the federal SSA figure is common and almost always methodology-driven. Likely sources of the gap:

1. **Technical/non-medical denials excluded.** State reports often quote allowance rates only over **medically-decided** claims, while SSA FYWL includes denials for non-medical reasons (not returning forms, ineligible for benefits administratively, etc.). Excluding ~15-20% of non-medical denials from the denominator typically lifts the allowance rate by 5-15 points.
2. **SFY vs FFY mismatch.** Massachusetts state fiscal year runs Jul 1 – Jun 30; federal fiscal year runs Oct 1 – Sep 30. A 9-month overlap, 3-month divergence. State-reported "FY22" covers Jul 2021 – Jun 2022; federal "FY22" covers Oct 2021 – Sep 2022.
3. **Initial-only vs all-determinations.** State reports may quote initial-claim allowance only, while SSA FYWL includes initial + reconsideration + continuing review. Reconsiderations have lower allowance rates, so excluding them raises the headline number.
4. **Adult-only vs combined.** The adult-only SSA figure is 44.21%. If MA reports adult-only with technical denials stripped, the figure could rise into the 50-60% range.

## Adjacent finding: MA favorable rate trend 2001–2024

While checking the FY22 row, I extracted the full MA adult favorable-determination rate series. Worth recording as a standalone time-series:

| FY | Favorable | All | Adult Favorable Rate |
|---:|---:|---:|---:|
| 2001 | 16,889 | 37,687 | 44.81% |
| 2002 | 17,936 | 40,394 | 44.40% |
| 2003 | 19,576 | 43,575 | 44.92% |
| 2004 | 20,171 | 45,061 | 44.76% |
| 2005 | 19,902 | 43,974 | 45.26% |
| 2006 | 18,915 | 42,181 | 44.84% |
| 2007 | 21,095 | 46,350 | 45.51% |
| 2008 | 19,710 | 43,744 | 45.06% |
| 2009 | 20,073 | 44,603 | 45.00% |
| 2010 | 21,708 | 51,287 | 42.33% |
| 2011 | 18,928 | 46,294 | 40.89% |
| 2012 | 19,352 | 49,298 | 39.26% |
| 2013 | 19,639 | 48,948 | 40.12% |
| 2014 | 18,769 | 48,213 | 38.93% |
| 2015 | 17,419 | 44,116 | 39.48% |
| 2016 | 15,958 | 40,464 | 39.44% |
| 2017 | 15,370 | 39,556 | 38.86% |
| 2018 | 14,243 | 37,132 | 38.36% |
| 2019 | 14,537 | 36,046 | 40.33% |
| 2020 | 14,213 | 32,594 | 43.61% |
| 2021 | 11,205 | 27,728 | 40.41% |
| 2022 | 10,354 | 23,418 | 44.21% |
| 2023 | 11,690 | 29,211 | 40.02% |
| 2024 | 11,143 | 30,896 | 36.07% |

**Headline trend:** MA's adult favorable rate dropped from **44.81% in FY01 to 36.07% in FY24** — a structural decline of nearly 9 percentage points over 23 years. The FY22 spike to 44.21% (post-pandemic catchup) appears to be a temporary reversal — FY24 fell back to the long-term decline trajectory.

This independent series is useful evidence for bargaining ("MA's allowance rate has fallen as DDS has been understaffed") regardless of whether the §7.1 specific 57%/46.76% reconciliation is ever closed.

## Status

| Item | Status |
|---|---|
| SSA "46.76%" verified | ✅ confirmed (column 28: combined adult + child favorable rate, MA FY22) |
| Adult-only SSA figure | ✅ derived (44.21%) |
| MA "57.0%" source located | ❌ requires FY22 MRC Annual Report (still in §6 gap list) |
| Methodology gap explanation | ⚠️ characterized but not confirmed; needs the MA report's own footnotes |
| 2001-2024 MA favorable-rate trend series | ✅ extracted as adjacent value-add |

## Next step to fully close §7.1

Acquire FY22 MRC Annual Report. Not findable at current mass.gov URLs (Google indexes the rotated pre-2023 paths, all 404 today). Best avenues:
1. **Wayback Machine** — `web.archive.org/web/2023*/mass.gov/doc/mrc-fy22-annual-report*`
2. **Direct PRR** to MRC for the FY22 Section 9F report
3. **Massachusetts Legislature archive** — Section 9F reports must be filed with House and Senate; `malegislature.gov/Reports/` has historical filings
