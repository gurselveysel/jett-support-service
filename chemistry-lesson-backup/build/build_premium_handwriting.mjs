import { readFileSync, writeFileSync } from 'node:fs';
import wawoff2 from 'wawoff2';
import opentype from 'opentype.js';

async function loadFont(path) {
  const woff2 = readFileSync(path);
  const sfnt = await wawoff2.decompress(woff2);
  return opentype.parse(sfnt.slice().buffer);
}

const latinFont = await loadFont('../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-600-normal.woff2');
const extFont   = await loadFont('../fonttest/node_modules/@fontsource/caveat/files/caveat-latin-ext-600-normal.woff2');
const UPM = latinFont.unitsPerEm; // 1000, same for both subsets (same family/weight)

function fontForChar(ch) {
  const li = latinFont.charToGlyph(ch).index;
  if (li !== 0) return latinFont;
  const ei = extFont.charToGlyph(ch).index;
  if (ei !== 0) return extFont;
  return null; // not covered by either subset — must be tokenized specially (delta/super/sub)
}

// custom hand-authored "delta" glyph (script fonts don't ship Greek letters in these subsets).
// Defined directly in already-scaled SVG output space (baseline at oy, up = negative y), matching
// the convention opentype.js's glyph.getPath(x,y,fontSize) already produces.
function deltaPath(ox, oy, fs) {
  const p = (x, y) => `${(ox + x * fs).toFixed(2)},${(oy + y * fs).toFixed(2)}`;
  return `M ${p(0.34, -0.06)} C ${p(0.10, -0.10)} ${p(0.02, -0.24)} ${p(0.10, -0.34)} ` +
         `C ${p(0.18, -0.44)} ${p(0.36, -0.42)} ${p(0.34, -0.30)} ` +
         `C ${p(0.32, -0.20)} ${p(0.14, -0.18)} ${p(0.12, -0.28)} ` +
         `C ${p(0.10, -0.40)} ${p(0.26, -0.52)} ${p(0.40, -0.50)}`;
}
const DELTA_ADVANCE = 480; // font units, roughly one lowercase-letter width

// re-round an already-2-decimal path data string down to 1 decimal to shave file size
// (at this on-screen scale, 0.1 unit precision is visually indistinguishable from 0.01).
function roundPathData(d) {
  return d.replace(/-?\d+\.\d+/g, (m) => {
    const r = Math.round(parseFloat(m) * 10) / 10;
    return (Object.is(r, -0) ? 0 : r).toString();
  });
}

// Tokenize a source string into render tokens. Recognized specials:
//  'δ' -> custom delta glyph
//  '⁺' / '⁻' -> real '+'/'-' glyph, shrunk + raised (superscript)
//  '₂' / '₃' -> real '2'/'3' glyph, shrunk + lowered (subscript)
//  ' ' -> space (advance only, extra pause weight, no visible glyph)
//  anything else -> looked up directly in latin/ext subset
function tokenize(text) {
  const tokens = [];
  for (const ch of text) {
    if (ch === ' ') { tokens.push({ kind: 'space' }); continue; }
    if (ch === 'δ') { tokens.push({ kind: 'delta' }); continue; }
    if (ch === '⁺') { tokens.push({ kind: 'super', ch: '+' }); continue; }
    if (ch === '⁻') { tokens.push({ kind: 'super', ch: '-' }); continue; }
    if (ch === '₂') { tokens.push({ kind: 'sub', ch: '2' }); continue; }
    if (ch === '₃') { tokens.push({ kind: 'sub', ch: '3' }); continue; }
    const font = fontForChar(ch);
    if (!font) { console.warn('WARNING: glyph not covered by either subset, skipping:', JSON.stringify(ch)); continue; }
    tokens.push({ kind: 'char', ch, font });
  }
  return tokens;
}

