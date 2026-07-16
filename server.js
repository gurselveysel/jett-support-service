import express from "express";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import axios from "axios";
import sharp from "sharp";
import { createClient } from "@supabase/supabase-js";
import ws from "ws";
import { randomUUID, createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// JETT ADAPTATION: required env list uses JETT_ prefix (was GOGO_INTERNAL_SECRET).
// N8N_INTERNAL_BASE_URL removed from required list: it was only used by the
// teacher web panel's action-forwarding route, which has been removed
// (WhatsApp-only decision, 2026-07-14).
const required = [
  "SUPABASE_URL",
  "SUPABASE_SERVICE_ROLE_KEY",
  "JETT_INTERNAL_SECRET",
  "WAHA_API_KEY"
];
for (const key of required) {
  if (!process.env[key]) {
    console.error(`Missing environment variable: ${key}`);
    process.exit(1);
  }
}

const PORT = Number(process.env.PORT || 8080);
// JETT ADAPTATION: isolated storage bucket, not shared with GOGO's gogo-private bucket.
const BUCKET = process.env.JETT_STORAGE_BUCKET || "jett-private";
const MAX_MEDIA_BYTES = Number(process.env.JETT_MAX_MEDIA_BYTES || 15 * 1024 * 1024);
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY,
  {
    auth: { persistSession: false, autoRefreshToken: false },
    realtime: { transport: ws }
  }
);

const registry = JSON.parse(
  fs.readFileSync(path.join(__dirname, "data", "character_registry.json"), "utf8")
);

const app = express();
app.set("trust proxy", 1);
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      formAction: ["'self'"],
      scriptSrc: ["'none'"],
      frameAncestors: ["'none'"]
    }
  },
  referrerPolicy: { policy: "no-referrer" }
}));
app.use(express.json({ limit: process.env.JETT_JSON_BODY_LIMIT || "25mb" }));
app.use(express.urlencoded({ extended: false, limit: "256kb" }));
app.use(rateLimit({ windowMs: 60_000, limit: 120 }));

// JETT ADAPTATION: header renamed X-GOGO-Internal-Secret -> X-Jett-Internal-Secret
// to match what the existing Teacher Router / Visual Solver Router n8n workflows
// already send ($env.JETT_INTERNAL_SECRET). This was a real bug in the original
// V2 package that would have caused every call to fail with 401.
function internalAuth(req, res, next) {
  const received = req.get("X-Jett-Internal-Secret") || "";
  if (received !== process.env.JETT_INTERNAL_SECRET) {
    return res.status(401).json({ ok: false, error: "unauthorized" });
  }
  next();
}

function safePathPart(value) {
  return String(value || "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 80);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeText(value) {
  return String(value || "")
    .toLocaleLowerCase("tr-TR")
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[^a-z0-9\s]/g, " ");
}

function normalizeSubject(subject) {
  const s = normalizeText(subject);
  const aliases = [
    ["matematik", "Matematik"],
    ["turkce", "Türkçe"],
    ["fen bilimleri", "Fen Bilimleri"],
    ["fen", "Fen Bilimleri"],
    ["sosyal bilgiler", "Sosyal Bilgiler"],
    ["inkilap", "T.C. İnkılap Tarihi ve Atatürkçülük"],
    ["ingilizce", "İngilizce"],
    ["din kulturu", "Din Kültürü ve Ahlak Bilgisi"],
    ["hayat bilgisi", "Hayat Bilgisi"],
    ["bilisim", "Bilişim Teknolojileri ve Yazılım"],
    ["gorsel sanatlar", "Görsel Sanatlar"],
    ["muzik", "Müzik"],
    ["beden", "Beden Eğitimi ve Spor"],
    ["turk dili ve edebiyati", "Türk Dili ve Edebiyatı"],
    ["edebiyat", "Türk Dili ve Edebiyatı"],
    ["fizik", "Fizik"],
    ["kimya", "Kimya"],
    ["biyoloji", "Biyoloji"],
    ["tarih", "Tarih"],
    ["cografya", "Coğrafya"],
    ["felsefe", "Felsefe"],
    ["almanca", "Almanca / İkinci Yabancı Dil"]
  ];
  for (const [needle, canonical] of aliases) {
    if (s.includes(needle)) return canonical;
  }
  return subject || "Matematik";
}

