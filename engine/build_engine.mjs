// Assembles the generic engine template: inlines opentype.js, the two Caveat
// WOFF subsets (opentype.js parses WOFF1 directly — verified) and the Inter UI
// font subsets into jett_engine_vN_source.html, producing
// jett_engine_vN_template.html with only the two per-question slots
// (__CONTRACT_JSON__, __IMAGE_DATA_URI__) left open.
//   node build_engine.mjs [version]   (default: ENGINE_VERSION below)
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export const ENGINE_VERSION = 'v13';

// importable without side effects (instantiate.mjs reads ENGINE_VERSION)
const isMain = import.meta.url === pathToFileURL(process.argv[1] || '').href;
if (isMain) build();

function build(){

const OPENTYPE = '../build/node_modules/opentype.js/dist/opentype.min.js';
const FONT_LATIN = '../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-600-normal.woff';
const FONT_EXT   = '../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-ext-600-normal.woff';
// UI typography (v13+): Inter latin-ext covers Turkish; woff2 for size.
const UI_FONTS = {
  __UI_FONT_400_B64__: '../fonttest/node_modules/@fontsource/inter/files/inter-latin-ext-400-normal.woff2',
  __UI_FONT_600_B64__: '../fonttest/node_modules/@fontsource/inter/files/inter-latin-ext-600-normal.woff2'
};

const ver = process.argv[2] || ENGINE_VERSION;
const srcFile = `jett_engine_${ver}_source.html`;
const outFile = `jett_engine_${ver}_template.html`;

let html = readFileSync(srcFile, 'utf8');

const put = (slot, content) => {
  if (!html.includes(slot)) throw new Error('slot not found: ' + slot);
  html = html.split(slot).join(content);
};

put('__OPENTYPE_JS__', readFileSync(OPENTYPE, 'utf8'));
put('__FONT_LATIN_B64__', readFileSync(FONT_LATIN).toString('base64'));
put('__FONT_EXT_B64__', readFileSync(FONT_EXT).toString('base64'));
// UI font slots exist from v13 on; older sources build fine without them
for (const [slot, file] of Object.entries(UI_FONTS)){
  if (html.includes(slot)){
    if (!existsSync(file)) throw new Error(`UI font missing: ${file} — run: (cd ../fonttest && npm i @fontsource/inter)`);
    put(slot, readFileSync(file).toString('base64'));
  }
}

writeFileSync(outFile, html, 'utf8');
console.log(`OK — ${outFile},`, (html.length / 1024).toFixed(0) + 'KB');
}
