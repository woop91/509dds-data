// Build (a) hearing-office-to-state lookup and (b) per-state ALJ allowance
// summary from the OHO ALJ disposition CSV.
//
// Run: node scripts/build-oho-state-aggregates.js
//
// Source mapping is curated based on SSA OHO's hearing-office locations as of
// 2026-05. Office names with explicit two-letter state codes (e.g., "AKRON OH")
// are honored verbatim; ambiguous city names use the office's actual SSA OHO
// site location. NHC = National Hearing Center (handles cases nationwide via
// video; mapped to "NHC" not a state). SPECIAL REVIEW CADRE has no geographic
// home (all-virtual workgroup; mapped to "SPECIAL").
const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..');
const ALJ_CSV = path.join(REPO, 'data/ssa/oho/alj-disposition-by-judge-LATEST.csv');
const LOOKUP_OUT = path.join(REPO, 'data/ssa/oho/hearing-office-to-state.csv');
const STATE_AGG_OUT = path.join(REPO, 'data/ssa/oho/per-state-alj-allowance-LATEST.json');

// Office → state mapping (167 offices as of May 2026 OHO ALJ data)
const OFFICE_TO_STATE = {
  'AKRON OH': 'OH', 'ALBANY': 'NY', 'ALBUQUERQUE': 'NM', 'ALEXANDRIA': 'VA',
  'ATLANTA DOWNTOWN': 'GA', 'ATLANTA NORTH': 'GA', 'BALTIMORE': 'MD',
  'BILLINGS': 'MT', 'BIRMINGHAM': 'AL', 'BOSTON': 'MA', 'BRONX': 'NY',
  'BUFFALO': 'NY', 'CHARLESTON SC': 'SC', 'CHARLESTON WV': 'WV',
  'CHARLOTTE': 'NC', 'CHARLOTTESVILLE': 'VA', 'CHATTANOOGA': 'TN',
  'CHICAGO': 'IL', 'CINCINNATI': 'OH', 'CLEVELAND': 'OH',
  'COLORADO SPRINGS': 'CO', 'COLUMBIA MO': 'MO', 'COLUMBIA SC': 'SC',
  'COLUMBUS': 'OH', 'COVINGTON GA': 'GA', 'DALLAS DOWNTOWN': 'TX',
  'DALLAS NORTH OHO': 'TX', 'DAYTON': 'OH', 'DENVER': 'CO', 'DES MOINES': 'IA',
  'DETROIT': 'MI', 'DOVER': 'DE', 'ELKINS PARK': 'PA', 'EUGENE': 'OR',
  'EVANSTON': 'IL', 'EVANSVILLE': 'IN', 'FARGO': 'ND', 'FAYETTEVILLE NC': 'NC',
  'FLINT': 'MI', 'FLORENCE': 'SC', 'FORT MYERS FL': 'FL', 'FORT SMITH': 'AR',
  'FORT WAYNE': 'IN', 'FORT WORTH': 'TX', 'FRANKLIN TN': 'TN', 'FRESNO': 'CA',
  'FT LAUDERDALE': 'FL', 'GRAND RAPIDS': 'MI', 'GREENSBORO': 'NC',
  'GREENVILLE': 'SC', 'HARRISBURG': 'PA', 'HARTFORD': 'CT',
  'HATTIESBURG': 'MS', 'HONOLULU': 'HI', 'HOUSTON NORTH': 'TX',
  'HOUSTON WEST': 'TX', 'HUNTINGTON WV': 'WV', 'INDIANAPOLIS': 'IN',
  'JACKSON MS OHO': 'MS', 'JACKSONVILLE': 'FL', 'JERSEY CITY': 'NJ',
  'JOHNSTOWN': 'PA', 'KANSAS CITY': 'MO', 'KINGSPORT': 'TN', 'KNOXVILLE': 'TN',
  'LANSING': 'MI', 'LAS VEGAS': 'NV', 'LAWRENCE MA': 'MA', 'LEXINGTON': 'KY',
  'LITTLE ROCK': 'AR', 'LIVONIA MI': 'MI', 'LONG BEACH': 'CA',
  'LONG ISLAND': 'NY', 'LOS ANGELES DOWNTOWN': 'CA', 'LOS ANGELES WEST': 'CA',
  'LOUISVILLE': 'KY', 'MACON': 'GA', 'MADISON': 'WI', 'MANCHESTER': 'NH',
  'MCALESTER': 'OK', 'MEMPHIS': 'TN', 'METAIRIE': 'LA', 'MIAMI OHO': 'FL',
  'MIDDLESBORO': 'KY', 'MILWAUKEE': 'WI', 'MINNEAPOLIS': 'MN', 'MOBILE': 'AL',
  'MONTGOMERY': 'AL', 'MORENO VALLEY': 'CA', 'MORGANTOWN': 'WV',
  'MT PLEASANT MI': 'MI', 'NASHVILLE': 'TN', 'NEW HAVEN': 'CT',
  'NEW ORLEANS': 'LA', 'NEW YORK': 'NY', 'NEW YORK VARICK': 'NY',
  'NEWARK': 'NJ', 'NHC ALBUQUERQUE': 'NHC', 'NHC BALTIMORE': 'NHC',
  'NHC CHICAGO': 'NHC', 'NHC FALLS CHURCH': 'NHC', 'NHC ST LOUIS': 'NHC',
  'NORFOLK': 'VA', 'NORWALK': 'CA', 'OAK BROOK': 'IL', 'OAK PARK': 'MI',
  'OAKLAND': 'CA', 'OKLAHOMA CITY': 'OK', 'OMAHA': 'NE', 'ORANGE': 'CA',
  'ORLAND PARK': 'IL', 'ORLANDO': 'FL', 'PADUCAH': 'KY', 'PASADENA': 'CA',
  'PEORIA': 'IL', 'PHILADELPHIA': 'PA', 'PHILADELPHIA EAST': 'PA',
  'PHOENIX DOWNTOWN': 'AZ', 'PHOENIX NORTH': 'AZ', 'PITTSBURGH': 'PA',
  'PONCE': 'PR', 'PORTLAND ME': 'ME', 'PORTLAND OR': 'OR', 'PROVIDENCE': 'RI',
  'QUEENS': 'NY', 'RALEIGH': 'NC', 'RENO': 'NV', 'RICHMOND': 'VA',
  'RIO GRANDE VALLEY TX': 'TX', 'ROANOKE': 'VA', 'ROCHESTER': 'NY',
  'SACRAMENTO': 'CA', 'SALT LAKE CITY': 'UT', 'SAN ANTONIO': 'TX',
  'SAN BERNARDINO': 'CA', 'SAN DIEGO': 'CA', 'SAN FRANCISCO': 'CA',
  'SAN JOSE': 'CA', 'SAN JUAN': 'PR', 'SAN RAFAEL': 'CA',
  'SANTA BARBARA': 'CA', 'SAVANNAH': 'GA', 'SEATTLE': 'WA',
  'SEVEN FIELDS': 'PA', 'SHREVEPORT': 'LA', 'SOUTH JERSEY': 'NJ',
  'SPECIAL REVIEW CADRE': 'SPECIAL', 'SPOKANE': 'WA', 'SPRINGFIELD MA': 'MA',
  'SPRINGFIELD MO': 'MO', 'ST LOUIS': 'MO', 'ST PETERSBURG FL OHO': 'FL',
  'STOCKTON': 'CA', 'SYRACUSE': 'NY', 'TACOMA': 'WA',
  'TALLAHASSEE FL OHO': 'FL', 'TAMPA OHO': 'FL', 'TOLEDO OH': 'OH',
  'TOPEKA KS': 'KS', 'TUCSON': 'AZ', 'TULSA OHO': 'OK', 'TUPELO': 'MS',
  'VALPARAISO IN': 'IN', 'WASHINGTON': 'DC', 'WHITE PLAINS': 'NY',
  'WICHITA': 'KS', 'WILKES BARRE': 'PA',
};

