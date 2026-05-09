// Fetch peer-state DDS examiner pay schedules + class specs that gateway-block
// headless requests when run from the developer's local IP. From a GitHub
// Actions runner with a real Chromium session, most of these come through.
//
// Output: PDFs and HTML pages saved under /tmp/peer-state-pdfs/ for the
// downstream parser at data/pay-scales/peer-states/_build_blocked_state_rates.py
//
// Run locally: node scripts/playwright-fetch-peer-states.js
// Run in CI:   wired into .github/workflows/peer-states-pay-refresh.yml
//
// Tuple shape:    [url, outRel, type, referer]
// type 'binary'   -> save raw response bytes (PDFs)
// type 'page'     -> save full rendered HTML (index pages, contract pages)

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_ROOT = process.env.PEER_STATE_PDF_DIR || '/tmp/peer-state-pdfs';

// Targets organized by state, in priority order. Multiple URLs per state
// because we don't know which exact filename will be live on May 16; the
// parser will glob and pick whichever PDFs landed.
const TARGETS = [
  // ─── New York — PEF Bargaining Unit 5 (Professional, Scientific & Technical) ───
  ['https://www.cs.ny.gov/businesssuite/payinfo/salary/',
   'NY/_index-cs-ny-payinfo.html', 'page', null],
  ['https://www.pef.org/contract/',
   'NY/_index-pef-contract.html', 'page', null],
  ['https://www.pef.org/wp-content/uploads/PS-T-Salary-Schedule.pdf',
   'NY/pef-pst-salary-schedule.pdf', 'binary', 'https://www.pef.org/contract/'],

  // ─── California — SEIU Local 1000 Bargaining Unit 4 (Office and Allied) ───
  ['https://www.calhr.ca.gov/Pages/Pay-Scales.aspx',
   'CA/_index-calhr-pay-scales.html', 'page', null],
  ['https://www.calhr.ca.gov/Documents/pay-scale-alpha.pdf',
   'CA/calhr-pay-scale-alpha.pdf', 'binary', 'https://www.calhr.ca.gov/Pages/Pay-Scales.aspx'],
  ['https://www.calhr.ca.gov/Documents/pay-scale-sec-03.pdf',
   'CA/calhr-pay-scale-sec03.pdf', 'binary', 'https://www.calhr.ca.gov/Pages/Pay-Scales.aspx'],
  ['https://www.seiu1000.org/contract',
   'CA/_index-seiu1000-contract.html', 'page', null],

  // ─── Connecticut — AFSCME Local 714 / SEBAC P-2 (Social and Human Services) ───
  ['https://portal.ct.gov/das/statewide-hr/compensation/salary-schedules',
   'CT/_index-ct-das-salary-schedules.html', 'page', null],
  ['https://portal.ct.gov/das/statewide-hr/compensation',
   'CT/_index-ct-das-comp.html', 'page', null],
  ['https://www.council4.org/contracts/',
   'CT/_index-afscme-c4-contracts.html', 'page', null],

  // ─── Hawaii — HGEA Bargaining Unit 13 (Professional and Scientific) ───
  ['https://dhrd.hawaii.gov/state-personnel-system/classes-and-pay/',
   'HI/_index-dhrd-classes-pay.html', 'page', null],
  ['https://www.hgea.org/contracts/',
   'HI/_index-hgea-contracts.html', 'page', null],

  // ─── Nevada — AFSCME Local 4041 (Aug 2024, newest DDS CBA in country) ───
  ['https://hr.nv.gov/Resources/SalarySchedule/',
   'NV/_index-hr-nv-salary.html', 'page', null],
  ['https://nvsea.com/',
   'NV/_index-nvsea.html', 'page', null],

  // ─── Illinois — AFSCME Council 31 (RC-62, Human Services Professional) ───
  ['https://council31.org/contracts/state/',
   'IL/_index-c31-contracts.html', 'page', null],
  ['https://cms.illinois.gov/employees/personnel/labor.html',
   'IL/_index-il-cms-labor.html', 'page', null],

  // ─── Michigan — SEIU Local 517M / HSS (Human Services Support) ───
  ['https://www.michigan.gov/mdcs',
   'MI/_index-mdcs.html', 'page', null],
  ['https://seiu517m.org/contracts/',
   'MI/_index-seiu517m-contracts.html', 'page', null],

  // ─── Pennsylvania — SEIU Local 668 (PA Social Services Union) ───
  ['https://www.oa.pa.gov/Programs/PCOMP/Pages/default.aspx',
   'PA/_index-pa-oa-pcomp.html', 'page', null],
  ['https://seiu668.org/contracts-and-constitution/',
   'PA/_index-seiu668-contracts.html', 'page', null],

  // ─── Oregon — SEIU Local 503 / OPEU (DHS Coalition) ───
  ['https://apps.oregon.gov/DAS/Classification-Compensation/',
   'OR/_index-or-das-class-comp.html', 'page', null],
  ['https://seiu503.org/your-contract/',
   'OR/_index-seiu503-contract.html', 'page', null],

  // ─── New Jersey — CWA Local 1036 / IFPTE 195 ───
  ['https://info.csc.state.nj.us/jobspec/',
   'NJ/_index-nj-csc-jobspec.html', 'page', null],
  ['https://cwanjstateworkers.org/',
   'NJ/_index-cwa-nj.html', 'page', null],

  // ─── Minnesota — re-fetch MAPE contract appendix to get step grid (was missed locally) ───
  ['https://www.mape.org/contract',
   'MN/_index-mape-contract.html', 'page', null],
  ['https://mn.gov/mmb/employee-relations/laws-policies-and-rules/salary-plans/',
   'MN/_index-mmb-salary-plans.html', 'page', null],
];

