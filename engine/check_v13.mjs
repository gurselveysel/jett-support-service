// usage: node check_v12.mjs <lesson.html> <nopanel|panel>
// All playback assertions run under a DETERMINISTIC speechSynthesis stub —
// the real headless engine is voiceless and nondeterministic.
import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import path from 'node:path';
const file = process.argv[2];
const expectPanel = process.argv[3] === 'panel';
const filePath = 'file://' + path.resolve(file);
const errors = [];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

let pass = true;
const assert = (cond, label) => { console.log((cond ? 'PASS' : 'FAIL') + ' — ' + label); if (!cond) pass = false; };

// deterministic speechSynthesis stub. opts:
//   voices: array of {lang, name, localService} | []
//   startDelay: ms until onstart (-1 = never fires)
//   endDelay: ms after onstart until onend (-1 = never fires)
//   boundary: emit word-boundary events every 120ms after onstart
const ttsStub = (opts) => `(() => {
  const O = ${JSON.stringify(opts)};
  window.__spoken = [];
  window.__speakCalls = [];
  let cur = null;
  const S = {
    speaking: false, pending: false, paused: false,
    getVoices: () => O.voices,
    resume(){}, pause(){},
    cancel(){ cur = null; S.speaking = false; S.pending = false; },
    addEventListener(){},
    speak(u){
      window.__speakCalls.push({ text: u.text, t: performance.now() });
      if (u.text) window.__spoken.push(u.text);
      if (!u.text) return; // unlock utterance: no lifecycle needed
      cur = u;
      if (O.startDelay < 0){ S.speaking = false; S.pending = false; return; }
      S.pending = true;
      setTimeout(() => {
        if (cur !== u) return;
        S.pending = false; S.speaking = true;
        u.onstart && u.onstart({ target: u });
        if (O.boundary && u.onboundary){
          let off = 0, d = 60;
          for (const part of u.text.split(/(\\s+)/)){
            if (part && !/^\\s+$/.test(part)){
              const ci = off;
              setTimeout(() => { if (cur === u && u.onboundary) u.onboundary({ name: 'word', charIndex: ci, target: u }); }, d);
              d += 120;
            }
            off += part.length;
          }
        }
        if (O.endDelay >= 0){
          setTimeout(() => {
            if (cur !== u) return;
            S.speaking = false; cur = null;
            u.onend && u.onend({ target: u });
          }, O.endDelay);
        }
      }, O.startDelay);
    }
  };
  Object.defineProperty(window, 'speechSynthesis', { value: S, configurable: true });
  window.SpeechSynthesisUtterance = function(text){ this.text = text || ''; };
})();`;

const TR_VOICE = [{ lang: 'tr-TR', name: 'Stub TR', localService: true, default: true, voiceURI: 'stub' }];

async function newStubPage(opts, viewport){
  const ctx = await browser.newContext();
  await ctx.addInitScript(ttsStub(opts));
  const page = await ctx.newPage();
  if (viewport) await page.setViewportSize(viewport);
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(filePath);
  await page.waitForTimeout(1200);
  return { ctx, page };
}
const seekTo = (page, t) => page.$eval('#seek', (el, v) => { el.value = v; el.dispatchEvent(new Event('input')); }, t);

/* ================= viewports (real engine irrelevant here) ================= */
for (const vp of [{w:320,h:568},{w:375,h:812},{w:1440,h:900}]) {
  const { ctx, page } = await newStubPage({ voices: TR_VOICE, startDelay: 50, endDelay: 800, boundary: false },
                                           { width: vp.w, height: vp.h });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  const mode = await page.$eval('#stageFrame', el => el.className.includes('mode-916') ? '916' : '169');
  assert(!overflow, `${vp.w}x${vp.h} yatay taşma yok`);
  assert(vp.w < 900 ? mode === '916' : mode === '169', `${vp.w}x${vp.h} otomatik mod (${mode})`);
  await ctx.close();
}

