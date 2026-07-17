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
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { synthesizeCaptionMp3 } from './tts.mjs';

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

let html = readFileSync('jett_engine_v12_template.html', 'utf8');
const put = (slot, content) => {
  if (!html.includes(slot)) throw new Error('slot not found: ' + slot);
  html = html.split(slot).join(content);
};
put('/*__CONTRACT_JSON__*/ null', JSON.stringify(contract));
put('__IMAGE_DATA_URI__', dataUri);

if (withAudio){
  const providers = new Set();
  const tracks = contract.scenes.map((scene, i) => {
    const mp3 = join(tmpdir(), `jett_narr_${process.pid}_${i}.mp3`);
    providers.add(synthesizeCaptionMp3(scene.caption, mp3, {
      elevenText: scene.elevenText, stability: scene.stability, style: scene.style, speed: scene.speed
    }));
    const b64 = readFileSync(mp3).toString('base64');
    rmSync(mp3, { force: true });
    return 'data:audio/mpeg;base64,' + b64;
  });
  put('/*__AUDIO_JSON__*/ null', JSON.stringify(tracks));
  console.log(`audio: ${tracks.length} sahne parçası gömüldü (ses: ${[...providers].join(', ')})`);
}

writeFileSync(outPath, html, 'utf8');
console.log('OK —', outPath + ',', (html.length / 1024).toFixed(0) + 'KB');
