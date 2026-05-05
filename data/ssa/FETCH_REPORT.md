## SSA DOCUMENT FETCH REPORT — 2026-05-05

### FILES SAVED

#### Annual Performance Reports
1. apr-fy24-extracted.md (144 KB)
   - Source: SSA_FY24_APR.pdf
   - Contains: FY2024 performance results, DDS state performance tables
   - Status: Successfully extracted via Firecrawl

2. apr-fy25-extracted.md (22 KB)  
   - Source: Overview of Our Fiscal Year 2025 Performance Results.pdf
   - Contains: FY2025 summary performance data
   - Status: Successfully extracted via Firecrawl

#### Congressional Justifications
1. cj-fy25-extracted.md (799 KB)
   - Source: FY25-JEAC.pdf (Justification of Estimates for Appropriations Committees)
   - Contains: DDS budget authority, work-year allocation (13,555 WY in FY2025), state regional performance
   - Status: Successfully extracted via Firecrawl

#### Source Metadata
- apr-fy24.source.txt
- apr-fy25.source.txt
- cj-fy25.source.txt
- dds-section-fy25.md (extracted DDS-specific budget section)

### KEY FINDINGS

#### DDS Budget Allocation by State
**DISCOVERY: Budget allocations are NATIONAL-ONLY in Congressional Justification**
- SSA publishes total DDS work-years (13,555 in FY2025) and national budget authority
- NO per-state DDS budget allocations found in CJ-FY25
- Work assignments to states are operational/admin matters, not in CJ budget appendix

#### DDS Performance Data Located
- FY24 APR contains state-by-state disability determination performance metrics
- Metrics include: processing times, quality review rates, pending case backlogs
- State performance tables extracted to apr-fy24-extracted.md

#### FY2026 Congressional Justification
- Could not retrieve due to Firecrawl credit exhaustion
- Would require additional credits or alternative download method

### EXTRACTION BLOCKERS
- FY26 CJ: Credits exhausted during processing (4 simultaneous PDFs)
- Direct HTTP downloads: Blocked by ssa.gov CDN (Access Denied)
- Resolution: Use Firecrawl scrape (successful) or obtain PDFs via SSA direct links with proxy

### NEXT STEPS
- Parse state performance tables from apr-fy24-extracted.md into CSV
- If per-state DDS budget allocations needed: check SSA regional office financial reports (separate publication)
