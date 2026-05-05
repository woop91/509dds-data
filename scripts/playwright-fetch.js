// Fetch SSA / BLS / OHO / CBPP / GAO files that block headless requests.
// Uses Playwright Chromium with persistent cookies so each domain only has
// to pass Cloudflare's challenge once before its child requests succeed.
//
// Run from repo root:  node scripts/playwright-fetch.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..');

// type 'binary'   -> save raw response bytes to disk
// type 'page'     -> save full rendered HTML
// type 'tables'   -> extract <table> outerHTML + page text into JSON
const TARGETS = [
  // ─── SSA Annual Statistical Supplement (state determinations) ───
  ['https://www.ssa.gov/policy/docs/statcomps/supplement/2025/supplement25.xlsx',
   'data/ssa/asss-2025-supplement-full.xlsx', 'binary',
   'https://www.ssa.gov/policy/docs/statcomps/supplement/2025/'],
  ['https://www.ssa.gov/policy/docs/statcomps/supplement/2024/supplement24.xlsx',
   'data/ssa/asss-2024-supplement-full.xlsx', 'binary',
   'https://www.ssa.gov/policy/docs/statcomps/supplement/2024/'],

  // ─── SSA DI Annual Statistical Report (state-level rolls + adjudication) ───
  ['https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect01c.xlsx',
   'data/ssa/di-asr-2024-sect01c-disabled-workers-by-state.xlsx', 'binary',
   'https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/'],
  ['https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect03.xlsx',
   'data/ssa/di-asr-2024-sect03-state-adjudication.xlsx', 'binary',
   'https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/'],
  ['https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect05.xlsx',
   'data/ssa/di-asr-2024-sect05-allowance-rates.xlsx', 'binary',
   'https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/'],

  // ─── BLS OEWS state files (SOC 13-1031 inside) ───
  ['https://www.bls.gov/oes/special-requests/oesm24st.zip',
   'data/external/bls-oews/oesm24st.zip', 'binary',
   'https://www.bls.gov/oes/tables.htm'],
  ['https://www.bls.gov/oes/special-requests/oesm23st.zip',
   'data/external/bls-oews/oesm23st.zip', 'binary',
   'https://www.bls.gov/oes/tables.htm'],
  ['https://www.bls.gov/oes/special-requests/oesm22st.zip',
   'data/external/bls-oews/oesm22st.zip', 'binary',
   'https://www.bls.gov/oes/tables.htm'],
  ['https://www.bls.gov/oes/current/oes131031.htm',
   'data/external/bls-oews/oes131031-national-current.html', 'page', null],

  // ─── OHO (post-DDS appeals) public datasets ───
  ['https://www.ssa.gov/appeals/DataSets/',
   'data/ssa/oho/oho-datasets-index.html', 'page', null],
  ['https://www.ssa.gov/appeals/DataSets/03_ALJ_Disposition_Data.html',
   'data/ssa/oho/03-alj-disposition.tables.json', 'tables', null],
  ['https://www.ssa.gov/appeals/DataSets/05_eFile_Office_Wait_Times.html',
   'data/ssa/oho/05-office-wait-times.tables.json', 'tables', null],
  ['https://www.ssa.gov/appeals/DataSets/01_NetStat_Report.html',
   'data/ssa/oho/01-netstat-report.tables.json', 'tables', null],
  ['https://www.ssa.gov/appeals/DataSets/02_HOTS_HOCALC.html',
   'data/ssa/oho/02-hots-hocalc.tables.json', 'tables', null],
  ['https://www.ssa.gov/appeals/DataSets/04_Hearing_Wait_Time.html',
   'data/ssa/oho/04-hearing-wait-time.tables.json', 'tables', null],

  // ─── CBPP state factsheet pages ───
  ['https://www.cbpp.org/research/social-security/social-security-disability-insurance',
   'data/external/cbpp/cbpp-ssdi-overview.html', 'page', null],
  ['https://www.cbpp.org/research/social-security/social-security-disability-insurance-0',
   'data/external/cbpp/cbpp-ssdi-explainer.html', 'page', null],
  ['https://www.cbpp.org/research/social-security/policy-basics-supplemental-security-income',
   'data/external/cbpp/cbpp-ssi-basics.html', 'page', null],

  // ─── GAO disability reports (URLs surfaced by Agent F) ───
  ['https://www.gao.gov/products/gao-22-103815',
   'data/oversight/gao/gao-22-103815-medical-consultants.html', 'page', null],
  ['https://www.gao.gov/products/gao-17-625',
   'data/oversight/gao/gao-17-625-expedited-processing.html', 'page', null],
  ['https://www.gao.gov/products/gao-15-19',
   'data/oversight/gao/gao-15-19-enhanced-policies.html', 'page', null],
  ['https://www.gao.gov/products/gao-09-149',
   'data/oversight/gao/gao-09-149-medical-evidence.html', 'page', null],
];

