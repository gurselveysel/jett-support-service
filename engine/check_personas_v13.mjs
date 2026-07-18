// Pen-persona end-to-end check: instantiates persona variants of a real
// contract into tmp lessons and proves (a) each persona measurably changes the
// ink physics in the produced file, (b) an unknown persona is a VISIBLE
// ContractGate error, never a silent fallback.
//   node check_personas_v13.mjs [contract] [image]
import { readFileSync, writeFileSync, rmSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;

const contractPath = process.argv[2] || 'contract_fonksiyon_v10.json';
const imagePath = process.argv[3] || 'fonksiyon_source.jpg';
const work = path.join(tmpdir(), 'jett_personas_' + process.pid);
mkdirSync(work, { recursive: true });

let pass = true;
const assert = (cond, label) => { console.log((cond ? 'PASS' : 'FAIL') + ' — ' + label); if (!cond) pass = false; };

const base = JSON.parse(readFileSync(contractPath, 'utf8'));
function makeLesson(style){
  const c = JSON.parse(JSON.stringify(base));
  if (style) c.meta.character = { ...(c.meta.character || { name: 'Test', pen_color: '#1E56C8' }), style };
  const cPath = path.join(work, `contract_${style || 'default'}.json`);
  const out = path.join(work, `lesson_${style || 'default'}.html`);
  writeFileSync(cPath, JSON.stringify(c));
  execFileSync('node', ['instantiate.mjs', cPath, imagePath, out], { stdio: 'pipe' });
  return out;
}

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
async function measure(file){
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(file));
  await page.waitForTimeout(1500);
  const m = await page.evaluate(() => {
    const err = document.getElementById('errorOverlay').classList.contains('show');
    if (err) return { err, msg: document.getElementById('errorMsg').textContent.slice(0, 120) };
    const bases = Array.from(document.querySelectorAll('.glyph')).slice(0, 30)
      .map(el => parseFloat(el.getAttribute('stroke-width')));
    return { err, persona: window.__penPersona, meanBase: bases.reduce((a, b) => a + b, 0) / bases.length };
  });
  await page.close();
  return m;
}

const def = await measure(makeLesson(null));
const kec = await measure(makeLesson('keceli'));
const tuk = await measure(makeLesson('tukenmez'));
assert(!def.err && !kec.err && !tuk.err, 'üç geçerli persona da hatasız boot ediyor');
assert(def.persona.name === 'varsayilan' && kec.persona.name === 'keceli' && tuk.persona.name === 'tukenmez',
  `persona çözümü doğru (${def.persona.name}/${kec.persona.name}/${tuk.persona.name})`);
const rKec = kec.meanBase / def.meanBase, rTuk = tuk.meanBase / def.meanBase;
assert(Math.abs(rKec - 1.35) < 0.06, `keçeli taban kalınlığı ×1.35 (ölçülen ×${rKec.toFixed(3)})`);
assert(Math.abs(rTuk - 0.85) < 0.06, `tükenmez taban kalınlığı ×0.85 (ölçülen ×${rTuk.toFixed(3)})`);
assert(kec.persona.floor === 0.8 && tuk.persona.floor === 0.7, 'persona basınç tabanları motorda etkin');

// unknown persona => visible gate error naming the field
const bad = await measure(makeLesson('gazoz'));
assert(bad.err === true, 'bilinmeyen persona: animasyon reddedildi (görünür hata)');
assert(/style bilinmiyor/.test(bad.msg || ''), `hata mesajı alanı adlandırıyor ("${(bad.msg || '').slice(0, 60)}…")`);

await browser.close();
rmSync(work, { recursive: true, force: true });
console.log(pass ? '\n== ALL PASS ==' : '\n== FAILURES ==');
process.exit(pass ? 0 : 1);