function selectStyle(subject, questionType) {
  const canonical = normalizeSubject(subject);
  const candidates = registry.characters.filter((c) => c.subject === canonical);
  const tokens = normalizeText(questionType).split(/\s+/).filter(Boolean);
  const scored = candidates.map((c) => {
    const haystack = normalizeText([
      c.identity, c.error_reflex, c.solution_order, c.overlay_rhythm,
      c.icon_repertoire, c.platform_adaptation
    ].join(" "));
    let score = 0;
    for (const t of tokens) if (t.length > 2 && haystack.includes(t)) score += 4;
    if (haystack.includes("grafik") && tokens.includes("grafik")) score += 10;
    if (haystack.includes("geometri") && tokens.some((t) => ["geometri", "sekil", "aci"].includes(t))) score += 10;
    if (haystack.includes("paragraf") && tokens.some((t) => ["paragraf", "metin", "ana"].includes(t))) score += 10;
    score += Math.max(0, 11 - c.branch_character_no) * 0.01;
    return { c, score };
  }).sort((a, b) => b.score - a.score);
  const chosen = scored[0]?.c || registry.characters[0];
  return {
    internal_character_id: chosen.character_id,
    style_profile: {
      main_color: chosen.main_color_hex_approx || "#2F6BFF",
      main_color_name: chosen.main_color,
      support_colors: chosen.support_colors,
      pen_tip: chosen.pen_tip,
      pressure: chosen.pressure,
      stability: chosen.stability,
      jitter: chosen.jitter,
      opacity: chosen.opacity,
      writing_rhythm: chosen.writing_rhythm,
      icon_repertoire: chosen.icon_repertoire,
      option_marking: chosen.option_marking,
      final_ritual: chosen.final_ritual
    }
  };
}

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

function decodeDataUrl(value) {
  const s = String(value || "");
  const m = s.match(/^data:([^;]+);base64,(.+)$/s);
  if (m) return { mime: m[1], buffer: Buffer.from(m[2], "base64") };
  return { mime: "image/png", buffer: Buffer.from(s, "base64") };
}

function selectCharacterV5(input = {}) {
  const subject = normalizeSubject(input.subject || input.academic_contract?.subject || "");
  const questionType = input.question_type || "";
  const contract = input.academic_contract || {};
  const canonical = input.canonical_solution || {};
  const candidates = registry.characters.filter((c) => c.subject === subject);
  const tokens = normalizeText([
    questionType, contract.topic, contract.unit, contract.primary_outcome?.text,
    ...(contract.process_components || []), ...(canonical.common_mistakes || [])
  ].filter(Boolean).join(" ")).split(/\s+/).filter((x) => x.length > 2);
  const scored = (candidates.length ? candidates : registry.characters).map((c) => {
    const haystack = normalizeText([
      c.identity,c.personality_energy,c.error_reflex,c.solution_order,c.overlay_rhythm,
      c.evidence,c.icon_repertoire,JSON.stringify(c.tymm_identity || {})
    ].join(" "));
    let score = 0;
    for (const t of tokens) if (haystack.includes(t)) score += 2;
    if ((contract.process_components || []).some((x) => normalizeText(x).includes("ispat")) && haystack.includes("kanit")) score += 12;
    if (questionType.toLowerCase().includes("grafik") && haystack.includes("grafik")) score += 10;
    score += (11 - Number(c.branch_character_no || 10)) * 0.01;
    return { c, score };
  }).sort((a,b) => b.score-a.score);
  const c = scored[0]?.c || registry.characters[0];
  return {
    character: c,
    style_profile: {
      main_color: c.main_color_hex_approx || "#2F6BFF",
      main_color_name: c.main_color,
      support_colors: c.support_colors,
      pen_tip: c.pen_tip, pressure: c.pressure, stability: c.stability,
      jitter: c.jitter, opacity: c.opacity, writing_rhythm: c.writing_rhythm,
      icon_repertoire: c.icon_repertoire, option_marking: c.option_marking,
      final_ritual: c.final_ritual
    }
  };
}

