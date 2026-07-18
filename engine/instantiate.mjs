// Instantiates a lesson from the generic engine template:
//   node instantiate.mjs <contract.json> <image.(jpg|png)> <out.html> [--audio]
// The ONLY per-question inputs are the contract JSON and the photo — every
// coordinate, duration and layout decision is derived at runtime by the engine.
// --audio additionally synthesizes each scene caption to an embedded MP3 track
// via tts.mjs (ElevenLabs when ELEVENLABS_API_KEY is set and reachable, else
// MBROLA/espeak locally). At runtime the engine still prefers the device's own
// Turkish speech voice; the embedded track is the fallback that guarantees
// narration on devices with no TTS voice at all.
import { readFileSync, writeFileSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { synthesizeCaptionMp3Timed } from './tts.mjs';
import { planNarration } from './narration_plan.mjs';
import { ENGINE_VERSION } from './build_engine.mjs';

const args = process.argv.slice(2);
const withAudio = args.includes('--audio');
const [contractPath, imagePath, outPath] = args.filter(a => a !== '--audio');
if (!contractPath || !imagePath || !outPath){
  console.error('usage: node instantiate.mjs <contract.json> <image> <out.html> [--audio]');
  process.exit(1);
}

const contract = JSON.parse(readFileSync(contractPath, 'utf8')); // fail fast on bad JSON
const mime = imagePath.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
const dataUri = `data:${mime};base64,` + readFileSync(imagePath).toString('base64');

let html = readFileSync(`jett_engine_${ENGINE_VERSION}_template.html`, 'utf8');
const put = (slot, content) => {
  if (!html.includes(slot)) throw new Error('slot not found: ' + slot);
  html = html.split(slot).join(content);
};

// v13 --audio: two-pass generation. (1) The narration planner resolves each
// scene's voice (role-based, lesson-seeded — explicit contract values win) and
// the speech is synthesized + MEASURED; (2) the measured duration is written
// back into the contract (scene._narrDur) so the engine's TimingEngine paces
// the ink WITH the voice — zero boundary freezes, zero audio spill. The plan's
// resolved values are also baked into the embedded contract so render_video
// and __sceneBounds speak with exactly the same voice.
if (withAudio){
  const plan = planNarration(contract);
  const providers = new Set();
  const tracks = [];
  const meta = [];
  contract.scenes.forEach((scene, i) => {
    const p = plan[i];
    if (p.elevenText) scene.elevenText = p.elevenText;
    scene.stability = p.stability; scene.style = p.style; scene.speed = p.speed;
    scene.role = p.role;
    if (p.markerAdded) console.log(`  sahne ${i} (${p.role}): soğuk açılışa söylem işaretçisi eklendi`);

    const mp3 = join(tmpdir(), `jett_narr_${process.pid}_${i}.mp3`);
    const r = synthesizeCaptionMp3Timed(scene.caption, mp3, {
      elevenText: scene.elevenText, stability: scene.stability, style: scene.style, speed: scene.speed
    });
    providers.add(r.provider);
    const dur = parseFloat(execFileSync('ffprobe',
      ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]).toString());
    scene._narrDur = Math.round(dur * 100) / 100;
    meta.push({ dur: scene._narrDur, s0: r.s0, s1: r.s1 });
    tracks.push('data:audio/mpeg;base64,' + readFileSync(mp3).toString('base64'));
    rmSync(mp3, { force: true });
  });
  put('/*__AUDIO_JSON__*/ null', JSON.stringify(tracks));
  put('/*__AUDIO_META_JSON__*/ null', JSON.stringify(meta));
  const rolesLine = plan.map(p => p.role + (p.roleSource === 'contract' ? '' : '*')).join(' ');
  console.log(`audio: ${tracks.length} sahne parçası gömüldü (ses: ${[...providers].join(', ')})`);
  console.log(`roller (*türetilmiş): ${rolesLine}`);
}

put('/*__CONTRACT_JSON__*/ null', JSON.stringify(contract));
put('__IMAGE_DATA_URI__', dataUri);

writeFileSync(outPath, html, 'utf8');
console.log('OK —', outPath + ',', (html.length / 1024).toFixed(0) + 'KB');