/* ================= main run: core engine + camera + rhythm + pooling ================= */
{
  const { ctx, page } = await newStubPage({ voices: TR_VOICE, startDelay: 50, endDelay: 1200, boundary: true },
                                           { width: 1200, height: 1700 });

  assert(await page.evaluate(() => window.__engineReady === true), 'motor hazır (__engineReady)');
  assert(!(await page.$eval('#errorOverlay', el => el.classList.contains('show'))), 'hata ekranı kapalı (SelfCheck PASS)');
  assert(await page.evaluate(() => document.getElementById('penTip') === null), 'kalem imleci grafiği YOK');
  const glyphs = await page.$$eval('.glyph', els => els.length);
  assert(glyphs > 80, `glif sayısı > 80 (${glyphs})`);
  const DUR = parseFloat(await page.$eval('#seek', el => el.max));
  assert(DUR >= 20 && DUR <= 75, `süre bant içinde (${DUR}s)`);

  const panelUsed = await page.evaluate(() => window.__panelUsed);
  assert(panelUsed === expectPanel, `panel kullanımı beklendiği gibi (${panelUsed})`);

  // ONE-HAND PROOF at DOM level — unchanged from v11: proves the schedule itself is untouched
  const seqViol = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.ann-draw')).map(el => ({
      s: parseFloat(el.dataset.start), e: parseFloat(el.dataset.end)
    })).sort((a, b) => a.s - b.s);
    let v = 0;
    for (let i = 0; i < els.length; i++)
      for (let j = i + 1; j < els.length; j++){
        if (els[j].s >= els[i].e - 0.004) break;
        v++;
      }
    return v;
  });
  assert(seqViol === 0, `tek-el değişmezi (ihlal: ${seqViol})`);

  const rects = await page.evaluate(() => window.__placedRects || []);
  let overlaps = 0;
  for (let i = 0; i < rects.length; i++)
    for (let j = i + 1; j < rects.length; j++){
      const a = rects[i], b = rects[j];
      if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) overlaps++;
    }
  assert(overlaps === 0, `yerleştirilen bloklar çakışmıyor (${rects.length} blok)`);

  // InkPhysics (v11 mirası)
  const inkMapsBuilt = await page.evaluate(() => window.__inkMapsBuilt || 0);
  assert(inkMapsBuilt > 0, `InkPhysics: eğrilik haritası üretildi (${inkMapsBuilt})`);

  /* ---------- camera ---------- */
  const camInfo = await page.evaluate((DUR) => {
    const totalH = parseFloat(document.getElementById('masterSvg').getAttribute('viewBox').split(' ')[3]);
    const A = 1000 / totalH;
    const bounds = window.__sceneBounds;
    const ts = [0, DUR].concat(bounds.map(b => (b.tStart + b.tEnd) / 2));
    const out = { totalH, A, samples: [], full0: null, fullEnd: null, anyZoom: false };
    for (const t of ts){
      const r = window.__cameraRectAt(t);
      out.samples.push({ t, ...r, aspect: r.w / r.h, zoom: 1000 / r.w });
      if (1000 / r.w > 1.05) out.anyZoom = true;
    }
    out.full0 = window.__cameraRectAt(0);
    out.fullEnd = window.__cameraRectAt(DUR);
    return out;
  }, DUR);
  assert(camInfo.samples.every(s => Math.abs(s.aspect - camInfo.A) < 1e-3), 'kamera: tüm örneklerde oran = tuval oranı');
  assert(camInfo.samples.every(s => s.x >= -0.01 && s.y >= -0.01 && s.x + s.w <= 1000.01 && s.y + s.h <= camInfo.totalH + 0.01), 'kamera: hep tuval içinde');
  assert(camInfo.samples.every(s => s.zoom <= 1.81), 'kamera: zoom ≤ ZMAX');
  assert(camInfo.full0.w === 1000 && camInfo.fullEnd.w === 1000, 'kamera: t=0 ve t=son tam görünüm');
  assert(camInfo.anyZoom, 'kamera: en az bir sahnede gerçekten yakınlaşıyor');

  // determinism: same t reached from different directions => identical viewBox
  await seekTo(page, 12); const vbA = await page.$eval('#masterSvg', el => el.getAttribute('viewBox'));
  await seekTo(page, DUR - 2); await seekTo(page, 12);
  const vbB = await page.$eval('#masterSvg', el => el.getAttribute('viewBox'));
  assert(vbA === vbB, `kamera determinizmi (aynı t → aynı viewBox)`);

  // paused => zero viewBox mutations over 500ms
  const mutations = await page.evaluate(async () => {
    const svg = document.getElementById('masterSvg');
    let n = 0;
    const mo = new MutationObserver(muts => { n += muts.filter(m => m.attributeName === 'viewBox').length; });
    mo.observe(svg, { attributes: true });
    await new Promise(r => setTimeout(r, 500));
    mo.disconnect();
    return n;
  });
  assert(mutations === 0, `duraklatılmışken viewBox mutasyonu yok (${mutations})`);

  // toggle off while paused mid-lesson => instant full view
  await page.click('#cameraToggleBtn');
  const vbOff = await page.$eval('#masterSvg', el => el.getAttribute('viewBox'));
  assert(parseFloat(vbOff.split(' ')[2]) === 1000, 'kamera kapatınca (duraklatıkken) anında tam görünüm');
  const camLabel = await page.$eval('#cameraToggleBtn', el => el.textContent.trim());
  assert(camLabel === 'Kamera: Kapalı', `kamera düğme etiketi (${camLabel})`);
  await page.click('#cameraToggleBtn'); // back on

  /* ---------- rhythm + pooling + style-write cache ---------- */
  const gts = await page.evaluate(() => window.__glyphTimingSample);
  const ratio = gts ? gts.wordInitialSlotPerAdv / gts.midWordSlotPerAdv : 0;
  assert(ratio >= 1.25 && ratio <= 1.5, `kelime ritmi oranı [1.25,1.5] içinde (${ratio.toFixed(3)})`);

  // resting widths uniform + deterministic across a seek round-trip
  await seekTo(page, DUR);
  const rest1 = await page.evaluate(() => Array.from(document.querySelectorAll('.glyph')).slice(0, 20)
    .map(el => ({ w: el.style.strokeWidth, base: parseFloat(el.getAttribute('stroke-width')) })));
  await seekTo(page, 0);
  await seekTo(page, DUR);
  const rest2 = await page.evaluate(() => Array.from(document.querySelectorAll('.glyph')).slice(0, 20)
    .map(el => el.style.strokeWidth));
  assert(rest1.every((r, i) => r.w === rest2[i]), 'dinlenme kalınlığı seek gidiş-dönüşte birebir aynı');
  assert(rest1.every(r => Math.abs(parseFloat(r.w) - 0.55 * r.base) < 0.02), 'dinlenme kalınlığı = 0.55×taban (pool(1)=1 kanıtı)');

  // pooling engaged during drawing, bounded
  await page.evaluate(() => { window.__poolSample.min = 1; window.__poolSample.max = 1; });
  for (let t = 2; t < Math.min(DUR, 26); t += 0.4) await seekTo(page, t);
  const pool = await page.evaluate(() => window.__poolSample);
  assert(pool.max > 1.0 && pool.max <= 1.19, `mürekkep yoğunlaşması devrede ve sınırlı (max ${pool.max.toFixed(3)})`);

  // style-write cache: re-render at the same t writes nothing
  await seekTo(page, 10);
  await seekTo(page, 10);
  const writesRepeat = await page.evaluate(() => window.__styleWrites);
  assert(writesRepeat === 0, `aynı t'de ikinci render 0 stil yazımı (${writesRepeat})`);

  /* ---------- karaoke captions ---------- */
  const midScene = await page.evaluate(() => window.__sceneBounds[1]);
  await seekTo(page, (midScene.tStart + midScene.tEnd) / 2);
  const capInfo = await page.evaluate(() => {
    const bar = document.getElementById('captionText');
    return { spanCount: bar.querySelectorAll('span').length, text: bar.textContent };
  });
  assert(capInfo.spanCount === midScene.caption.split(/\s+/).filter(Boolean).length,
    `karaoke: span sayısı = kelime sayısı (${capInfo.spanCount})`);
  assert(capInfo.text === midScene.caption, 'karaoke: birleşik metin caption ile birebir aynı');

  // node stability: no per-frame rewrite (same span element survives playback within a scene)
  const spanHandle = await page.evaluateHandle(() => document.getElementById('captionText').querySelector('span'));
  await page.click('#playBtn');
  await page.waitForTimeout(600);
  await page.click('#pauseBtn');
  assert(await spanHandle.evaluate(el => el.isConnected), 'karaoke: span düğümleri kare-başı yeniden yazılmıyor');

  // synthetic boundaries highlight words while playing
  await seekTo(page, 0.2);
  await page.click('#playBtn');
  await page.waitForTimeout(2500);
  const hl = await page.evaluate(() => {
    const bar = document.getElementById('captionBar');
    return { speaking: bar.querySelectorAll('span.speaking').length, spoken: bar.querySelectorAll('span.spoken').length };
  });
  await page.click('#pauseBtn');
  assert(hl.speaking + hl.spoken > 0, `karaoke: boundary vurgusu çalışıyor (speaking=${hl.speaking}, spoken=${hl.spoken})`);
  const hlAfterSeek = await page.evaluate(() => {
    const t = window.__sceneBounds[2].tStart + 0.2;
    const el = document.getElementById('seek');
    el.value = t; el.dispatchEvent(new Event('input'));
    const bar = document.getElementById('captionBar');
    return bar.querySelectorAll('span.speaking, span.spoken').length;
  });
  assert(hlAfterSeek === 0, 'karaoke: seek sonrası vurgular temiz');

  // caption toggle staleness regression
  await page.click('#captionToggleBtn'); // off
  await seekTo(page, (midScene.tStart + midScene.tEnd) / 2);
  await page.click('#captionToggleBtn'); // on
  const staleText = await page.$eval('#captionBar', el => el.textContent);
  assert(staleText === midScene.caption, 'karaoke: alt yazı kapat→sahne değiştir→aç güncel caption gösteriyor');

  /* ---------- animation-complete + teacher gate (stub altında) ---------- */
  await page.evaluate(() => { window.__completed = false; window.addEventListener('animation-complete', () => window.__completed = true); });
  await seekTo(page, DUR - 0.5);
  await page.click('#playBtn');
  await page.waitForTimeout(3500); // son sahne beklemesi + tamamlanma payı
  assert(await page.evaluate(() => window.__completed), 'animation-complete tetiklendi');
  await page.check('#teacherApprove');
  await page.waitForTimeout(100);
  assert(!(await page.$eval('#sendBtn', el => el.disabled)), 'öğretmen onayıyla Gönder aktif');

  await ctx.close();
}

