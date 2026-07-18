import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2];
const filePath = 'file://' + path.resolve(file);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.goto(filePath);
await page.waitForFunction(() => window.__sceneBounds && window.__sceneBounds.length > 0);
const r = await page.evaluate(() => {
  const b = window.__sceneBounds;
  const DUR = parseFloat(document.getElementById('seek').max);
  return { b, DUR, narrDriven: window.__narrDriven === true };
});
r.b.forEach((s, i) => {
  const win = (r.b[i + 1] ? r.b[i + 1].tStart : r.DUR) - s.tStart;
  const narr = s.narrDur || 0;
  console.log(`scene${i}${s.role ? ' [' + s.role + ']' : ''}: base=${(s.tEnd - s.tStart).toFixed(2)}s window=${win.toFixed(2)}s` +
    (narr ? ` narr=${narr.toFixed(2)}s fit=${win + 0.05 >= narr + 0.3 ? 'OK' : 'FAIL'}` : ''));
});
console.log(`DUR=${r.DUR}s narrDriven=${r.narrDriven}`);
await browser.close();
