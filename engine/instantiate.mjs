// Instantiates a lesson from the generic engine template:
//   node instantiate.mjs <contract.json> <image.(jpg|png)> <out.html>
// The ONLY per-question inputs are the contract JSON and the photo — every
// coordinate, duration and layout decision is derived at runtime by the engine.
import { readFileSync, writeFileSync } from 'node:fs';

const [contractPath, imagePath, outPath] = process.argv.slice(2);
if (!contractPath || !imagePath || !outPath){
  console.error('usage: node instantiate.mjs <contract.json> <image> <out.html>');
  process.exit(1);
}

const contract = JSON.parse(readFileSync(contractPath, 'utf8')); // fail fast on bad JSON
const mime = imagePath.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
const dataUri = `data:${mime};base64,` + readFileSync(imagePath).toString('base64');

let html = readFileSync('jett_engine_v10_template.html', 'utf8');
const put = (slot, content) => {
  if (!html.includes(slot)) throw new Error('slot not found: ' + slot);
  html = html.split(slot).join(content);
};
put('/*__CONTRACT_JSON__*/ null', JSON.stringify(contract));
put('__IMAGE_DATA_URI__', dataUri);

writeFileSync(outPath, html, 'utf8');
console.log('OK —', outPath + ',', (html.length / 1024).toFixed(0) + 'KB');
