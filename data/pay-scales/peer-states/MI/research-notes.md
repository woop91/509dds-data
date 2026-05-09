# Michigan DDS Salary Research

**Status**: Partial — firecrawl out of credits. Data compiled from available web search + direct MDCS site inspection via curl.

## Administering Agency
- **Michigan Department of Health and Human Services (MDHHS), Disability Determination Services**
- Official MDHHS DDS page: https://www.michigan.gov/mdhhs (currently redirects to 404; historical URL structure suggests it was merged under modern health portal)

## Examiner Class Title
- Presumed: **Disability Examiner** or variant (e.g., "Disability Determination Examiner")
- Michigan uses **P-grade structure** for professional staff (P-11, P-12, etc. or numeric equivalents)
- **NOT YET VERIFIED** against Michigan Civil Service Commission classification database (MDCS site access blocked by redirect)

## Supervisor Class Title
- Presumed: **Supervisor, Disability Examination** or **Medical-Vocational Specialist, Supervisory** (common DDS pattern)
- **NOT YET VERIFIED**

## Pay Grade & Scheduled Rates
- **Source Status**: UNABLE TO RETRIEVE
  - Michigan MDCS pay schedules: https://www.michigan.gov/mdcs/csc/compensation/ → 404 or Gravity Forms-protected
  - SEIU Local 517M HSS (Human Services Support) contracts: https://seiu517m.org/contracts/ → no direct PDF links visible in curl output
  - Michigan state pay schedule (standard link): https://www.michigan.gov/mdcs/0,4614,7-147-6877_10005-37574--,00.html → no data returned

## Bargaining Unit
- **SEIU Local 517M / HSS (Human Services Support) Unit**
- **CBA Terms**: Presumed 2025-2027 (typical biennial cycle)
- **Status**: Contract text not retrieved

## Curl Attempts Performed
1. `curl https://seiu517m.org/contracts/` → returned Gravity Forms boilerplate, no PDF links
2. `curl https://www.michigan.gov/mdcs` → SPDOC 26-04, 26-03, 26-02 PDFs listed but no pay schedule
3. `curl https://www.michigan.gov/mdcs/csc/classifications/all-current-classifications` → returned nav links only, no classification data
4. `curl https://www.michigan.gov/mdcs/0,4614,7-147-6877_10005-37574--,00.html` → no output
5. Attempted firecrawl scrape `https://www.michigan.gov/mdcs/csc/compensation` → **insufficient credits**

## Known Data Gaps
- Pay grade code (P-11? P-12? Numeric)
- Step-based salary schedule (if applicable)
- Min/max salary for examiner
- Min/max salary for supervisor
- Effective date of current schedule
- Contract renewal/negotiation status for 2025-2027

## Next Steps (Recommended)
1. **Direct MDCS contact**: Call Michigan Civil Service Commission to request current pay schedule PDFs by grade
2. **SEIU 517M direct contact**: Email seiu517m.org contracts inbox requesting HSS Unit 2025-2027 CBA
3. **Alternate source**: BLS OES wage data for Michigan by SOC 43-4061 (Eligibility Interviewers) — may not align perfectly to DDS examiners
4. **Job posting search**: Indeed, LinkedIn, StateJobs.com for Michigan DDS postings listing salary bands

---

**Research completed**: 2026-05-08
**Researcher notes**: Firecrawl paid skill out of credits. Manual curl + site inspection exhausted. Michigan state websites partially down or restructured.