// Build the list of glyphs (with path 'd' + advance in font units) for one line, starting at (x,y), fontSize.
// Applies real font kerning (Caveat ships a GPOS table) between consecutive plain-letter glyphs
// from the SAME subset font — tightening pairs like "V"+"o" exactly as the type designer intended,
// instead of the naive "just sum advance widths" spacing used previously.
function layoutLine(tokens, x, y, fontSize) {
  let cursor = x;
  const glyphs = [];
  let prevGlyph = null, prevFont = null;
  for (const tok of tokens) {
    // opentype.js's toPathData() has an edge-case bug that emits a literal "NaN" coordinate
    // when fed certain long floating-point-noise inputs (e.g. 79.69600000000001); rounding the
    // pen position to a clean precision before every getPath() call avoids triggering it.
    cursor = Math.round(cursor * 1000) / 1000;
    if (tok.kind === 'space') {
      const adv = 260 * (fontSize / UPM);
      cursor += adv;
      glyphs.push({ d: null, isSpace: true, isPunct: false, advancePx: adv });
      prevGlyph = null; prevFont = null;
      continue;
    }
    if (tok.kind === 'delta') {
      const d = deltaPath(cursor, y, fontSize);
      const adv = DELTA_ADVANCE * (fontSize / UPM);
      glyphs.push({ d, isSpace: false, isPunct: false, advancePx: adv });
      cursor += adv;
      prevGlyph = null; prevFont = null;
      continue;
    }
    if (tok.kind === 'super' || tok.kind === 'sub') {
      const g = latinFont.charToGlyph(tok.ch);
      const scale = 0.62;
      const subFs = fontSize * scale;
      const yOff = tok.kind === 'super' ? -fontSize * 0.34 : fontSize * 0.10;
      const path = g.getPath(cursor, y + yOff, subFs);
      const adv = g.advanceWidth * (subFs / UPM) * 1.05;
      glyphs.push({ d: roundPathData(path.toPathData(2)), isSpace: false, isPunct: false, advancePx: adv });
      cursor += adv;
      prevGlyph = null; prevFont = null;
      continue;
    }
    // plain character — apply real kerning against the previous plain glyph if it came from the same subset font
    const g = tok.font.charToGlyph(tok.ch);
    if (prevGlyph && prevFont === tok.font) {
      let kern = 0;
      try { kern = tok.font.getKerningValue(prevGlyph, g) || 0; } catch (e) { kern = 0; }
      cursor += kern * (fontSize / UPM);
      cursor = Math.round(cursor * 1000) / 1000;
    }
    const path = g.getPath(cursor, y, fontSize);
    const adv = g.advanceWidth * (fontSize / UPM);
    const isPunct = /[.,;:()]/.test(tok.ch);
    glyphs.push({ d: roundPathData(path.toPathData(2)), isSpace: false, isPunct, advancePx: adv });
    prevGlyph = g; prevFont = tok.font;
    cursor += adv;
  }
  return glyphs;
}

// Distribute [lineStart,lineEnd] across glyphs proportional to advance width, with extra
// pause weight after spaces/punctuation for a natural writing rhythm. Bakes absolute
// data-start/data-end onto each glyph (stroke pass mostly, then a short fill crossfade).
function timeGlyphs(glyphs, lineStart, lineEnd) {
  const weights = glyphs.map(g => g.advancePx + (g.isSpace ? 55 : 0) + (g.isPunct ? 30 : 0));
  const total = weights.reduce((a, b) => a + b, 0) || 1;
  const duration = lineEnd - lineStart;
  let acc = 0;
  return glyphs.map((g, i) => {
    const t0 = lineStart + (acc / total) * duration;
    acc += weights[i];
    const t1 = lineStart + (acc / total) * duration;
    const strokeEnd = t0 + (t1 - t0) * 0.72;
    return { ...g, start: t0, end: Math.max(t0 + 0.02, strokeEnd), fillStart: strokeEnd, fillEnd: t1 };
  });
}

