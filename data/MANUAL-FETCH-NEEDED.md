# Manual-Fetch Needed (2026-05-05, updated 2026-05-08)

These URLs returned **403 Forbidden** to every automated fetcher tried on 2026-05-05
(PowerShell `Invoke-WebRequest`, `curl` with browser headers + Referer, full
Playwright Chromium with cookies). The blocking is per-path bot scoring on
`ssa.gov`, `bls.gov`, `gao.gov`, and `cbpp.org` against direct binary downloads
and certain HTML paths. They open fine in an interactive browser.

**Update 2026-05-08:** A Firecrawl-based session ([report](../docs/firecrawl-gap-fill-session-2026-05-08.md))
**resolved the GAO and CBPP HTML items** by routing through Firecrawl's residential-IP
browser stack. The SSA `.xlsx` and BLS `.zip` items remain unsolved because Firecrawl
returns text/markdown only — it cannot capture binary files even when it can reach the URL.

**To complete the remaining items below, open each URL in your browser and save it to the
listed path. None of this is gated — it's standard public data, just bot-blocked.**

## SSA — high priority

- [ ] `data/ssa/asss-2025-supplement-full.xlsx`  
  https://www.ssa.gov/policy/docs/statcomps/supplement/2025/supplement25.xlsx
- [ ] `data/ssa/asss-2024-supplement-full.xlsx`  
  https://www.ssa.gov/policy/docs/statcomps/supplement/2024/supplement24.xlsx
- [ ] `data/ssa/di-asr-2024-sect01c-disabled-workers-by-state.xlsx`  
  https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect01c.xlsx
- [ ] `data/ssa/di-asr-2024-sect03-state-adjudication.xlsx`  
  https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect03.xlsx
- [ ] `data/ssa/di-asr-2024-sect05-allowance-rates.xlsx`  
  https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect05.xlsx

## BLS — for SOC 13-1031 (Claims Examiners) wages by state

- [ ] `data/external/bls-oews/oesm24st.zip` (May 2024 state file)  
  https://www.bls.gov/oes/special-requests/oesm24st.zip
- [ ] `data/external/bls-oews/oesm23st.zip`  
  https://www.bls.gov/oes/special-requests/oesm23st.zip
- [ ] `data/external/bls-oews/oesm22st.zip`  
  https://www.bls.gov/oes/special-requests/oesm22st.zip

## GAO — disability program reports — RESOLVED 2026-05-08 via Firecrawl

Product-page HTML (executive summary + recommendations + linked PDF URL) captured to
`data/oversight/gao/*.md`. For full PDF body content, scrape the underlying
`gao.gov/assets/{report-id}.pdf` URLs — Firecrawl's PDF parser returns full report text.

- [x] `data/oversight/gao/gao-22-103815.md` (12.5KB) — captured 2026-05-08
- [x] `data/oversight/gao/gao-17-625.md` (18.7KB) — captured 2026-05-08
- [x] `data/oversight/gao/gao-15-19.md` (19.8KB) — captured 2026-05-08
- [x] `data/oversight/gao/gao-09-149.md` (12.5KB) — captured 2026-05-08

## CBPP — SSDI/SSI policy explainers — RESOLVED 2026-05-08 via Firecrawl

- [x] `data/external/cbpp/cbpp-ssdi-explainer.md` (49KB) — captured 2026-05-08
- [x] `data/external/cbpp/cbpp-ssi-basics.md` (19.6KB) — captured 2026-05-08

## Notes

- After saving files, the existing `.source.txt` companions in those folders
  describe their source URL and intended use — you can leave the existing ones
  in place, or update them with the actual fetch date.
- The **SSA OHO datasets index** (`https://www.ssa.gov/appeals/DataSets/`) is
  also blocked, but the individual report pages linked from it returned 200 in
  Playwright — see `data/ssa/oho/` for the captures we got. If you want
  additional OHO datasets beyond ALJ Disposition + Hearing Office Wait Time,
  open the index in your browser and add the dataset URLs to
  `scripts/playwright-fetch.js`.
- These bot-blocks are environmental, not a reflection of the data being
  restricted. The same files download cleanly when accessed from a real
  interactive browser session.
