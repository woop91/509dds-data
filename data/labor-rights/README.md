# Labor Rights — Filing & Reference Materials

Reference materials for SEIU Local 509 stewards and members navigating workplace claims: union grievances, discrimination, wages, safety, leave, and civil-service appeals.

> ⚠ **Status:** Scraped public agency content + interpretive guides. **Not legal advice.** Each derived guide cites the specific source file/line so any fact can be verified back to its agency origin.

## What's here

This directory holds three layers of content, designed to read top-down:

| Layer | Files | Purpose |
|---|---|---|
| **Synthesized guides** | `00-MEMBER-GUIDE.md`, `00-CHEATSHEET.md`, `00-INDEX.md`, `00-ma-labor-law-reference.md` | Member-facing plain-language guide, steward cheat sheet, topic-organized index, and statute index |
| **Agency landing pages** | `01-` through `11-` (11 files) | One file per enforcement agency — what each agency does, contact info, scope of authority |
| **Filing-procedure subpages** | `sub-*` (27 files) | Drill-down details: statutes of limitations, complaint forms, hearing procedures, appeal rights |

**Structured extract:** [`agencies.json`](agencies.json) contains the queryable subset — agency contacts, jurisdictional scope, statutes enforced, and filing deadlines with citations back to source files. Use this for app integrations rather than parsing markdown.

## Audience

- **Stewards** at MassAbility DDS — first responders to member grievances, accommodation requests, discipline meetings
- **Members** with active workplace problems — pay disputes, denied accommodations, retaliation concerns, civil service appeals
- **509dds.com developers** building member-facing rights/filing routes — start with `agencies.json` for structured data, fall back to markdown for narrative content

## Coverage

Twelve enforcement agencies / programs:

| # | Agency | Scope | Primary statute |
|---|---|---|---|
| 01 | MA Department of Labor Relations (DLR) | Public-sector ULPs | M.G.L. c. 150E |
| 02 | MA Commission Against Discrimination (MCAD) | State discrimination/accommodation | M.G.L. c. 151B |
| 03 | MA AG Fair Labor Division | Wages, sick time, wage theft | M.G.L. c. 149 §§ 148, 148C, 150 |
| 04 | MA Department of Labor Standards (DLS) | Public-sector workplace safety | MA Public Sector OSHA State Plan |
| 05 | MA Department of Industrial Accidents (DIA) | Workers' compensation | M.G.L. c. 152 |
| 06 | MA Civil Service Commission (CSC) | Discipline/bypass/layoff appeals | M.G.L. c. 31 |
| 07 | MA State Ethics Commission | Conflict of interest | M.G.L. c. 268A |
| 08 | EEOC (federal) | Federal discrimination | Title VII, ADA, ADEA, GINA |
| 09 | US DOL Wage and Hour Division | Federal wage/hour, FMLA | FLSA, FMLA |
| 10 | OSHA (federal) | Private-sector safety + cross-statute whistleblower | OSH Act + 25+ retaliation statutes |
| 11 | NLRB | Private-sector labor relations | NLRA |
| — | DFML / PFML | State paid family/medical leave | M.G.L. c. 175M |

## Headline filing deadlines

The single most common cause of lost claims is missing a deadline. The most-cited:

| Claim | Deadline | Source |
|---|---|---|
| MA DLR prohibited-practice charge (c. 150E) | **6 months** from knowledge | `sub-01-dlr-ulp-procedures.md:103` |
| MA MCAD discrimination complaint (c. 151B) | **300 days** from last act | `sub-02-mcad-deadline.md:55` |
| MCAD CBA-grievance tolling exception | 300 days from when employee knew/should have known of discrimination basis | `sub-02-mcad-deadline.md:63` |
| EEOC charge (extended in MA via 151B parity) | **300 days** | `sub-08-eeoc-how-to-file.md:34` |
| OSHA safety/health complaint | **<6 months** | `10-osha.md:15` |
| OSHA whistleblower retaliation | **30–180 days** by statute | `10-osha.md:17` |
| NLRB ULP charge (private sector) | 6 months (NLRA § 10(b)) | (statutory) |
| MA Wage Act civil suit (c. 149 § 148) | 3 years; mandatory triple damages | (statutory) |
| MA CSC pre-hearing scheduled within | 60 days of receiving appeal | `sub-06-csc-appeals-process.md:36` |
| MA CSC reconsideration | 10 days | `sub-06-csc-appeals-process.md:163` |

## Sources & confidence

| Tier | Sources | Confidence |
|---|---|---|
| **Authoritative (primary)** | Direct scrapes of mass.gov, eeoc.gov, dol.gov, osha.gov, nlrb.gov via Firecrawl, May 2026 | Verified against live agency publication on scrape date |
| **Synthesized (derived)** | `00-` prefixed guides built from the primary scrapes — every fact citation traces back to a `sub-` or numbered file with line reference | Authority depends on the cited primary source |
| **Statutory (well-established)** | NLRA § 10(b) 6-month SOL, c. 149 § 150 triple damages, FLSA 2/3-year SOL — facts not pulled from a specific scrape | Established Massachusetts/federal labor law |

The synthesized guides (`00-CHEATSHEET.md`, `00-MEMBER-GUIDE.md`) are reference compilations, not legal advice. Treat them as a starting point for steward intake and member education; refer to a labor attorney for specific case strategy.

## Updating

Agency websites update their procedural details (deadlines, forms, addresses) several times per year. The recommended cadence:

| Action | When |
|---|---|
| Re-scrape primary agency landings (`01-` through `11-`) | Every 6 months |
| Re-scrape filing-procedure subpages (`sub-*`) | Annually, or after any reported procedural change |
| Refresh the synthesized cheat sheet/member guide | Whenever a deadline or contact changes |
| Verify `agencies.json` against current agency sites | Quarterly for the highest-traffic agencies (DLR, MCAD, AGO Fair Labor) |

Re-scrape using the Firecrawl CLI; the URL list is in the heading metadata of each agency landing file.

## License

This directory aggregates public-domain government content from Massachusetts and federal agencies. Original source documents retain their respective licenses (public domain for federal, mass.gov terms for state).

The synthesized guides and `agencies.json` extract are © SEIU Local 509 / DDS chapter — free to redistribute with attribution for member education and union work.