function buildVisualPrompt({ questionText, academicContract = {}, canonicalSolution = {}, character = {}, generationMode = "initial", renderMode = "preserve_source" }) {
  const steps = (canonicalSolution.steps || []).filter((x) => x.visualizable !== false).map((x) => `${x.step_no}. ${x.action} — ${x.reason} [Hedef bağı: ${x.outcome_alignment}]`).join("\n");
  const values = (academicContract.values || []).filter((x) => ["explicit","natural"].includes(x.relevance)).map((x) => `${x.name}: ${x.expected_action}`).join("; ");
  return `Ünlüler Ai öğretmen kontrollü görsel çözüm üretimi.\n\nDEĞİŞTİRİLEMEZ AKADEMİK KAYNAK:\nÖğrenme çıktısı: ${academicContract.primary_outcome?.code || ""} ${academicContract.primary_outcome?.text || ""}\nSüreç bileşenleri: ${(academicContract.process_components || []).join("; ")}\nBeklenen öğrenme kanıtı: ${(academicContract.learning_evidence_expected || []).join("; ")}\nHazırbulunuşluk: ${(academicContract.prerequisite_assumptions || []).join("; ")}\nKaçınılacak yöntemler: ${(academicContract.discouraged_solution_methods || []).join("; ")}\nİlgili değer-eylem: ${values || "Yok; yapay değer cümlesi ekleme."}\n\nCANONICAL ÇÖZÜM:\nYöntem: ${canonicalSolution.solution_method || ""}\n${steps}\nFinal cevap: ${canonicalSolution.final_answer?.display || canonicalSolution.final_answer?.value || ""}\n\nÖĞRETMEN PROFİLİ:\n${character.name || "Öğretmen"} - ${character.identity || ""}\nAnlatım sırası: ${character.solution_order || ""}\nGörsel ritim: ${character.overlay_rhythm || ""}\nKalem/renk: ${character.pen_tip || ""}; ${character.main_color || ""}; ${character.support_colors || ""}\nTYMM baskın profilleri: ${(character.tymm_identity?.dominant_profiles || []).join(", ")}\n\nÜRETİM MODU: ${generationMode}; KAYNAK MODU: ${renderMode}.\n\nKURALLAR:\n- Orijinal soru metnini, saxılarını, seçeneklerini, grafik ve şekillerini değiştirme.\n- Soruyu bağımsız yeniden çözme; yalnız canonical çözümü görselleştir.\n- Hedef öğrenme çıktısını ve süreç bileşenini görselde görünür kıl.\n- Minimum yeterli not kullan; mobil WhatsApp ekranında okunaklı ol.\n- Türkçe karakter, formül, sembol ve birimler kusursuz olsun.\n- Öğretmen eli doğallığı üret; okunaksızlık veya yapay kir yaratma.\n- Final cevap tek ve açık biçimde işaretlensin.\n- ${questionText ? `Soru bağlamı: ${questionText}` : ""}`;
}

async function renderSafePanelV2({ originalPath, canonicalSolution = {}, styleProfile = {} }) {
  const original = await downloadStorage(originalPath);
  const meta = await sharp(original).metadata();
  const width = meta.width || 1080, height = meta.height || 1350;
  const raw = (canonicalSolution.steps || []).slice(0,6).map((x) => `${x.action}${x.reason ? ` — ${x.reason}` : ""}`);
  const wrapped = raw.flatMap((line) => wrapText(line, Math.max(38, Math.floor(width/22))));
  const panelHeight = Math.max(320, 150 + wrapped.length*54 + 90);
  const mainColor = /^#[0-9a-f]{6}$/i.test(styleProfile.main_color || "") ? styleProfile.main_color : "#2F6BFF";
  const textElements = wrapped.map((line,index) => `<text x="64" y="${135+index*54}" font-family="Arial" font-size="34" fill="#1f2937">${xml(line)}</text>`).join("");
  const answer = canonicalSolution.final_answer?.display || canonicalSolution.final_answer?.value || "";
  const svg = Buffer.from(`<svg width="${width}" height="${panelHeight}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#fff"/><path d="M30 22 Q${Math.floor(width/2)} 12 ${width-30} 25" stroke="${mainColor}" stroke-width="8" fill="none"/><text x="64" y="78" font-family="Arial" font-size="40" font-weight="700" fill="${mainColor}">Müfredata Uygun Öğretmen Çözümü</text>${textElements}<text x="64" y="${panelHeight-55}" font-family="Arial" font-size="38" font-weight="700" fill="${mainColor}">Cevap: ${xml(answer)}</text></svg>`);
  return sharp({create:{width,height:height+panelHeight,channels:3,background:"#fff"}}).composite([{input:original,top:0,left:0},{input:svg,top:height,left:0}]).png({compressionLevel:9}).toBuffer();
}

