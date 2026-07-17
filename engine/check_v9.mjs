import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2] || 'jett_lesson_kimya_v9_engine.html';
const filePath = 'file://' + path.resolve(file);
const errors = [];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

let pass = true;
const assert = (cond, label) => { console.log((cond ? 'PASS' : 'FAIL') + ' — ' + label); if (!cond) pass = false; };

for (const vp of [{w:320,h:568},{w:375,h:812},{w:1440,h:900}]) {
  const page = await browser.newPage({ viewport: { width: vp.w, height: vp.h } });
  page.on('console', msg => { if (msg.type() === 'error') errors.push(`[${vp.w}] ` + msg.text()); });
  page.on('pageerror', exc => errors.push(`[${vp.w}] ` + String(exc)));
  await page.goto(filePath);
  await page.waitForTimeout(1000);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  const mode = await page.$eval('#stageFrame', el => el.className.includes('mode-916') ? '916' : '169');
  assert(!overflow, `${vp.w}x${vp.h} yatay taşma yok`);
  assert(vp.w < 900 ? mode === '916' : mode === '169', `${vp.w}x${vp.h} otomatik mod (${mode})`);
  await page.close();
}

const page = await browser.newPage({ viewport: { width: 1200, height: 1700 } });
page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
page.on('pageerror', exc => errors.push(String(exc)));
await page.goto(filePath);
await page.waitForTimeout(1200);

assert(await page.evaluate(() => window.__engineReady === true), 'motor hazır (__engineReady)');
assert(!(await page.$eval('#errorOverlay', el => el.classList.contains('show'))), 'hata ekranı kapalı (SelfCheck PASS)');
const glyphs = await page.$$eval('.glyph', els => els.length);
assert(glyphs > 100, `glif sayısı > 100 (${glyphs})`);
const DUR = parseFloat(await page.$eval('#seek', el => el.max));
assert(DUR >= 20 && DUR <= 75, `süre bant içinde (${DUR}s)`);

// teacher gate + completion
await page.evaluate(() => { window.__completed = false; window.addEventListener('animation-complete', () => window.__completed = true); });
await page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, DUR - 0.5);
await page.click('#playBtn');
await page.waitForTimeout(1200);
assert(await page.evaluate(() => window.__completed), 'animation-complete tetiklendi');
await page.check('#teacherApprove');
await page.waitForTimeout(100);
assert(!(await page.$eval('#sendBtn', el => el.disabled)), 'öğretmen onayıyla Gönder aktif');

// ---- quantitative pen regression (visible-only, like v8's final metric) ----
const samples = [];
for (let t = 0; t <= DUR; t += 0.15) {
  await page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, t);
  const info = await page.evaluate(() => {
    const el = document.getElementById('penTip');
    const tr = el.getAttribute('transform');
    const m = tr ? tr.match(/translate\(([-\d.]+),([-\d.]+)\)/) : null;
    return { visible: el.classList.contains('on'), x: m ? parseFloat(m[1]) : null, y: m ? parseFloat(m[2]) : null };
  });
  samples.push({ t: Math.round(t*100)/100, ...info });
}
let prevVis = null, maxJump = 0;
const bigJumps = [];
for (const s of samples) {
  if (s.visible && s.x !== null) {
    if (prevVis) {
      const d = Math.hypot(s.x - prevVis.x, s.y - prevVis.y);
      maxJump = Math.max(maxJump, d);
      if (d > 300) bigJumps.push({ t: s.t, jump: Math.round(d) });
    }
    prevVis = s;
  } else prevVis = null;
}
console.log('büyük sıçramalar (>300u, kalem görünürken):', bigJumps.length, JSON.stringify(bigJumps));
assert(bigJumps.length <= 12, `sıçrama sayısı makul (${bigJumps.length} — hepsi uzay geçişi olmalı)`);

await browser.close();
console.log('TOTAL console errors:', errors.length);
errors.slice(0, 6).forEach(e => console.log(' -', e));
assert(errors.length === 0, 'konsol hatası yok');
console.log(pass ? '\n== ALL PASS ==' : '\n== FAILURES ==');
process.exit(pass ? 0 : 1);
