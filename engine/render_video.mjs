// Lesson HTML → MP4: deterministic frame capture + narration audio mux.
//   node render_video.mjs <lesson.html> <out.mp4> [fps]
// Frames come from the engine's own render(t) via seek (pure function of t),
// so the video is pixel-identical to live playback. The video clock follows
// the same narration-hold rule as the live player: the timeline waits at a
// scene boundary until that scene's narration finishes. Narration audio is
// synthesized with the same tts.mjs provider chain used by instantiate.mjs
// --audio, so HTML and MP4 speak with the same voice.
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { tmpdir } from 'node:os';
import { synthesizeCaptionMp3 } from './tts.mjs';

const [lessonPath, outPath, fpsArg] = process.argv.slice(2);
if (!lessonPath || !outPath){
  console.error('usage: node render_video.mjs <lesson.html> <out.mp4> [fps]');
  process.exit(1);
}
const FPS = parseInt(fpsArg || '24', 10);
const work = path.join(tmpdir(), 'jett_video_' + process.pid);
mkdirSync(path.join(work, 'frames'), { recursive: true });

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext();
await ctx.addInitScript(() => { delete window.speechSynthesis; delete window.SpeechSynthesisUtterance; });
const page = await ctx.newPage();
await page.setViewportSize({ width: 1720, height: 1200 }); // stage-max 1040px => crisp frames
await page.goto('file://' + path.resolve(lessonPath));
await page.waitForTimeout(1500);
await page.click('#mode169Btn'); // deterministic 16:9 stage regardless of viewport heuristics

const DURATION = parseFloat(await page.$eval('#seek', el => el.max));
const scenes = await page.evaluate(() => window.__sceneBounds);

// 1) narration audio per scene (same chain as the embedded tracks)
const audio = [];
for (let i = 0; i < scenes.length; i++){
  const mp3 = path.join(work, `scene_${i}.mp3`);
  const provider = synthesizeCaptionMp3(scenes[i].caption, mp3, {
    elevenText: scenes[i].elevenText, stability: scenes[i].stability, style: scenes[i].style, speed: scenes[i].speed
  });
  const dur = parseFloat(execFileSync('ffprobe',
    ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]).toString());
  audio.push({ mp3, dur });
  if (i === 0) console.log('ses sağlayıcısı:', provider);
}

// 2) hold-aware clock walk: videoT advances uniformly; lessonT freezes at a
//    scene boundary while that scene's narration is still speaking (capped
//    like the live player: max 6s extra per scene)
const dt = 1 / FPS;
const frames = []; // {lessonT, sceneIdx, karaokeIdx, speaking}
let lessonT = 0, videoT = 0;
let sceneIdx = -1, audioStartT = 0;
const HOLD_CAP = 6;
let holdStarted = -1;
while (true){
  const active = scenes.reduce((acc, s, i) => (lessonT >= s.tStart - 0.0005 ? i : acc), 0);
  if (active !== sceneIdx){ sceneIdx = active; audioStartT = videoT; holdStarted = -1; }
  const aEnd = audioStartT + audio[sceneIdx].dur + 0.15;
  const speaking = videoT >= audioStartT && videoT < aEnd - 0.15;
  const kIdx = speaking
    ? Math.floor((videoT - audioStartT) / Math.max(0.001, audio[sceneIdx].dur) * scenes[sceneIdx].caption.split(/\s+/).filter(Boolean).length)
    : -1;
  frames.push({ lessonT, kIdx, speaking });

  // advance
  videoT += dt;
  let nextT = lessonT + dt;
  const boundary = (sceneIdx + 1 < scenes.length ? scenes[sceneIdx + 1].tStart : DURATION) - 0.001;
  if (nextT > boundary && videoT < aEnd){
    if (holdStarted < 0) holdStarted = videoT;
    if (videoT - holdStarted < HOLD_CAP) nextT = boundary; // hold: sentence finishes first
  }
  lessonT = Math.min(nextT, DURATION);
  if (lessonT >= DURATION - 0.0005 && videoT >= audioStartT + audio[sceneIdx].dur + 0.6) break;
  if (videoT > DURATION + audio.reduce((a, b) => a + b.dur, 0) + 30) break; // hard safety stop
}
// record where each scene's audio starts on the video clock (for the mix)
const audioStarts = [];
{
  let si = -1;
  frames.forEach((f, k) => {
    const active = scenes.reduce((acc, s, i) => (f.lessonT >= s.tStart - 0.0005 ? i : acc), 0);
    if (active !== si){ si = active; audioStarts[active] = k / FPS; }
  });
}
console.log(`kareler: ${frames.length} (${(frames.length / FPS).toFixed(1)}s @ ${FPS}fps), ders süresi ${DURATION}s`);

// 3) capture
const stage = await page.$('#stageFrame');
for (let k = 0; k < frames.length; k++){
  const f = frames[k];
  await page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, f.lessonT.toFixed(3));
  await page.evaluate(({ kIdx, speaking }) => {
    const spans = document.querySelectorAll('#captionText > span');
    spans.forEach((sp, i) => {
      sp.classList.toggle('speaking', i === kIdx);
      sp.classList.toggle('spoken', kIdx >= 0 && i < kIdx);
    });
    document.getElementById('speakIndicator').classList.toggle('show', speaking);
  }, f);
  await stage.screenshot({ path: path.join(work, 'frames', `f_${String(k).padStart(5, '0')}.png`) });
  if (k % 240 === 0) console.log(`  kare ${k}/${frames.length}`);
}
await browser.close();

// 4) mux: frames → h264, scene audios adelay'lenip mikslenir
const inputs = [];
const delayed = [];
audio.forEach((a, i) => {
  inputs.push('-i', a.mp3);
  const ms = Math.round((audioStarts[i] || 0) * 1000);
  delayed.push(`[${i + 1}:a]adelay=${ms}|${ms}[a${i}]`);
});
const filter = delayed.join(';') + ';' + audio.map((_, i) => `[a${i}]`).join('') +
  `amix=inputs=${audio.length}:normalize=0[mix]`;
execFileSync('ffmpeg', [
  '-y', '-loglevel', 'error',
  '-framerate', String(FPS), '-i', path.join(work, 'frames', 'f_%05d.png'),
  ...inputs,
  '-filter_complex', filter,
  '-map', '0:v', '-map', '[mix]',
  '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0c0f14,format=yuv420p',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
  '-c:a', 'aac', '-b:a', '96k',
  outPath
]);
rmSync(work, { recursive: true, force: true });
const size = execFileSync('du', ['-h', outPath]).toString().split('\t')[0];
console.log(`OK — ${outPath} (${size.trim()})`);