function seedFromString(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function mulberry32(seed) {
  let a = seed;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function renderLineGroup(id, x, y, fontSize, text, lineStart, lineEnd) {
  const tokens = tokenize(text);
  const glyphsRaw = layoutLine(tokens, x, y, fontSize);
  const timed = timeGlyphs(glyphsRaw, lineStart, lineEnd);
  const rnd = mulberry32(seedFromString(id));
  const rot = ((rnd() - 0.5) * 2.2).toFixed(2);
  const baseW = Math.max(1.6, fontSize * 0.075);
  let inner = '';
  for (const g of timed) {
    if (g.isSpace || !g.d) continue;
    const w = (baseW * (0.85 + rnd() * 0.3)).toFixed(2);
    // ONE path per glyph does double duty: stroke-dasharray/dashoffset (data-start/data-end,
    // handled by the existing ann-draw reveal + pen tracking) traces the outline first, then
    // fill-opacity (data-fill-start/data-fill-end) ramps 0->1 so the ink "fills in" right after —
    // no second element / no duplicated 'd' string needed for that crossfade.
    inner += `<path class="ann-draw glyph" data-start="${g.start.toFixed(3)}" data-end="${g.end.toFixed(3)}" data-fill-start="${g.fillStart.toFixed(3)}" data-fill-end="${g.fillEnd.toFixed(3)}" d="${g.d}" fill="var(--pen)" fill-opacity="0" stroke="var(--pen)" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" opacity="0"></path>`;
  }
  return `<g id="${id}" class="hw-line" transform="rotate(${rot} ${x} ${y})">${inner}</g>`;
}

const LINES = [
  { id: 'hw-chain',    x: 812, y: 330, fs: 30, start: 27,   end: 28.3, text: 'Y >' },
  { id: 'hw-chain2',   x: 812, y: 368, fs: 30, start: 28,   end: 29.5, text: 'X > Z' },
  { id: 'panel-line-1', x: 34, y: 55,  fs: 34, start: 4,    end: 9,    text: "Hatırla: EN yüksek atom ortak elektron çiftini çeker => δ⁻ olur." },
  { id: 'panel-line-2', x: 34, y: 103, fs: 34, start: 11,   end: 16,   text: "XY₂: X δ⁺ (merkez), Y δ⁻ (uçlar) => Y, X'ten daha elektronegatif." },
  { id: 'panel-line-3', x: 34, y: 151, fs: 34, start: 18,   end: 23,   text: "ZX₂: Z δ⁺ (merkez), X δ⁻ (uçlar) => X, Z'den daha elektronegatif." },
  { id: 'panel-line-4', x: 34, y: 199, fs: 34, start: 23,   end: 27,   text: "Birleştir: Y > X ve X > Z => zincirleme sıralama kurulur." },
  { id: 'panel-line-5', x: 34, y: 255, fs: 34, start: 29.5, end: 34,   text: "Aynı periyotta EN artar, yarıçap azalır; EN'i en düşük Z'nin yarıçapı en büyük." },
  { id: 'panel-line-6', x: 34, y: 303, fs: 34, start: 34.8, end: 37,   text: "I doğru: EN(Z) en düşük => yarıçapı en büyük Z'dir." },
  { id: 'panel-line-7', x: 34, y: 351, fs: 34, start: 37.6, end: 39.5, text: "II doğru: sıralamada en üstte Y var => EN'i en yüksek Y'dir." },
  { id: 'panel-line-8', x: 34, y: 399, fs: 34, start: 40.1, end: 41.8, text: "III doğru: Y > Z => ZY₃'te ortak çifti Y çeker => δ⁻ = Y." },
  { id: 'panel-line-9', x: 34, y: 447, fs: 34, start: 43.6, end: 48.6, text: "Bağımsız kontrol: tersten okunursa Z < X < Y — çelişki yok, tutarlı." },
  { id: 'final-box-text', x: 54, y: 547, fs: 42, start: 50.6, end: 53.6, text: "Cevap: E) I, II ve III — madde değişiyor" },
];

let template = readFileSync('../jett_lesson_v8_template.html', 'utf8');
let totalGlyphs = 0;

for (const L of LINES) {
  const markup = renderLineGroup(L.id, L.x, L.y, L.fs, L.text, L.start, L.end);
  totalGlyphs += (markup.match(/class="ann-draw glyph"/g) || []).length;

  // match the existing <text id="L.id" ...>...</text> (single or double-quoted attrs, id anywhere)
  const idRe = new RegExp(`<text[^>]*\\bid="${L.id}"[^>]*>[\\s\\S]*?</text>`);
  if (L.id === 'final-box-text') {
    // this one has no id in v2 template (it's the plain <text> inside #finalBoxGroup) — match by content
    const literalRe = /<text x="54" y="547"[^>]*>[\s\S]*?<\/text>/;
    if (!literalRe.test(template)) throw new Error('final-box-text anchor not found in template');
    template = template.replace(literalRe, markup);
    continue;
  }
  if (L.id === 'hw-chain' || L.id === 'hw-chain2') {
    if (!idRe.test(template)) throw new Error(`anchor not found for ${L.id}`);
    template = template.replace(idRe, markup);
    continue;
  }
  // panel lines: v2 template has no id, just class="hw panel-line" with a unique data-start/data-end pair
  const panelRe = new RegExp(`<text class="hw panel-line" data-start="${L.start}" data-end="${L.end}"[^>]*>[\\s\\S]*?</text>`);
  if (!panelRe.test(template)) throw new Error(`anchor not found for ${L.id} (panel regex)`);
  template = template.replace(panelRe, markup);
}

writeFileSync('../jett_lesson_v8_glyphs.html', template, 'utf8');
console.log('OK — wrote jett_lesson_v8_glyphs.html, total glyph-stroke paths:', totalGlyphs);
