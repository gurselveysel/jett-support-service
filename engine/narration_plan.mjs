// Narration variation planner (v13) — pure & deterministic, shared by
// instantiate.mjs and render_video.mjs.
//
// WHY: the perceptual listening review (2026-07-18) proved the old workflow's
// biggest robotic tell — voice params were hand-copied by narrative POSITION,
// so every lesson's opening scene shipped the exact same [warmly]+0.42/0.1/1.0
// triple. This module derives per-scene voice settings from the scene's
// RHETORICAL ROLE plus a lesson-seeded, bounded jitter, so two lessons never
// share an identical triple, while explicit contract values always win.
//
// It also fixes the second proven defect (cold opens): a scene whose speech
// starts symbol/digit-dense gets a short role-appropriate discourse marker
// ("Bakalım...", "Şimdi...") — three ASR models failed to decode such a cold
// open in the review.
//
// No Date.now()/Math.random(): everything is seeded from lesson title+scene.

const ROLES = ["giris", "hatirlatma", "hesap", "karsilastirma", "kontrol", "sonuc"];

// role bases — centers of the band each role speaks in
const ROLE_BASE = {
  giris:         { stability: 0.40, style: 0.10, speed: 0.99, tag: "warmly"     },
  hatirlatma:    { stability: 0.36, style: 0.12, speed: 0.99, tag: "thoughtful" },
  hesap:         { stability: 0.33, style: 0.15, speed: 1.02, tag: null         },
  karsilastirma: { stability: 0.31, style: 0.17, speed: 1.00, tag: "curious"    },
  kontrol:       { stability: 0.36, style: 0.12, speed: 0.97, tag: "thoughtful" },
  sonuc:         { stability: 0.40, style: 0.14, speed: 0.93, tag: "confident"  }
};
// bounded jitter half-widths — small but guaranteed variation between lessons
const JITTER = { stability: 0.03, style: 0.03, speed: 0.03 };

const MARKERS = {
  giris:         ["Bakalım...", "Evet, bakalım...", "Şimdi bakalım..."],
  hatirlatma:    ["Şunu hatırlayalım...", "Küçük bir not..."],
  hesap:         ["Şimdi...", "Peki...", "Devam edelim..."],
  karsilastirma: ["Peki...", "Şimdi..."],
  kontrol:       ["Bir bakalım...", "Kontrol edelim..."],
  sonuc:         ["Evet...", "Sonuçta..."]
};

function fnv(str){
  let h = 2166136261;
  for (let i = 0; i < str.length; i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function mulberry32(seed){
  let a = seed;
  return function(){
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const round3 = (x) => Math.round(x * 1000) / 1000;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

export function deriveRole(scene, idx, count){
  if (scene.role){
    if (!ROLES.includes(scene.role))
      throw new Error(`scenes[${idx}].role bilinmiyor: "${scene.role}" (geçerli: ${ROLES.join(", ")})`);
    return { role: scene.role, source: "contract" };
  }
  const text = `${scene.caption || ""} ${scene.elevenText || ""}`.toLowerCase();
  let role;
  if (idx === 0) role = "giris";
  else if (idx === count - 1) role = "sonuc";
  else if (/kontrol|sağlama|tutarl|çelişki/.test(text)) role = "kontrol";
  else if (/hatırla|hatırlat/.test(text)) role = "hatirlatma";
  else if (/karşılaştır|birleştir|sırala|aynı mantık/.test(text)) role = "karsilastirma";
  else role = "hesap";
  return { role, source: "derived" };
}

// spoken-duration estimate for reporting/limits — calibrated on the 25 scenes
// measured in the 2026-07-18 review (10.9–14.9 chars/s => conservative 11.5)
export function estimateSpeechSeconds(text){
  const stripped = String(text || "").replace(/\[[^\]]+\]/g, "").replace(/\s+/g, " ").trim();
  return stripped.length / 11.5;
}

const NUMBER_WORDS = /^(sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin)\b/i;
const DISCOURSE_OPEN = /^(bakalım|şimdi|evet|peki|önce|hadi|sonuç|devam|küçük|bir de|şunu|soruda|kontrol)/i;

export function needsDiscourseMarker(spokenText){
  const s = String(spokenText || "").replace(/^\s*(\[[^\]]+\]\s*)+/, "").trim();
  if (!s || DISCOURSE_OPEN.test(s)) return false;
  const firstWord = (s.split(/[\s,]+/)[0] || "");
  // cold open: bare variable letter ("f küçük eşit..."), digit, or number word
  return /^[a-zçğıöşü]['’]?$/i.test(firstWord) || /^\d/.test(firstWord) || NUMBER_WORDS.test(firstWord);
}

// plan one lesson. contract: parsed contract JSON. Returns array (per scene):
// { role, roleSource, stability, style, speed, elevenText, markerAdded }
export function planNarration(contract){
  const scenes = contract.scenes || [];
  const title = (contract.meta && contract.meta.title) || "";
  return scenes.map((scene, i) => {
    const { role, source } = deriveRole(scene, i, scenes.length);
    const rnd = mulberry32(fnv(`${title}#${i}#${role}`));
    const base = ROLE_BASE[role];
    // explicit contract values ALWAYS win (backward compatible); derived
    // values get seeded, bounded jitter so no two lessons share a triple
    const stability = scene.stability !== undefined ? scene.stability
      : round3(clamp(base.stability + (rnd() - 0.5) * 2 * JITTER.stability, 0.25, 0.5));
    const style = scene.style !== undefined ? scene.style
      : round3(clamp(base.style + (rnd() - 0.5) * 2 * JITTER.style, 0.05, 0.25));
    const speed = scene.speed !== undefined ? scene.speed
      : round3(clamp(base.speed + (rnd() - 0.5) * 2 * JITTER.speed, 0.88, 1.08));

    let elevenText = scene.elevenText || null;
    let markerAdded = false;
    const spoken = elevenText || scene.caption || "";
    if (needsDiscourseMarker(spoken)){
      const list = MARKERS[role];
      const marker = list[Math.floor(rnd() * list.length) % list.length];
      const tags = (spoken.match(/^\s*(\[[^\]]+\]\s*)+/) || [""])[0];
      const rest = spoken.slice(tags.length);
      elevenText = `${tags}${marker} ${rest}`;
      markerAdded = true;
    } else if (!elevenText && base.tag && source === "derived" && scene.elevenText === undefined){
      // caption-only scene: at least carry the role's tag so the voice isn't flat
      elevenText = `[${base.tag}] ${scene.caption}`;
    }

    return { role, roleSource: source, stability, style, speed, elevenText, markerAdded };
  });
}
