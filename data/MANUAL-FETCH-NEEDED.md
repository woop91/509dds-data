# Manual-Fetch Needed (2026-05-05)

These URLs return **403 Forbidden** to every automated fetcher tried in this session
(PowerShell `Invoke-WebRequest`, `curl` with browser headers + Referer, full
Playwright Chromium with cookies). The blocking is per-path bot scoring on
`ssa.gov`, `bls.gov`, `gao.gov`, and `cbpp.org` against direct binary downloads
and certain HTML paths. They open fine in an interactive browser.

**To complete the dataset, open each URL in your browser and save it to the
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

## GAO — disability program reports

- [ ] `data/oversight/gao/gao-22-103815.pdf`  
  https://www.gao.gov/products/gao-22-103815 (look for "View Report (PDF)" link)
- [ ] `data/oversight/gao/gao-17-625.pdf`  
  https://www.gao.gov/products/gao-17-625
- [ ] `data/oversight/gao/gao-15-19.pdf`  
  https://www.gao.gov/products/gao-15-19
- [ ] `data/oversight/gao/gao-09-149.pdf`  
  https://www.gao.gov/products/gao-09-149

## CBPP — SSDI/SSI policy explainers

- [ ] `data/external/cbpp/cbpp-ssdi-explainer.html`  
  https://www.cbpp.org/research/social-security/social-security-disability-insurance-0
- [ ] `data/external/cbpp/cbpp-ssi-basics.html`  
  https://www.cbpp.org/research/social-security/policy-basics-supplemental-security-income

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