// ── (1) Write hearing-office-to-state lookup ──
const lookupRows = [['Office', 'State']];
for (const office of Object.keys(OFFICE_TO_STATE).sort()) {
  lookupRows.push([office, OFFICE_TO_STATE[office]]);
}
const csvEsc = v => /[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
fs.writeFileSync(LOOKUP_OUT, lookupRows.map(r => r.map(csvEsc).join(',')).join('\n') + '\n');
fs.writeFileSync(LOOKUP_OUT + '.source.txt',
  `Source: scripts/build-oho-state-aggregates.js (curated mapping)\n` +
  `Built: ${new Date().toISOString()}\n` +
  `Rows: ${Object.keys(OFFICE_TO_STATE).length} offices + 1 header\n` +
  `Notes: NHC = National Hearing Center (virtual, nationwide). ` +
  `SPECIAL = Special Review Cadre (virtual workgroup, no geographic home). ` +
  `Mapping reflects each OHO office's physical site location, not the ` +
  `claimant's state of residence (cases are routed by region, not strict state).\n`);
console.log(`OK  lookup       ${Object.keys(OFFICE_TO_STATE).length} rows -> ${LOOKUP_OUT}`);

// ── (2) Per-state ALJ allowance summary ──
const lines = fs.readFileSync(ALJ_CSV, 'utf8').split(/\r?\n/);
const header = lines[0].split(',');
const idx = {
  judge: header.indexOf('Judge'),
  office: header.indexOf('Office'),
  totalDispositions: header.indexOf('Total Dispositions'),
  decisions: header.indexOf('Decisions'),
  awards: header.indexOf('Awards'),
  denials: header.indexOf('Denials'),
  fullyFav: header.indexOf('Fully Favorable'),
  partiallyFav: header.indexOf('Partially Favorable'),
};

const parseRow = line => {
  const cols = []; let cur = '', inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') { inQ = !inQ; continue; }
    if (c === ',' && !inQ) { cols.push(cur); cur = ''; continue; }
    cur += c;
  }
  cols.push(cur);
  return cols;
};

