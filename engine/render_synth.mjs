// usage: node render_synth.mjs <in.svg> <out.png> <height>
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const inSvg = process.argv[2] || 'synth_question.svg';
const outPng = process.argv[3] || 'synth_question.png';
const height = parseInt(process.argv[4] || '750', 10);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 1000, height } });
await page.goto('file://' + path.resolve(inSvg));
await page.waitForTimeout(300);
await page.screenshot({ path: outPng, clip: { x: 0, y: 0, width: 1000, height } });
await browser.close();
console.log(outPng, 'yazıldı');
