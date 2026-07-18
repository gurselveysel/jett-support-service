// Unit checks for narration_plan.mjs — pure, no network/API.
//   node check_narration_plan.mjs
import { readFileSync } from 'node:fs';
import { planNarration, deriveRole, needsDiscourseMarker, estimateSpeechSeconds } from './narration_plan.mjs';

let pass = true;
const assert = (cond, label) => { console.log((cond ? 'PASS' : 'FAIL') + ' — ' + label); if (!cond) pass = false; };

const A = JSON.parse(readFileSync('contract_fonksiyon_v10.json', 'utf8'));
const B = JSON.parse(readFileSync('contract_kimya.json', 'utf8'));
const C = JSON.parse(readFileSync('contract_ucgen_v10.json', 'utf8'));

// strip explicit voice params so we test the DERIVED path (the product path
// for future contracts; today's contracts carry hand-tuned values that win)
const bare = (c) => ({ ...c, scenes: c.scenes.map(({ stability, style, speed, ...s }) => s) });
const pa = planNarration(bare(A)), pb = planNarration(bare(B)), pc = planNarration(bare(C));

// determinism: same input => identical plan
assert(JSON.stringify(pa) === JSON.stringify(planNarration(bare(A))), 'plan deterministik');

// roles resolve and openings/closings behave
assert(pa[0].role === 'giris' && pb[0].role === 'giris' && pc[0].role === 'giris', 'sahne 0 = giriş');
assert(pa.at(-1).role === 'sonuc' && pb.at(-1).role === 'sonuc' && pc.at(-1).role === 'sonuc', 'son sahne = sonuç');
assert(pb.some(s => s.role === 'kontrol') && pa.some(s => s.role === 'kontrol'), 'kontrol sahneleri yakalandı');

// THE core anti-template guarantee: same-role scenes in DIFFERENT lessons
// never share an identical (stability, style, speed) triple
const key = (s) => `${s.stability}|${s.style}|${s.speed}`;
let collisions = 0;
for (const [p1, p2] of [[pa, pb], [pa, pc], [pb, pc]])
  for (const s1 of p1) for (const s2 of p2)
    if (s1.role === s2.role && key(s1) === key(s2)) collisions++;
assert(collisions === 0, `farklı derslerde aynı-rollü sahne üçlüsü çakışmıyor (çakışma: ${collisions})`);

// jitter stays inside the declared band around the role base
const inBand = [...pa, ...pb, ...pc].every(s =>
  s.stability >= 0.25 && s.stability <= 0.5 && s.style >= 0.05 && s.style <= 0.25 && s.speed >= 0.88 && s.speed <= 1.08);
assert(inBand, 'tüm türetilmiş değerler bant içinde');

// explicit contract values always win
const withExplicit = { ...bare(A), scenes: bare(A).scenes.map((s, i) => i === 2 ? { ...s, stability: 0.42, style: 0.09, speed: 1.0 } : s) };
const pe = planNarration(withExplicit)[2];
assert(pe.stability === 0.42 && pe.style === 0.09 && pe.speed === 1.0, 'açık contract değerleri kazanıyor');

// contract-declared role wins over derivation, unknown role throws visibly
const withRole = { ...bare(A), scenes: bare(A).scenes.map((s, i) => i === 3 ? { ...s, role: 'kontrol' } : s) };
assert(planNarration(withRole)[3].role === 'kontrol' && planNarration(withRole)[3].roleSource === 'contract', 'contract role alanı kazanıyor');
let threw = false;
try { planNarration({ ...bare(A), scenes: [{ ...bare(A).scenes[0], role: 'gazoz' }] }); } catch(e){ threw = /bilinmiyor/.test(e.message); }
assert(threw, 'bilinmeyen role görünür hata fırlatıyor');

// cold-open detector: proven-defect cases from the listening review
assert(needsDiscourseMarker("[warmly] f küçük eşit g'de dört tam sayı var"), "soğuk açılış: 'f küçük eşit…' yakalanıyor");
assert(needsDiscourseMarker('B altmış, DAC on derece'), "soğuk açılış: 'B altmış…' yakalanıyor");
assert(!needsDiscourseMarker('[warmly] Bakalım... f küçük eşit'), 'zaten işaretçili metin ikinci kez işaretlenmiyor');
assert(!needsDiscourseMarker('Soruda XY molekülü işaretlenmiş'), 'normal açılış işaretlenmiyor');

// marker injection keeps audio tags at the front and flags itself
const cold = planNarration({ meta: { title: 'T' }, scenes: [{ caption: 'x', elevenText: '[warmly] f artan bir fonksiyon' }, { caption: 'x' }, { caption: 'son' }] })[0];
assert(cold.markerAdded && /^\[warmly\] \S+/.test(cold.elevenText) && !/\]\s*\[/.test(cold.elevenText),
  `işaretçi tag'den sonra eklendi ("${cold.elevenText.slice(0, 40)}…")`);

// duration estimator sane on a known measurement (fonksiyon scene1 ≈ 9.2s)
const est = estimateSpeechSeconds('f artan, g ise azalan bir fonksiyon. İki eğri birbirini yalnızca tek bir noktada keser... işte tam burada, x eşittir bir.');
assert(est > 7 && est < 13, `süre tahmini makul (${est.toFixed(1)}s ~ ölçülen 9.2s)`);

console.log(pass ? '\n== ALL PASS ==' : '\n== FAILURES ==');
process.exit(pass ? 0 : 1);
