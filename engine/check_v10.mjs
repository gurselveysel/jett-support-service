// usage: node check_v10.mjs <lesson.html> <nopanel|panel>
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2];
const expectPanel = process.argv[3] === 'panel';
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
assert(await page.evaluate(() => document.getElementById('penTip') === null), 'kalem imleci grafiği YOK');
const glyphs = await page.$$eval('.glyph', els => els.length);
assert(glyphs > 80, `glif sayısı > 80 (${glyphs})`);
const DUR = parseFloat(await page.$eval('#seek', el => el.max));
assert(DUR >= 20 && DUR <= 75, `süre bant içinde (${DUR}s)`);

const panelUsed = await page.evaluate(() => window.__panelUsed);
assert(panelUsed === expectPanel, `panel kullanımı beklendiği gibi (${panelUsed})`);
if (!expectPanel) {
  const vb = await page.$eval('#masterSvg', el => el.getAttribute('viewBox'));
  const imgH = await page.$eval('#clipRect', el => parseFloat(el.getAttribute('height')));
  assert(parseFloat(vb.split(' ')[3]) === imgH, `viewBox = yalnız görsel yüksekliği (${vb})`);
}

// runtime-placed handwriting blocks must never overlap each other
const rects = await page.evaluate(() => window.__placedRects || []);
let overlaps = 0;
for (let i = 0; i < rects.length; i++)
  for (let j = i + 1; j < rects.length; j++){
    const a = rects[i], b = rects[j];
    if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) overlaps++;
  }
assert(overlaps === 0, `yerleştirilen bloklar çakışmıyor (${rects.length} blok)`);

await page.evaluate(() => { window.__completed = false; window.addEventListener('animation-complete', () => window.__completed = true); });
await page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, DUR - 0.5);
await page.click('#playBtn');
await page.waitForTimeout(1200);
assert(await page.evaluate(() => window.__completed), 'animation-complete tetiklendi');
await page.check('#teacherApprove');
await page.waitForTimeout(100);
assert(!(await page.$eval('#sendBtn', el => el.disabled)), 'öğretmen onayıyla Gönder aktif');

await browser.close();
console.log('TOTAL console errors:', errors.length);
errors.slice(0, 6).forEach(e => console.log(' -', e));
assert(errors.length === 0, 'konsol hatası yok');
console.log(pass ? '\n== ALL PASS ==' : '\n== FAILURES ==');
process.exit(pass ? 0 : 1);
