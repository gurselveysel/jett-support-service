// quick interactive smoke probe for v13 shell work (not part of check_v13)
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2] || 'jett_lesson_fonksiyon_v13.html';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));
await page.goto('file://' + path.resolve(file));
await page.waitForTimeout(2000);
const state = await page.evaluate(() => ({
  ready: window.__engineReady === true,
  mode: document.getElementById('stageFrame').className,
  contentAr: getComputedStyle(document.documentElement).getPropertyValue('--content-ar'),
  shadeHidden: document.getElementById('bootShade').classList.contains('hide'),
  timeLabel: document.getElementById('timeLabel').textContent,
  narrBtn: { state: document.getElementById('narrationToggleBtn').dataset.state,
             text: document.getElementById('narrationToggleBtn').textContent.trim().replace(/\s+/g, ' ') },
  fontUI: getComputedStyle(document.body).fontFamily.slice(0, 40),
  bodyBg: getComputedStyle(document.body).backgroundColor
}));
// theme flip
await page.click('#themeToggleBtn');
state.afterThemeClick = await page.evaluate(() => ({
  attr: document.documentElement.getAttribute('data-theme'),
  bodyBg: getComputedStyle(document.body).backgroundColor
}));
// keyboard: space should start playback (focus off the theme button first —
// Space on a focused button is native click by design)
await page.evaluate(() => document.activeElement && document.activeElement.blur());
await page.keyboard.press('Space');
await page.waitForTimeout(700);
state.playingAfterSpace = await page.$eval('#seek', el => parseFloat(el.value)) > 0;
await page.keyboard.press('Space');
// arrow seek
const before = await page.$eval('#seek', el => parseFloat(el.value));
await page.keyboard.press('ArrowRight');
state.arrowJump = (await page.$eval('#seek', el => parseFloat(el.value))) - before;
// manual mode override still works
await page.click('#mode169Btn');
state.manual169 = await page.$eval('#stageFrame', el => el.className);
console.log(JSON.stringify(state, null, 1));
console.log('errors:', errors.length, errors.slice(0, 3));
await browser.close();
process.exit(errors.length ? 1 : 0);