async function generateOpenAIVisual({ signedUrl, prompt }) {
  if (!process.env.OPENAI_API_KEY) throw new Error("OPENAI_API_KEY missing");
  const response = await axios.post("https://api.openai.com/v1/responses", {
    model: process.env.OPENAI_VISUAL_MODEL || "gpt-5.6",
    input: [{ role: "user", content: [{ type: "input_text", text: prompt }, { type: "input_image", image_url: signedUrl }] }],
    tools: [{ type: "image_generation" }]
  }, { headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, "Content-Type": "application/json" }, timeout: Number(process.env.JETT_VISUAL_TIMEOUT_MS || 360000) });
  const call = (response.data?.output || []).find((x) => x.type === "image_generation_call" && x.result);
  if (!call) throw new Error("OpenAI image_generation_call missing");
  return { buffer: Buffer.from(call.result, "base64"), model: response.data?.model || process.env.OPENAI_VISUAL_MODEL || "gpt-5.6", responseId: response.data?.id || "" };
}

// NOTE: El-Yazisi-Stabil / external provider path kept intact (per user decision:
// "OpenAI + safe_panel now, El-Yazisi-Stabil later"). This function will simply
// never be reached until JETT_VISUAL_PROVIDER or the request's provider field is
// set to 'external'/'el-yazisi-stabil'/'nano-banana', and JETT_EXTERNAL_VISUAL_SOLVER_URL
// is configured. Source reference for the later integration:
// gurselveysel/El-Yazisi-Stabil@1bdd6840b6865c330e4c3d95b828bce4c47e5535
async function generateExternalVisual({ originalPath, prompt }) {
  if (!process.env.JETT_EXTERNAL_VISUAL_SOLVER_URL) throw new Error("External visual solver URL missing");
  const original = await downloadStorage(originalPath);
  const dataUrl = `data:image/jpeg;base64,${original.toString("base64")}`;
  const response = await axios.post(process.env.JETT_EXTERNAL_VISUAL_SOLVER_URL, {
    problem_text: prompt,
    images_base64: [dataUrl],
    is_step_by_step: true,
    solution_type: "handwritten"
  }, { headers: { "Content-Type": "application/json", ...(process.env.JETT_EXTERNAL_VISUAL_SOLVER_API_KEY ? { Authorization: `Bearer ${process.env.JETT_EXTERNAL_VISUAL_SOLVER_API_KEY}` } : {}) }, timeout: Number(process.env.JETT_VISUAL_TIMEOUT_MS || 360000) });
  const image = response.data?.handwritten_image || response.data?.image_base64 || response.data?.data;
  if (!image) throw new Error("External visual image missing");
  return { buffer: decodeDataUrl(image).buffer, model: response.data?.model || "external-handwritten", responseId: response.data?.session_id || "" };
}

async function createSignedUrl(storagePath, expiresIn = 900) {
  const { data, error } = await supabase.storage.from(BUCKET)
    .createSignedUrl(storagePath, expiresIn);
  if (error) throw error;
  return data.signedUrl;
}

async function downloadStorage(storagePath) {
  const { data, error } = await supabase.storage.from(BUCKET).download(storagePath);
  if (error) throw error;
  return Buffer.from(await data.arrayBuffer());
}

async function uploadStorage(storagePath, buffer, contentType) {
  const { error } = await supabase.storage.from(BUCKET).upload(storagePath, buffer, {
    contentType,
    upsert: true,
    cacheControl: "3600"
  });
  if (error) throw error;
}