function pad(s, n) { return (String(s) + ' '.repeat(n)).substring(0, n); }

(async () => {
  console.log(`Targets: ${TARGETS.length}  Output: ${OUT_ROOT}`);
  fs.mkdirSync(OUT_ROOT, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
               '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 900 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' },
  });
  const page = await context.newPage();
  const visitedReferers = new Set();
  const results = [];

  for (const [url, outRel, type, referer] of TARGETS) {
    const out = path.join(OUT_ROOT, outRel);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const t0 = Date.now();
    try {
      if (referer && !visitedReferers.has(referer)) {
        try {
          await page.goto(referer, { waitUntil: 'domcontentloaded', timeout: 20000 });
          visitedReferers.add(referer);
        } catch {}
      }

      if (type === 'binary') {
        const resp = await context.request.get(url, {
          timeout: 60000,
          headers: referer ? { Referer: referer } : {},
        });
        const status = resp.status();
        if (!resp.ok()) {
          results.push({ url, status, ok: false, bytes: 0, ms: Date.now() - t0, out });
          console.log(`${pad(status, 5)} ${pad('FAIL', 6)} ${pad('-', 12)} ${url}`);
          continue;
        }
        const buf = await resp.body();
        // sanity: real PDFs start with %PDF
        const isPdf = buf.length > 4 && buf.slice(0, 4).toString() === '%PDF';
        if (!isPdf) {
          fs.writeFileSync(out + '.error.html', buf);
          results.push({ url, status, ok: false, reason: 'not-a-pdf', bytes: buf.length, ms: Date.now() - t0 });
          console.log(`${pad(status, 5)} ${pad('NOTPDF', 6)} ${pad(buf.length + 'B', 12)} ${url}`);
          continue;
        }
        fs.writeFileSync(out, buf);
        results.push({ url, status, ok: true, bytes: buf.length, ms: Date.now() - t0, out });
        console.log(`${pad(status, 5)} ${pad('PDF', 6)} ${pad(buf.length + 'B', 12)} ${outRel}`);
      } else if (type === 'page') {
        const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(1500);
        const html = await page.content();
        fs.writeFileSync(out, html);
        // Also extract any PDF links from this page so the parser can chase them
        const pdfLinks = await page.evaluate(() =>
          Array.from(document.querySelectorAll('a[href$=".pdf"], a[href*=".pdf?"]'))
               .map(a => ({ href: a.href, text: (a.textContent || '').trim().substring(0, 200) }))
        );
        if (pdfLinks.length) {
          fs.writeFileSync(out.replace(/\.html$/, '.pdf-links.json'), JSON.stringify(pdfLinks, null, 2));
        }
        results.push({
          url, status: resp ? resp.status() : null, ok: true, bytes: html.length,
          pdfLinks: pdfLinks.length, ms: Date.now() - t0, out,
        });
        console.log(`${pad(resp?.status() ?? '?', 5)} ${pad('PAGE', 6)} ${pad(html.length + 'B', 12)} ${outRel}  (${pdfLinks.length} pdf links)`);
      }
    } catch (e) {
      results.push({ url, ok: false, error: e.message.substring(0, 200), ms: Date.now() - t0, out });
      console.log(`---   ERR    -            ${url}`);
      console.log(`      ${e.message.substring(0, 120)}`);
    }
  }

  // Manifest with provenance — used by the parser to know what to look at
  const manifestPath = path.join(OUT_ROOT, '_manifest.json');
  const manifest = {
    fetchedAt: new Date().toISOString(),
    tool: 'playwright-' + require('playwright/package.json').version,
    targetCount: TARGETS.length,
    okCount: results.filter(r => r.ok).length,
    failCount: results.filter(r => !r.ok).length,
    totalBytes: results.filter(r => r.ok).reduce((s, r) => s + (r.bytes || 0), 0),
    results,
  };
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

  console.log(`\nManifest: ${manifestPath}`);
  console.log(`Summary: ${manifest.okCount}/${TARGETS.length} OK, ${manifest.totalBytes} bytes`);

  await browser.close();
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
