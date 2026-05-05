// Extract the ALJ Disposition Data table from the OHO Playwright JSON capture
// into a clean CSV. Source JSON contains rendered HTML of the SSA OHO page.
// Run: node scripts/extract-oho-alj-table.js
const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..');
const SRC = path.join(REPO, 'data/ssa/oho/03-alj-disposition.tables.json');
const OUT = path.join(REPO, 'data/ssa/oho/alj-disposition-by-judge-LATEST.csv');

const j = JSON.parse(fs.readFileSync(SRC, 'utf8'));
const tableHtml = j.tables[0] || '';

// Strip tags + decode entities + split into cell stream
const decode = s => s.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  .replace(/&nbsp;/g, ' ').replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
  .replace(/&quot;/g, '"').replace(/&apos;/g, "'");

// Split on <tr>, then within each row split on <td>/<th>
const rows = [];
const rowMatches = tableHtml.match(/<tr[^>]*>[\s\S]*?<\/tr>/gi) || [];
for (const tr of rowMatches) {
  const cells = (tr.match(/<t[dh][^>]*>[\s\S]*?<\/t[dh]>/gi) || [])
    .map(c => decode(c.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()));
  if (cells.length) rows.push(cells);
}

console.log(`Parsed ${rows.length} rows. Column counts seen:`,
  Array.from(new Set(rows.map(r => r.length))).sort((a, b) => a - b));

// Find the modal column count (the data rows)
const counts = {};
rows.forEach(r => { counts[r.length] = (counts[r.length] || 0) + 1; });
const modal = +Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
console.log(`Modal column count = ${modal} (${counts[modal]} rows)`);

// First row matching modal count = header; rest = data
const headerIdx = rows.findIndex(r => r.length === modal);
const header = rows[headerIdx];
const data = rows.filter((r, i) => i !== headerIdx && r.length === modal);

// Sniff for outer rows that aren't the data table (footer disclaimers etc.)
console.log('Header:', JSON.stringify(header));
console.log('Sample data rows:');
data.slice(0, 3).forEach(r => console.log('  ', JSON.stringify(r)));
console.log('  ...');
data.slice(-2).forEach(r => console.log('  ', JSON.stringify(r)));

// Write CSV
const csvEsc = v => /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
const csv = [header, ...data].map(r => r.map(csvEsc).join(',')).join('\n');
fs.writeFileSync(OUT, csv + '\n');

// Companion source ledger
fs.writeFileSync(OUT + '.source.txt',
  `Source URL: https://www.ssa.gov/appeals/DataSets/03_ALJ_Disposition_Data.html\n` +
  `Fetched: ${j.fetchedAt}\n` +
  `Extraction tool: scripts/extract-oho-alj-table.js (regex over rendered HTML)\n` +
  `Rows: ${data.length} ALJ rows + 1 header\n` +
  `Columns: ${header.length}\n` +
  `Header: ${header.join(' | ')}\n`
);

console.log(`\nOK  ${data.length} rows -> ${OUT}`);
console.log(`OK  ledger      -> ${OUT}.source.txt`);
