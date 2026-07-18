// One-command lesson pipeline (v13):
//   node make_lesson.mjs <contract.json> <photo> <name> [--no-video] [--fast]
// Produces jett_lesson_<name>_v13.html (+ narration) and
// jett_video_<name>_v13.mp4, runs the full check suite, and prints an honest
// quality report (durations, per-scene narration fit, providers, sizes).
// The API key comes from the environment only — never stored anywhere.
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, statSync, readFileSync } from 'node:fs';
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';

const args = process.argv.slice(2);
const noVideo = args.includes('--no-video');
const fast = args.includes('--fast');
const [contractPath, photoPath, name] = args.filter(a => !a.startsWith('--'));
if (!contractPath || !photoPath || !name){
  console.error('usage: node make_lesson.mjs <contract.json> <photo> <name> [--no-video] [--fast]');
  process.exit(1);
}
const html = `jett_lesson_${name}_v13.html`;
const mp4 = `jett_video_${name}_v13.mp4`;
const run = (cmd, argv) => {
  const r = spawnSync(cmd, argv, { stdio: 'inherit' });
  if (r.status !== 0) { console.error(`ADIM BAŞARISIZ: ${cmd} ${argv.join(' ')}`); process.exit(r.status || 1); }
};

console.log('— 1/4 motor şablonu —');
if (!existsSync('jett_engine_v13_template.html')) run('node', ['build_engine.mjs']);
else console.log('şablon mevcut (yeniden üretmek için: node build_engine.mjs)');

console.log('— 2/4 ders üretimi (anlatım planı + gerçek ses ölçümü) —');
run('node', ['instantiate.mjs', contractPath, photoPath, html, '--audio']);

console.log('— 3/4 test paketi —');
const contract = JSON.parse(readFileSync(contractPath, 'utf8'));
const usesPanel = JSON.stringify(contract.scenes).includes('"panel"');
run('node', ['check_v13.mjs', html, usesPanel ? 'panel' : 'nopanel']);

if (!noVideo){
  console.log('— 4/4 video —');
  run('node', ['render_video.mjs', html, mp4, fast ? '24' : '30', fast ? '720' : '1080']);
} else console.log('— 4/4 video atlandı (--no-video) —');

/* ---- quality report ---- */
console.log('\n================ KALİTE RAPORU ================');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.goto('file://' + path.resolve(html));
await page.waitForFunction(() => window.__engineReady === true);
const q = await page.evaluate(() => {
  const b = window.__sceneBounds, DUR = parseFloat(document.getElementById('seek').max);
  const fits = b.map((s, i) => {
    const win = (b[i + 1] ? b[i + 1].tStart : DUR) - s.tStart;
    return { i, role: s.role, win, narr: s.narrDur || 0, ok: !s.narrDur || win + 0.05 >= s.narrDur + 0.3 };
  });
  return { DUR, scenes: b.length, glyphs: document.querySelectorAll('.glyph').length,
           persona: window.__penPersona && window.__penPersona.name,
           narrDriven: window.__narrDriven === true, fits,
           speechWins: (window.__audioMeta || []).filter(m => m.s0 !== null).length };
});
await browser.close();
console.log(`ders: ${html} (${(statSync(html).size / 1024).toFixed(0)} KB)`);
console.log(`süre: ${q.DUR}s · ${q.scenes} sahne · ${q.glyphs} glif · kalem: ${q.persona} · anlatım-güdümlü: ${q.narrDriven}`);
console.log(`konuşma penceresi ölçülen sahne: ${q.speechWins}/${q.scenes}`);
const bad = q.fits.filter(f => !f.ok);
console.log(bad.length === 0
  ? 'anlatım sığdırma: TÜM sahneler OK (donma=0, taşma=0)'
  : `anlatım sığdırma: ${bad.length} sahne SIĞMIYOR → ${bad.map(f => 's' + f.i).join(',')}`);
if (!noVideo && existsSync(mp4)){
  const vdur = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4]).toString().trim();
  console.log(`video: ${mp4} (${(statSync(mp4).size / 1048576).toFixed(1)} MB, ${parseFloat(vdur).toFixed(1)}s)`);
}
console.log('===============================================');
process.exit(bad.length === 0 ? 0 : 1);