/* ================= narration first-speak + gesture unlock (fresh page) ================= */
{
  const { ctx, page } = await newStubPage({ voices: TR_VOICE, startDelay: 50, endDelay: 1200, boundary: false },
                                           { width: 1200, height: 1700 });
  await page.click('#playBtn');
  await page.waitForTimeout(500);
  await page.click('#pauseBtn');
  await page.click('#playBtn');
  await page.waitForTimeout(300);
  await page.click('#pauseBtn');
  const speakState = await page.evaluate(() => ({
    spoken: window.__spoken.slice(),
    emptyCalls: window.__speakCalls.filter(c => c.text === '').length,
    scene0: window.__sceneBounds[0].caption
  }));
  assert(speakState.spoken.length > 0 && speakState.spoken[0] === speakState.scene0,
    `anlatım: ilk konuşulan metin = sahne 0 caption'ı`);
  assert(speakState.emptyCalls === 1, `jest kilidi: boş utterance iki Play'de tam 1 kez (${speakState.emptyCalls})`);
  // pause+resume within the same scene must NOT re-speak the caption
  assert(speakState.spoken.length === 1, `duraklat/devam aynı sahneyi yeniden okumuyor (${speakState.spoken.length})`);
  await ctx.close();
}

/* ================= narration hold behavior ================= */
{
  // long utterance (onend 3s after start) => playback must plateau at the scene boundary
  const { ctx, page } = await newStubPage({ voices: TR_VOICE, startDelay: 50, endDelay: 3000, boundary: false },
                                           { width: 1200, height: 1700 });
  const b = await page.evaluate(() => window.__sceneBounds[1].tStart);
  await seekTo(page, Math.max(0, b - 1.2)); // speak starts fresh 1.2s before the boundary
  await page.click('#playBtn');
  const samples = [];
  for (let i = 0; i < 24; i++){ await page.waitForTimeout(150); samples.push(await page.$eval('#seek', el => parseFloat(el.value))); }
  await page.click('#pauseBtn');
  const plateau = samples.filter(v => Math.abs(v - (b - 0.001)) < 0.06).length * 0.15;
  const advanced = samples[samples.length - 1] > b + 0.3;
  assert(plateau >= 0.9, `bekleme: sahne sınırında plato (${plateau.toFixed(2)}s)`);
  assert(advanced, 'bekleme: utterance bitince oynatma ilerliyor');
  const spokenDuringHold = await page.evaluate((cap) => window.__spoken.filter(s => s === cap).length,
    await page.evaluate(() => window.__sceneBounds[1].caption));
  assert(spokenDuringHold <= 1, 'bekleme: sahne B beklerken tekrar tekrar konuşulmadı');
  await ctx.close();
}
{
  // utterance that NEVER ends => the cap must release the hold
  const { ctx, page } = await newStubPage({ voices: TR_VOICE, startDelay: 50, endDelay: -1, boundary: false },
                                           { width: 1200, height: 1700 });
  const b = await page.evaluate(() => window.__sceneBounds[1].tStart);
  await seekTo(page, Math.max(0, b - 1.0));
  await page.click('#playBtn');
  let released = false, waited = 0;
  while (waited < 9000){
    await page.waitForTimeout(300); waited += 300;
    const v = await page.$eval('#seek', el => parseFloat(el.value));
    if (v > b + 0.3){ released = true; break; }
  }
  await page.click('#pauseBtn');
  assert(released, `bekleme tavanı: sonsuz utterance ${ (waited/1000).toFixed(1) }s içinde bırakıldı (≤ 6.5s + pay)`);
  // seek during hold clears state
  await seekTo(page, Math.max(0, b - 1.0));
  await page.click('#playBtn');
  await page.waitForTimeout(1300); // holding now
  await seekTo(page, 2);
  const holdState = await page.evaluate(() => window.__narration.holding);
  assert(holdState === false, 'bekleme: hold ortasında seek durumu temizliyor');
  await ctx.close();
}