function xml(value) {
  return escapeHtml(value).replaceAll("\n", " ");
}

function wrapText(text, maxChars = 58) {
  const words = String(text || "").trim().split(/\s+/);
  const lines = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines;
}

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "jett-live-teacher-support", version: "2.0.0-jett" });
});

app.post("/internal/select-style", internalAuth, (req, res) => {
  const { subject, question_type } = req.body || {};
  res.json(selectStyle(subject, question_type));
});

app.post("/internal/prepare-media", internalAuth, async (req, res, next) => {
  try {
    const { ticket_id, question_id, source_url, mimetype = "image/jpeg" } = req.body || {};
    const storageKey = ticket_id || question_id;
    if (!storageKey || !source_url) return res.status(400).json({ ok: false, error: "missing_fields" });

    const response = await axios.get(source_url, {
      responseType: "arraybuffer",
      timeout: 60_000,
      maxContentLength: MAX_MEDIA_BYTES,
      maxBodyLength: MAX_MEDIA_BYTES,
      headers: { "X-Api-Key": process.env.WAHA_API_KEY }
    });

    if (response.data.byteLength > MAX_MEDIA_BYTES) {
      return res.status(413).json({ ok: false, error: "media_too_large" });
    }

    const normalized = await sharp(Buffer.from(response.data))
      .rotate()
      .resize({ width: 2200, height: 3000, fit: "inside", withoutEnlargement: true })
      .jpeg({ quality: 92, mozjpeg: true })
      .toBuffer();

    const meta = await sharp(normalized).metadata();
    const prefix = ticket_id ? 'tickets' : 'questions';
    const storagePath = `${prefix}/${safePathPart(storageKey)}/original.jpg`;
    await uploadStorage(storagePath, normalized, "image/jpeg");
    const signedUrl = await createSignedUrl(storagePath, 1800);

    res.json({
      ok: true,
      has_image: true,
      original_path: storagePath,
      signed_url: signedUrl,
      width: meta.width,
      height: meta.height,
      mimetype: "image/jpeg",
      source_mimetype: mimetype
    });
  } catch (error) {
    next(error);
  }
});

app.post("/internal/sign-media", internalAuth, async (req, res, next) => {
  try {
    const storagePath = String(req.body?.path || "");
    const expiresIn = Math.min(Number(req.body?.expires_in || 900), 3600);
    if (!storagePath) return res.status(400).json({ ok: false, error: "path_required" });
    res.json({ ok: true, path: storagePath, signed_url: await createSignedUrl(storagePath, expiresIn) });
  } catch (error) {
    next(error);
  }
});

app.post("/internal/delete-media", internalAuth, async (req, res, next) => {
  try {
    const paths = [...new Set((Array.isArray(req.body?.paths) ? req.body.paths : [])
      .map((p) => String(p || "").trim())
      .filter((p) => p.startsWith("tickets/")))];
    if (!paths.length) return res.json({ ok: true, deleted: [] });
    const { data, error } = await supabase.storage.from(BUCKET).remove(paths);
    if (error) throw error;
    res.json({ ok: true, deleted: (data || []).map((x) => x.name || x) });
  } catch (error) {
    next(error);
  }
});

app.post("/internal/select-character-v5", internalAuth, (req, res) => {
  res.json({ ok: true, ...selectCharacterV5(req.body || {}) });
});

app.post("/internal/sign-pair", internalAuth, async (req, res, next) => {
  try {
    const expiresIn = Math.min(Number(req.body?.expires_in || 900), 3600);
    const sourcePath = String(req.body?.source_path || "");
    const generatedPath = String(req.body?.generated_path || "");
    res.json({ ok: true, source_signed_url: sourcePath ? await createSignedUrl(sourcePath, expiresIn) : "", generated_signed_url: generatedPath ? await createSignedUrl(generatedPath, expiresIn) : "" });
  } catch (error) { next(error); }
});