const byState = {};      // state -> aggregate
const unmapped = new Set();
let aljRowCount = 0;

for (let i = 1; i < lines.length; i++) {
  if (!lines[i]) continue;
  const cols = parseRow(lines[i]);
  const office = cols[idx.office];
  const state = OFFICE_TO_STATE[office];
  aljRowCount++;
  if (!state) { unmapped.add(office); continue; }
  if (!byState[state]) {
    byState[state] = {
      state,
      alj_count: 0, total_dispositions: 0, decisions: 0,
      awards: 0, denials: 0, fully_favorable: 0, partially_favorable: 0,
    };
  }
  const s = byState[state];
  s.alj_count += 1;
  s.total_dispositions += +cols[idx.totalDispositions] || 0;
  s.decisions += +cols[idx.decisions] || 0;
  s.awards += +cols[idx.awards] || 0;
  s.denials += +cols[idx.denials] || 0;
  s.fully_favorable += +cols[idx.fullyFav] || 0;
  s.partially_favorable += +cols[idx.partiallyFav] || 0;
}

// Compute allowance rates
const stateRows = Object.values(byState).map(s => ({
  ...s,
  allowance_rate_pct: s.decisions > 0
    ? Math.round((s.awards / s.decisions) * 10000) / 100
    : null,
})).sort((a, b) => a.state.localeCompare(b.state));

const summary = {
  source: 'data/ssa/oho/alj-disposition-by-judge-LATEST.csv',
  joined_via: 'data/ssa/oho/hearing-office-to-state.csv',
  built_at: new Date().toISOString(),
  alj_rows_processed: aljRowCount,
  states_with_data: stateRows.length,
  unmapped_offices: [...unmapped].sort(),
  caveat: 'allowance_rate_pct = awards / decisions. Decisions excludes ' +
          'dismissals. ALJs hearing remotely show their primary office, so ' +
          'rates are office-state, not claimant-state. NHC (national ' +
          'hearing centers) and SPECIAL (review cadre) are tracked separately.',
  by_state: stateRows,
};

fs.writeFileSync(STATE_AGG_OUT, JSON.stringify(summary, null, 2));
console.log(`OK  per-state    ${stateRows.length} states -> ${STATE_AGG_OUT}`);
console.log(`    ALJ rows processed: ${aljRowCount}`);
console.log(`    Unmapped offices: ${unmapped.size}${unmapped.size ? ' (' + [...unmapped].join(', ') + ')' : ''}`);

// Spot-check: print MA + 5 most-active states
console.log('\nSpot check (MA + top-5 by ALJ count):');
const maState = stateRows.find(s => s.state === 'MA');
const top5 = [...stateRows].sort((a, b) => b.alj_count - a.alj_count).slice(0, 5);
const checkSet = new Set([maState, ...top5].filter(Boolean));
for (const s of [...checkSet].sort((a, b) => b.alj_count - a.alj_count)) {
  console.log(`  ${s.state}: ${s.alj_count} ALJs, ${s.decisions} decisions, ${s.allowance_rate_pct}% allowance`);
}