/* ================= voiceless engine => honest status OR embedded-audio fallback ================= */
{
  const { ctx, page } = await newStubPage({ voices: [], startDelay: -1, endDelay: -1, boundary: false },
                                           { width: 1200, height: 1700 });
  assert(await page.evaluate(() => window.__engineReady === true), 'sessiz motorda motor yine hazır');
  const hasAudio = await page.evaluate(() => (window.__audioTracks || 0) > 0);
  await page.click('#playBtn');
  await page.waitForTimeout(5000);
  if (hasAudio){
    // with embedded tracks the correct behavior is: fall back to audio and SPEAK
    const spoke = await page.evaluate(() => window.__narration.speaking || window.__narration.state === 'on');
    const stubUnused = await page.evaluate(() => window.__spoken.length === 0);
    assert(spoke, 'sessiz motorda gömülü ses devreye girdi (anlatım hâlâ Açık)');
    assert(stubUnused, 'sessiz motorda speechSynthesis yolu kullanılmadı (gömülü ses tercih edildi)');
  } else {
    const label = await page.$eval('#narrationToggleBtn', el => el.textContent.trim());
    assert(label === 'Anlatım: Ses bulunamadı', `sessiz motor tespiti: düğme "${label}"`);
  }
  await page.click('#pauseBtn');
  // completion after a near-end play: immediate without audio; with embedded
  // audio the final caption legitimately holds ≤ cap (6s) before completing
  const DUR = parseFloat(await page.$eval('#seek', el => el.max));
  await page.evaluate(() => { window.__completed = false; window.addEventListener('animation-complete', () => window.__completed = true); });
  await seekTo(page, DUR - 0.5);
  await page.click('#playBtn');
  await page.waitForTimeout(hasAudio ? 8000 : 2000);
  assert(await page.evaluate(() => window.__completed),
    hasAudio ? 'sessiz motorda animation-complete (son sahne sesi + tavan payıyla)' : 'sessiz motorda animation-complete gecikmesiz');
  await ctx.close();
}