app.post("/internal/upload-base64", internalAuth, async (req, res, next) => {
  try {
    const { question_id, ticket_id, draft_id, data, asset_type = "generated", mimetype = "image/png" } = req.body || {};
    const key = ticket_id || question_id;
    if (!key || !data) return res.status(400).json({ ok:false,error:"missing_fields" });
    const decoded = decodeDataUrl(data);
    if (decoded.buffer.length > MAX_MEDIA_BYTES) return res.status(413).json({ok:false,error:"media_too_large"});
    const normalized = await sharp(decoded.buffer).png({compressionLevel:9}).toBuffer();
    const meta = await sharp(normalized).metadata();
    const prefix = ticket_id ? "tickets" : "questions";
    const storagePath = `${prefix}/${safePathPart(key)}/${safePathPart(asset_type)}-${safePathPart(draft_id || randomUUID())}.png`;
    await uploadStorage(storagePath, normalized, mimetype);
    res.json({ok:true,rendered_path:storagePath,signed_url:await createSignedUrl(storagePath,1800),width:meta.width,height:meta.height,mime_type:"image/png",sha256:sha256(normalized)});
  } catch(error) { next(error); }
});

app.post("/internal/generate-visual", internalAuth, async (req, res, next) => {
  const started = Date.now();
  try {
    const { question_id, ticket_id, draft_id, original_path, question_text = "", canonical_solution = {}, academic_contract = {}, character_profile = {}, generation_mode = "initial", render_mode = "preserve_source", prompt_version = "visual_prompt_v5@5.0.0" } = req.body || {};
    if (!(ticket_id || question_id) || !original_path) return res.status(400).json({ok:false,error:"missing_fields"});
    const selected = character_profile?.character_id ? { character: character_profile, style_profile: character_profile.style_profile || {} } : selectCharacterV5({subject:academic_contract.subject,academic_contract,canonical_solution});
    const character = selected.character || character_profile;
    const styleProfile = selected.style_profile || character_profile.style_profile || {};
    const prompt = buildVisualPrompt({questionText:question_text,academicContract:academic_contract,canonicalSolution:canonical_solution,character,generationMode:generation_mode,renderMode:render_mode});
    // JETT ADAPTATION: default provider chain is openai -> safe_panel fallback only.
    // 'external'/'el-yazisi-stabil'/'nano-banana' remain valid provider values for
    // later use once JETT_EXTERNAL_VISUAL_SOLVER_URL is configured (deferred by user decision).
    let provider = String(req.body?.provider || process.env.JETT_VISUAL_PROVIDER || "openai");
    let result, fallbackUsed = false, providerError = "";
    const signedUrl = await createSignedUrl(original_path, 1800);
    try {
      if (provider === "external" || provider === "el-yazisi-stabil" || provider === "nano-banana") result = await generateExternalVisual({originalPath:original_path,prompt});
      else if (provider === "safe_panel") result = {buffer:await renderSafePanelV2({originalPath:original_path,canonicalSolution:canonical_solution,styleProfile}),model:"safe-panel-v2",responseId:""};
      else result = await generateOpenAIVisual({signedUrl,prompt});
    } catch (error) {
      providerError = error.message;
      fallbackUsed = true;
      result = {buffer:await renderSafePanelV2({originalPath:original_path,canonicalSolution:canonical_solution,styleProfile}),model:"safe-panel-v2",responseId:""};
      provider = "safe_panel";
    }
    const meta = await sharp(result.buffer).metadata();
    const prefix = ticket_id ? "tickets" : "questions";
    const key = ticket_id || question_id;
    const storagePath = `${prefix}/${safePathPart(key)}/visual-${safePathPart(draft_id || randomUUID())}-${Date.now()}.png`;
    await uploadStorage(storagePath,result.buffer,"image/png");
    res.json({ok:true,provider,model:result.model,prompt_version,width:meta.width,height:meta.height,mime_type:"image/png",rendered_path:storagePath,signed_url:await createSignedUrl(storagePath,1800),sha256:sha256(result.buffer),latency_ms:Date.now()-started,fallback_used:fallbackUsed,provider_error:providerError,qa:{method:provider,teacher_review_required:true,original_source_path:original_path}});
  } catch(error) { next(error); }
});

