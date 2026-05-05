# 509dds-data

Open data, source documents, and analysis for **SEIU Local 509's Disability Determination Services (DDS) chapter** in Massachusetts. Backing dataset for [509dds.com](https://509dds.com).

> ⚠ **Critical disambiguation:** "DDS" in this repo means **Disability Determination Services** — the division within MassAbility (formerly MRC) that adjudicates SSI/SSDI claims for the Social Security Administration. It is **NOT** the Department of Developmental Services (a separate MA agency that serves people with intellectual/developmental disabilities). See [`docs/dds-det-vs-dds-dev.md`](docs/dds-det-vs-dds-dev.md).

## What's here

| Folder | Contents |
|---|---|
| [`data/ssa/`](data/ssa/) | SSA public datasets — all-state initial claims (2001–2024), federal QA accuracy review (2007–2022), processing time (FY16–FY26), OIG staffing audit |
| [`data/ma-annual-reports/`](data/ma-annual-reports/) | MassAbility / MRC annual reports as markdown — FY23, FY24, FY25 + State Rehabilitation Council reports FY22–FY24 |
| [`data/contract/`](data/contract/) | SEIU Local 509 Units 8 & 10 Collective Bargaining Agreement 2024–2026 (full text) |
| [`data/pay-scales/`](data/pay-scales/) | Unit 8 salary charts — 5 effective dates from 2024-07-14 through 2026-07-12 + VDE-grade-extracted JSON |
| [`data/cthru-staffing/`](data/cthru-staffing/) | MA Comptroller payroll headcount (CTHRU): VDE counts by grade by year, DDS division totals |
| [`data/ra-process/`](data/ra-process/) | Reasonable Accommodation: state Executive Branch process, application page, MassAbility DDS info, MOD guidance, DLC self-advocacy guide |
| [`data/labor-rights/`](data/labor-rights/) | Labor rights filing & reference: 12 enforcement agencies (DLR, MCAD, AGO Fair Labor, DLS, DIA, CSC, Ethics, EEOC, DOL WHD, OSHA, NLRB, DFML), 24 filing deadlines, member guide + steward cheat sheet + statute index, queryable [`agencies.json`](data/labor-rights/agencies.json) extract |
| [`data/dds-statistics-master-table.json`](data/dds-statistics-master-table.json) | The filled DDS Statistics master table (operational metrics 2013–2025, with PRR/TBD cells flagged) |
| [`docs/`](docs/) | Methodology, data dictionary, agency disambiguation, peer-state comparison |
| [`prr-templates/`](prr-templates/) | Public Records Request templates for filling remaining gaps |

## Headline findings

- **VDE headcount: −44%** from 2019 (232) to 2023 (129) per CTHRU payroll — substantiates "unprecedented staffing vacancies" cited in MA's 2025 Annual Report
- **Senior examiner pipeline collapse**: VDE III went from 44 (2019) to 7 (2023)
- **Cost per case: +30%** from 2018 ($568) to 2024 ($1,071) — fewer staff, higher unit cost
- **MA favorable rate: −5.6 pts** from FY20 (45.82%) to FY24 (40.17%) — steepest decline among population-peer states (TN, IN, MD, VA, WA, MO, WI)
- **National processing time: +110%** from FY16 (110 days) to FY24 (231 days), per SSA — backdrop for state-level pain
- **DDS-Det budget cut: −16.7%** from FY24 ($50.8M) to FY25 ($42.3M)

## Sources & confidence levels

| Tier | Sources | Confidence |
|---|---|---|
| **Authoritative** | SSA-SA-FYWL.csv, DDS-Net-Accuracy.csv, MA annual reports, SEIU 509 CBA, mass.gov RA process pages | Verified against primary publication |
| **Computed** | CE Rate, MER Rate, annual VDE pay max, DDS-Only Total Staff | Derived arithmetically from authoritative inputs |
| **PRR-pending** | DDS budget pre-FY23, homeless case counts, Total Receipts/Dispositions for some years | Awaiting Public Records Request — see [`prr-templates/`](prr-templates/) |

See [`docs/methodology.md`](docs/methodology.md) for full sourcing methodology and known data caveats.

## Audience

The audience for this data is:
- **SEIU Local 509 stewards and members** at MassAbility DDS (Boston + Worcester offices)
- **Bargaining-team negotiators** preparing for contract / staffing arguments
- **509dds.com developers** building member-facing dashboards from this data
- **Researchers** studying disability claim adjudication workforce trends

## Updating

Most sources are static (annual reports, CBAs). The auto-updating sources:

| Dataset | Update cadence | Source URL |
|---|---|---|
| `ssa-sa-fywl-all-states-2001-2024.csv` | Annual, ~Nov | https://www.ssa.gov/disability/data/SSA-SA-FYWL.csv |
| `dds-net-accuracy-by-state-2007-2022.csv` | Annual | https://www.ssa.gov/data/DDS-Net-Accuracy.csv |
| `cdp-time-monthly-fy16-fy26.csv` | Monthly | https://www.ssa.gov/data/fy16-onwards-CDP-Time-Monthly.csv |
| CTHRU payroll | Quarterly (CY+12mo lag) | https://cthru.data.socrata.com/resource/rxhc-k6iz.json?$where=chris='MRC' |

For 509dds.com integration: schedule the Vercel cron to re-fetch SSA CSVs annually each November and CTHRU quarterly. Both endpoints accept browser-UA requests via Firecrawl.

## License

This repository aggregates and analyzes data from public-domain government sources (Social Security Administration, Massachusetts state government). No proprietary data is included. Original source documents retain their respective licenses.

Repo content (READMEs, analysis, JSON extracts, PRR templates) — © SEIU Local 509 / DDS chapter, all rights reserved unless otherwise noted.

## Contact

- 509 DDS Chapter contact: see project memory
- Repo issues / data updates: file a GitHub issue or PR
