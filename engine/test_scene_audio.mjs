// usage: node test_scene_audio.mjs <contract.json> <sceneIndex> <outMp3Dir>
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { synthesizeCaptionMp3 } from './tts.mjs';

const [contractPath, sceneIdxStr, outDir] = process.argv.slice(2);
const sceneIdx = parseInt(sceneIdxStr, 10);
const contract = JSON.parse(readFileSync(contractPath, 'utf8'));
const scene = contract.scenes[sceneIdx];
const mp3Path = `${outDir}/${contractPath.replace(/.*contract_|_v10|\.json/g, '')}_scene${sceneIdx}_test.mp3`;

const provider = synthesizeCaptionMp3(scene.caption, mp3Path, {
  elevenText: scene.elevenText, stability: scene.stability, style: scene.style, speed: scene.speed
});
const dur = execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', mp3Path]).toString().trim();
console.log(`scene${sceneIdx}: provider=${provider} duration=${dur}s -> ${mp3Path}`);
