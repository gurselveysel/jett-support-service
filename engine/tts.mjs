// Narration TTS provider chain — best available wins:
//   1. ElevenLabs (needs ELEVENLABS_API_KEY env + network egress to
//      api.elevenlabs.io; voice via ELEVEN_VOICE_ID, default a calm
//      pedagogical female preset; eleven_multilingual_v2 speaks Turkish)
//   2. espeak-ng + MBROLA mb-tr2 / mb-tr1 (human diphone voices — far more
//      natural than raw espeak; apt: mbrola mbrola-tr1 mbrola-tr2)
//   3. espeak-ng tr (formant synth — last resort, robotic)
// API keys are read from the environment ONLY — never stored in this repo.
import { execFileSync } from 'node:child_process';
import { statSync, rmSync, existsSync, writeFileSync } from 'node:fs';

const ELEVEN_DEFAULT_VOICE = 'EXAVITQu4vr4xnSDxMaL'; // "Sarah" — warm, calm narration
let elevenBroken = false;

// Caption → spoken Turkish. Written captions use math notation (≤, |AC|, m(B),
// XY₂ …) that every TTS reads badly; a teacher SAYS these differently than
// they are written. Applied to the spoken text only — captions stay as-is.
export function speechNormalizeTr(text){
  let s = text;
  s = s.replace(/\|([A-ZÇĞİÖŞÜ]{2,3})\|/g, '$1 uzunluğu');       // |AC| → AC uzunluğu
  s = s.replace(/m\(([^)]+)\)/g, '$1 açısı');                    // m(DAC) → DAC açısı
  s = s.replace(/(^|[\s(])I{3}($|[.,:;)\s'])/g, '$1üç$2');       // roman III
  s = s.replace(/(^|[\s(])I{2}($|[.,:;)\s'])/g, '$1iki$2');      // roman II
  s = s.replace(/(^|[\s(])I($|[.,:;)\s'])/g, '$1bir$2');         // roman I
  s = s.replace(/≤/g, ' küçük eşit ');
  s = s.replace(/≥/g, ' büyük eşit ');
  s = s.replace(/⇒|→/g, ', yani ');
  s = s.replace(/δ⁻/g, ' delta eksi ').replace(/δ⁺/g, ' delta artı ');
  s = s.replace(/√/g, ' karekök ');
  s = s.replace(/Δ/g, ' üçgen ');
  s = s.replace(/°/g, ' derece ');
  s = s.replace(/</g, ' küçüktür ').replace(/>/g, ' büyüktür ');
  s = s.replace(/=/g, ' eşittir ');
  s = s.replace(/\+/g, ' artı ');
  s = s.replace(/(^|[\s(])[-−](?=\s*\d)/g, '$1eksi ');           // unary minus before a number
  const subs = { '₀':' sıfır', '₁':' bir', '₂':' iki', '₃':' üç', '₄':' dört', '₅':' beş', '₆':' altı', '₇':' yedi', '₈':' sekiz', '₉':' dokuz' };
  s = s.replace(/[₀-₉]/g, ch => subs[ch]);
  s = s.replace(/\s{2,}/g, ' ').trim();
  return s;
}

// MBROLA'nın tr diphone veritabanı "ğ" için diphone içermiyor (sessizlik
// boşluğu üretir). Gerçek telaffuza uygun düşür: ince ünlüden sonra y'ye,
// kalın ünlüden sonra ünlü uzatmasına çevir. Yalnız espeak/mbrola yolunda.
function mbrolaNormalizeTr(text){
  return text
    .replace(/([eiöü])ğ/gi, '$1y')
    .replace(/([aıou])ğ([aıou])/gi, '$1$2')
    .replace(/([aıou])ğ/gi, '$1$1')
    .replace(/ğ/gi, 'g');
}

export function synthesizeCaptionMp3(text, mp3Path){
  text = speechNormalizeTr(text);
  if (process.env.ELEVENLABS_API_KEY && !elevenBroken){
    try {
      const voice = process.env.ELEVEN_VOICE_ID || ELEVEN_DEFAULT_VOICE;
      execFileSync('curl', ['-sS', '--fail', '--max-time', '90',
        '-H', 'xi-api-key: ' + process.env.ELEVENLABS_API_KEY,
        '-H', 'Content-Type: application/json',
        '-d', JSON.stringify({
          text,
          model_id: 'eleven_multilingual_v2',
          voice_settings: { stability: 0.55, similarity_boost: 0.75 }
        }),
        '-o', mp3Path,
        `https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=mp3_22050_32`]);
      if (existsSync(mp3Path) && statSync(mp3Path).size > 1000) return 'elevenlabs';
      throw new Error('boş/kısa yanıt');
    } catch (e){
      elevenBroken = true; // bir kez düştüyse kalan caption'larda tekrar deneme — tutarlı tek ses kullan
      rmSync(mp3Path, { force: true });
      console.warn('ElevenLabs kullanılamadı (' + (e.message || '').split('\n')[0] + ') — yerel sese düşülüyor.');
    }
  }
  const wav = mp3Path + '.tmp.wav';
  const pho = mp3Path + '.tmp.pho';
  const localText = mbrolaNormalizeTr(text);
  // MBROLA yolu: espeak'in fonem çıktısındaki, tr diphone veritabanında
  // BULUNMAYAN alofonlar (L/, l/, &, D) veritabanında var olan eşdeğerlerine
  // çevrilip mbrola'ya doğrudan beslenir — aksi halde her eksik diphone
  // sessizlik boşluğuna dönüşüp ünsüz düşürüyordu ("altı" → "a_tı").
  const MB = [
    { esp: 'mb-tr2', db: '/usr/share/mbrola/tr2/tr2' },
    { esp: 'mb-tr1', db: '/usr/share/mbrola/tr1/tr1' }
  ];
  for (const v of MB){
    try {
      if (!existsSync(v.db)) continue;
      const rawPho = execFileSync('espeak-ng', ['-v', v.esp, '-q', '--pho', '-s', '140', localText]).toString();
      const fixedPho = rawPho.split('\n').map(line =>
        line.replace(/^L\//, 'L').replace(/^l\//, 'l').replace(/^&/, '@').replace(/^D(?=\s)/, 'd')
      ).join('\n');
      writeFileSync(pho, fixedPho);
      execFileSync('mbrola', [v.db, pho, wav]);
      if (!existsSync(wav) || statSync(wav).size < 1000) throw new Error('boş wav');
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', wav,
        '-ac', '1', '-ar', '24000', '-b:a', '48k', '-af', 'dynaudnorm=g=7', mp3Path]);
      rmSync(wav, { force: true }); rmSync(pho, { force: true });
      return v.esp;
    } catch (e){ rmSync(wav, { force: true }); rmSync(pho, { force: true }); }
  }
  try {
    execFileSync('espeak-ng', ['-v', 'tr', '-s', '140', '-a', '180', '-w', wav, localText]);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', wav,
      '-ac', '1', '-ar', '24000', '-b:a', '48k', '-af', 'dynaudnorm=g=7', mp3Path]);
    rmSync(wav, { force: true });
    return 'tr';
  } catch (e){
    rmSync(wav, { force: true });
    throw new Error('hiçbir TTS sağlayıcısı çalışmadı (espeak-ng kurulu mu?)');
  }
}