function pad(s, n) { return (String(s) + ' '.repeat(n)).substring(0, n); }

(async () => {
  console.log(`Targets: ${TARGETS.length}  Output root: ${REPO}`);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
               '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 900 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
    },
  });
  const page = await context.newPage();
  const visitedReferers = new Set();

  const results = [];
  for (const [url, outRel, type, referer] of TARGETS) {
    const out = path.join(REPO, outRel);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const t0 = Date.now();
    try {
      // Warm up the parent page first (gets cookies, passes any challenge)
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
        fs.writeFileSync(out, buf);
        results.push({ url, status, ok: true, bytes: buf.length, ms: Date.now() - t0, out });
        console.log(`${pad(status, 5)} ${pad('OK', 6)} ${pad(buf.length + 'B', 12)} ${outRel}`);
      } else if (type === 'page') {
        const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(1500); // let any late JS finish
        const html = await page.content();
        fs.writeFileSync(out, html);
        results.push({
          url, status: resp ? resp.status() : null, ok: true, bytes: html.length,
          ms: Date.now() - t0, out,
        });
        console.log(`${pad(resp?.status() ?? '?', 5)} ${pad('PAGE', 6)} ${pad(html.length + 'B', 12)} ${outRel}`);
      } else if (type === 'tables') {
        const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(2000);
        const data = await page.evaluate(() => ({
          title: document.title,
          tableCount: document.querySelectorAll('table').length,
          tables: Array.from(document.querySelectorAll('table')).map(t => t.outerHTML),
          bodyText: document.body.innerText.substring(0, 50000),
        }));
        const payload = {
          url,
          fetchedAt: new Date().toISOString(),
          status: resp ? resp.status() : null,
          ...data,
        };
        const json = JSON.stringify(payload, null, 2);
        fs.writeFileSync(out, json);
        results.push({
          url, status: resp ? resp.status() : null, ok: true, bytes: json.length,
          ms: Date.now() - t0, out, tables: data.tableCount,
        });
        console.log(`${pad(resp?.status() ?? '?', 5)} ${pad('TBL', 6)} ${pad(data.tableCount + 'tbl', 12)} ${outRel}`);
      }
    } catch (e) {
      results.push({ url, ok: false, error: e.message, ms: Date.now() - t0, out });
      console.log(`---   ERR    -            ${url}\n      ${e.message.substring(0, 120)}`);
    }
  }

  // Manifest with provenance
  const manifestPath = path.join(REPO, 'data', 'fetch-manifest-2026-05-05.json');
  fs.writeFileSync(manifestPath, JSON.stringify({
    fetchedAt: new Date().toISOString(),
    tool: 'playwright-' + require('playwright/package.json').version,
    targetCount: TARGETS.length,
    okCount: results.filter(r => r.ok).length,
    failCount: results.filter(r => !r.ok).length,
    totalBytes: results.filter(r => r.ok).reduce((s, r) => s + (r.bytes || 0), 0),
    results,
  }, null, 2));
  console.log(`\nManifest: ${manifestPath}`);
  console.log(`Summary: ${results.filter(r => r.ok).length}/${TARGETS.length} OK, ${results.filter(r => r.ok).reduce((s, r) => s + (r.bytes || 0), 0)} bytes`);

  await browser.close();
})().catch(e => { console.error('FATAL:', e); process.exit(1); });
