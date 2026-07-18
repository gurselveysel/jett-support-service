// Layout screenshot artifacts for human review (NOT a pixel-baseline test —
// font rasterization varies by platform; layout invariants are asserted in
// check_v13.mjs instead).
//   node screens_v13.mjs <lesson.html> <outDir> [t]
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { mkdirSync } from 'node:fs';
import path from 'node:path';

const [lessonPath, outDir, tArg] = process.argv.slice(2);
if (!lessonPath || !outDir){
  console.error('usage: node screens_v13.mjs <lesson.html> <outDir> [t]');
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
const base = path.basename(lessonPath, '.html');

const WIDTHS = [320, 375, 414, 768, 1024, 1440, 1920];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

for (const theme of ['dark', 'light']){
  const ctx = await browser.newContext({ colorScheme: theme });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(lessonPath));
  await page.waitForFunction(() => window.__engineReady === true || document.getElementById('errorOverlay').classList.contains('show'));
  if (tArg){
    await page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, tArg);
  }
  for (const w of WIDTHS){
    const h = Math.round(w < 800 ? w * 2.16 : w * 0.62);
    await page.setViewportSize({ width: w, height: h });
    await page.waitForTimeout(80);
    await page.screenshot({ path: path.join(outDir, `${base}_${theme}_${w}.png`), fullPage: w < 800 });
  }
  await ctx.close();
}
await browser.close();
console.log(`OK — ${WIDTHS.length * 2} görüntü → ${outDir}`);