/* ================= no API at all => unsupported, disabled ================= */
{
  const ctx = await browser.newContext();
  await ctx.addInitScript(() => { delete window.speechSynthesis; delete window.SpeechSynthesisUtterance; });
  const page = await ctx.newPage();
  page.on('console', m => { if (m.type() === 'error') errors.push('[no-tts] ' + m.text()); });
  page.on('pageerror', e => errors.push('[no-tts] ' + String(e)));
  await page.goto(filePath);
  await page.waitForTimeout(1200);
  assert(await page.evaluate(() => window.__engineReady === true), 'API yokken motor yine hazır');
  const hasAudioNoApi = await page.evaluate(() => (window.__audioTracks || 0) > 0);
  const noApiLabel = await page.$eval('#narrationToggleBtn', el => el.textContent.trim());
  const noApiDisabled = await page.$eval('#narrationToggleBtn', el => el.disabled);
  if (hasAudioNoApi){
    // embedded audio keeps narration functional even without the Web Speech API
    assert(noApiLabel === 'Anlatım: Açık', `API yokken gömülü sesle düğme "Anlatım: Açık" (${noApiLabel})`);
    assert(!noApiDisabled, 'API yokken gömülü sesle düğme aktif');
  } else {
    assert(noApiLabel === 'Anlatım: Yok', `API yokken düğme "Anlatım: Yok" (${noApiLabel})`);
    assert(noApiDisabled, 'API yokken düğme devre dışı');
  }
  await ctx.close();
}

await browser.close();
console.log('TOTAL console errors:', errors.length);
errors.slice(0, 8).forEach(e => console.log(' -', e));
assert(errors.length === 0, 'konsol hatası yok');
console.log(pass ? '\n== ALL PASS ==' : '\n== FAILURES ==');
process.exit(pass ? 0 : 1);
