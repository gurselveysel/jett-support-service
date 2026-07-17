// Assembles the generic engine template: inlines opentype.js and the two
// Caveat WOFF subsets (opentype.js parses WOFF1 directly — verified) into
// jett_engine_v11_source.html, producing jett_engine_v11_template.html with
// only the two per-question slots (__CONTRACT_JSON__, __IMAGE_DATA_URI__) left open.
import { readFileSync, writeFileSync } from 'node:fs';

const OPENTYPE = '../build/node_modules/opentype.js/dist/opentype.min.js';
const FONT_LATIN = '../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-600-normal.woff';
const FONT_EXT   = '../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-ext-600-normal.woff';

let html = readFileSync('jett_engine_v11_source.html', 'utf8');

const put = (slot, content) => {
  if (!html.includes(slot)) throw new Error('slot not found: ' + slot);
  html = html.split(slot).join(content);
};

put('__OPENTYPE_JS__', readFileSync(OPENTYPE, 'utf8'));
put('__FONT_LATIN_B64__', readFileSync(FONT_LATIN).toString('base64'));
put('__FONT_EXT_B64__', readFileSync(FONT_EXT).toString('base64'));

writeFileSync('jett_engine_v11_template.html', html, 'utf8');
console.log('OK — jett_engine_v11_template.html,', (html.length / 1024).toFixed(0) + 'KB');