app.post("/internal/render", internalAuth, async (req, res, next) => {
  try {
    const { ticket_id, draft_id, original_path, overlay_plan = {}, style_profile = {} } = req.body || {};
    if (!ticket_id || !draft_id || !original_path) {
      return res.status(400).json({ ok: false, error: "missing_fields" });
    }

    const original = await downloadStorage(original_path);
    const meta = await sharp(original).metadata();
    const width = meta.width || 1080;
    const height = meta.height || 1350;

    const rawLines = [
      ...(Array.isArray(overlay_plan.lines) ? overlay_plan.lines : []),
      overlay_plan.micro_note || ""
    ].filter(Boolean).slice(0, 6);

    const wrapped = rawLines.flatMap((line) => wrapText(line, Math.max(38, Math.floor(width / 22))));
    const panelHeight = Math.max(300, 150 + wrapped.length * 54 + 90);
    const mainColor = /^#[0-9a-f]{6}$/i.test(style_profile.main_color || "")
      ? style_profile.main_color
      : "#2F6BFF";
    const title = overlay_plan.title || "Öğretmen Kontrollü Çözüm";
    const answer = overlay_plan.final_answer || "";

    const textElements = wrapped.map((line, index) => {
      const y = 135 + index * 54 + (index % 2 === 0 ? 1 : -1);
      return `<text x="64" y="${y}" font-family="Arial, Helvetica, sans-serif" font-size="34" fill="#1f2937">${xml(line)}</text>`;
    }).join("");

    const answerY = panelHeight - 58;
    // JETT ADAPTATION: removed "UzemGO" watermark text (branding rule — no
    // GOGO/UzemGO name may appear in anything a student or teacher can see).
    const svg = Buffer.from(`
      <svg width="${width}" height="${panelHeight}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" rx="0" fill="#ffffff"/>
        <path d="M30 22 Q${Math.floor(width/2)} 12 ${width-30} 25" stroke="${mainColor}" stroke-width="8" fill="none" stroke-linecap="round"/>
        <text x="64" y="78" font-family="Arial, Helvetica, sans-serif" font-size="40" font-weight="700" fill="${mainColor}">${xml(title)}</text>
        ${textElements}
        <rect x="55" y="${answerY-42}" width="${Math.min(width-110, 520)}" height="64" rx="20" fill="${mainColor}" opacity="0.12"/>
        <text x="78" y="${answerY}" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="700" fill="${mainColor}">Cevap: ${xml(answer || "Öğretmen kontrolünde")}</text>
      </svg>
     
    `);

    const rendered = await sharp({
      create: {
        width,
        height: height + panelHeight,
        channels: 3,
        background: "#ffffff"
      }
    })
      .composite([
        { input: original, top: 0, left: 0 },
        { input: svg, top: height, left: 0 }
      ])
      .png({ compressionLevel: 9 })
      .toBuffer();

    const outputPath = `tickets/${safePathPart(ticket_id)}/draft-${safePathPart(draft_id)}-solution.png`;
    await uploadStorage(outputPath, rendered, "image/png");
    const signedUrl = await createSignedUrl(outputPath, 1800);

    res.json({
      ok: true,
      rendered_path: outputPath,
      signed_url: signedUrl,
      width,
      height: height + panelHeight,
      qa: {
        pass: true,
        original_pixels_preserved: true,
        method: "append-only-safe-panel",
        prompt_visible: false
      }
    });
  } catch (error) {
    next(error);
  }
});

// JETT ADAPTATION: teacher web panel routes (GET/POST /teacher/:ticketCode) and the
// panelPage() HTML renderer have been REMOVED. Decision (2026-07-14): teacher UX
// stays WhatsApp-only for now (CLAIM/LISTE/DETAY/ONAYLA/DUZENLE/REDDET via
// JETT Teacher Command Inbound -> Teacher Router -> Teacher Action Handler).
// The panel depended on a `gogo_panel_ticket` Supabase RPC that does not exist in
// jett_academic and was never built. If a rich visual-preview web panel is wanted
// later, re-add these routes plus a `jett_panel_ticket` RPC at that time.

app.use((error, _req, res, _next) => {
  console.error(error);
  res.status(500).json({
    ok: false,
    error: "internal_error",
    message: process.env.NODE_ENV === "production" ? undefined : error.message
  });
});

app.listen(PORT, () => {
  console.log(`Jett support service listening on :${PORT}`);
});
