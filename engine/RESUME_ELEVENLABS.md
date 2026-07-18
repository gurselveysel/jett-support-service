# jett engine v12 — devam talimatı (ElevenLabs v3 doğal anlatım tamamlandı)

Son durum (dal: `claude/jett-elevenlabs-lessons-32kbbq`, son commit: `610abe2`):
ElevenLabs erişimi açık, hesap **Creator plana yükseltildi** (121.000 karakter/ay —
bu oturum başında free tier'ın 10.000'i kalibrasyon testleriyle tükenmişti).
3 ders de `eleven_v3` + audio-tag'li doğal anlatımla üretildi, `check_v12.mjs`
ALL PASS verdi, HTML+MP4 kullanıcıya teslim edildi, yalnızca HTML'ler commit'lenip
push edildi (mp4 `.gitignore`'da). Bu dosya artık bir **devam noktası özeti** —
yeni bir oturumda buradan ilerlenir.

## Mimari (bu oturumda eklendi)

Eskiden `contract_*.json`'daki `scene.caption` (ekran metni) aynen TTS'e
gidiyordu — sabit/robotik okundu. Şimdi ayrı bir alan var:

- `scene.caption` — ekranda görünen + karaoke metni. **Değişmez.**
- `scene.elevenText` — ElevenLabs'e giden, audio-tag'li (`[warmly]`,
  `[thoughtful]`, `[curious]`, `[pause]` …) ve noktalamayla (`...`) doğal
  duraklama/vurgu içeren konuşma metni. Yoksa `caption` kullanılır (geriye
  dönük uyumlu).
- `scene.stability` / `scene.style` / `scene.speed` — sahne bazlı
  `voice_settings` (v3: `similarity_boost` YOK, `speed` var). Düşük stability
  (~0.3) = tag'lere daha duyarlı/canlı; yüksek (~0.4) = sakin/düz.

Kod tarafı: `tts.mjs` (`synthesizeCaptionMp3(text, mp3Path, opts)` — `opts.
elevenText/stability/style/speed`), `instantiate.mjs` ve `render_video.mjs`
bu alanları contract'tan okuyup geçiriyor, `jett_engine_v12_source.html`'daki
`sceneMeta`/`window.__sceneBounds` bu alanları taşıyor (build_engine.mjs ile
template'e derlenir, template gitignore'da — HER oturumda yeniden üretilmeli).

MBROLA/espeak yedek yolu **hiçbir zaman** `elevenText`/tag görmez — yalnız
düz `caption`'ı okur (audio tag'ler ekrana da yerel sese de sızmaz).

## Kritik kısıt: sahne süre bütçesi

Her sahnenin bir "taban süresi" var (contract'taki `items`'in çizim/el yazısı
süresinden türetilir, `window.__sceneBounds`'tan `tEnd - tStart` ile
ölçülür). Canlı oynatıcı VE `render_video.mjs`, gerçek anlatım sesi taban
süreyi aşarsa sahneyi **en fazla 6 saniye** daha bekletir (`HOLD_CAP` —
`render_video.mjs`), sonra bekletmeden geçer (ses bir sonraki sahneye
taşabilir). Yani her `elevenText`, o sahnenin **(taban süre + 6s)** bütçesine
sığacak uzunlukta olmalı. Bu oturumda 3 dersin tüm sahneleri gerçek
ElevenLabs sesiyle ölçülüp bu bütçeye kalibre edildi — yeni bir ders/contract
eklerken aynı yöntem izlenmeli:

```bash
# taban süreleri ölç (audio olmadan instantiate + playwright ile window.__sceneBounds oku)
node instantiate.mjs contract_X.json X_source.jpg /tmp/test.html
# sonra playwright ile page.evaluate(() => window.__sceneBounds) → tEnd-tStart

# elevenText süresini ölç (tek tek, TÜM sahneleri defalarca göndermekten kaçın — kota gider)
node -e 'import("./tts.mjs").then(({synthesizeCaptionMp3}) => { ... })'
# ffprobe ile mp3 süresini al, taban+6 ile karşılaştır
```

## Ortam kurulumu (yeni konteynerde tekrar gerekli)

```bash
(mkdir -p build && cd build && npm init -y && npm i opentype.js)
(mkdir -p fonttest && cd fonttest && npm init -y && npm i @fontsource/caveat)
apt-get install -y espeak-ng mbrola mbrola-tr1 mbrola-tr2 ffmpeg
cd engine && node build_engine.mjs   # jett_engine_v12_template.html üretir (gitignore'da)
```

```bash
export ELEVENLABS_API_KEY=<anahtar>              # kullanıcı sağlar, ASLA commit'lenmez
export ELEVEN_VOICE_ID=tZYpRZkmCNQcfmtDbhUg       # GOGO Hoca — workspace'e özel, Türkçe/öğretmen tonu
curl -sS -o /dev/null -w "%{http_code}\n" https://api.elevenlabs.io/v1/models -H "xi-api-key: $ELEVENLABS_API_KEY"  # 200 bekleniyor
curl -sS https://api.elevenlabs.io/v1/user/subscription -H "xi-api-key: $ELEVENLABS_API_KEY"  # kota kontrolü (character_count/character_limit)

node instantiate.mjs contract_fonksiyon_v10.json fonksiyon_source.jpg jett_lesson_fonksiyon_v12.html --audio   # "ses: elevenlabs" beklenir
node render_video.mjs jett_lesson_fonksiyon_v12.html jett_video_fonksiyon_v12.mp4                                # "ses sağlayıcısı: elevenlabs" beklenir
node check_v12.mjs jett_lesson_fonksiyon_v12.html nopanel   # (kimya: panel)
ffprobe -v error -show_entries format=duration jett_video_fonksiyon_v12.mp4
```

## Yapılmadı / sonraki oturum için açık noktalar

1. **Gerçek dinleme/algısal eleştiri yapılmadı.** Bu oturumda yalnızca *süre
   bütçesi* kalibre edildi (elevenText, taban+6s içine sığdırıldı). "Gerçek
   öğretmenden ayırt edilemez mi" sorusu için üretilen mp4'lerin bizzat
   dinlenip ritim/duraklama/tekrar-deseni açısından eleştirilmesi, gerekirse
   `elevenText`/`stability`/`style` bir tur daha revize edilmesi hâlâ açık.
2. Commit imzalama: bu ortamdaki SSH imzalama anahtarı (`~/.ssh/
   commit_signing_key.pub`) boş — commit'ler GitHub'da "Unverified" görünüyor.
   Ortam sağlayıcısı tarafında düzeltilmesi gereken bir altyapı konusu,
   depo/kod tarafında yapılacak bir şey yok.
3. ElevenLabs artık Creator planda (121k karakter/ay) — yine de yeni
   kalibrasyon turlarında tüm sahneleri tekrar tekrar göndermek yerine
   birkaç örnek sahneyle ölçüp genellemek daha tutumlu olur.

## Teslim sırası (kullanıcı tercihi)

Fonksiyon → Kimya → Üçgen. Her ders: HTML + MP4 birlikte gönderilir,
yalnızca HTML commit'lenir (mp4 `.gitignore`'da), API anahtarı hiçbir
commit'e/dosyaya yazılmaz.
