import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2];
const filePath = 'file://' + path.resolve(file);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.goto(filePath);
await page.waitForFunction(() => window.__sceneBounds && window.__sceneBounds.length > 0);
const bounds = await page.evaluate(() => window.__sceneBounds);
bounds.forEach((b, i) => {
  console.log(`scene${i}: base=${(b.tEnd - b.tStart).toFixed(2)}s tStart=${b.tStart.toFixed(2)} tEnd=${b.tEnd.toFixed(2)}`);
});
await browser.close();
