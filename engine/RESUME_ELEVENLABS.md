# ElevenLabs sesiyle yeniden üretim — devam talimatı

Ağ politikasına `api.elevenlabs.io` eklendi ancak çalışan oturumlar egress
kurallarını başlangıçta sabitlediği için değişiklik ancak YENİ bir oturumda
etkili olur. Yeni oturumda yapılacaklar (anahtar depoya YAZILMAZ, ortam
değişkeninden verilir):

```bash
cd engine
export ELEVENLABS_API_KEY=<anahtar>          # kullanıcı sağlar
# (isteğe bağlı) farklı ses: export ELEVEN_VOICE_ID=<voice_id>

# 1) hızlı doğrulama — 000/403 yerine 200 dönmeli:
curl -sS -o /dev/null -w "%{http_code}\n" https://api.elevenlabs.io/v1/models -H "xi-api-key: $ELEVENLABS_API_KEY"

# 2) dersler (instantiate 'ses: elevenlabs' yazmalı; 'mb-tr2' yazarsa erişim yok demektir):
node instantiate.mjs contract_fonksiyon_v10.json fonksiyon_source.jpg jett_lesson_fonksiyon_v12.html --audio
node instantiate.mjs contract_kimya.json kimya_source.jpg jett_lesson_kimya_v12.html --audio
node instantiate.mjs contract_ucgen_v10.json ucgen_source.jpg jett_lesson_ucgen_v12.html --audio

# 3) videolar:
node render_video.mjs jett_lesson_fonksiyon_v12.html jett_video_fonksiyon_v12.mp4
node render_video.mjs jett_lesson_kimya_v12.html jett_video_kimya_v12.mp4
node render_video.mjs jett_lesson_ucgen_v12.html jett_video_ucgen_v12.mp4

# 4) doğrulama + teslim: check_v12.mjs üçünde ALL PASS; HTML+MP4 kullanıcıya gönderilir.
```

Gereksinimler yeni konteynerde yeniden kurulmalı (build/fonttest npm kurulumları
+ apt: espeak-ng mbrola mbrola-tr1 mbrola-tr2 ffmpeg — espeak/mbrola yalnız
ElevenLabs erişilemezse yedek olarak kullanılır):

```bash
(mkdir -p build && cd build && npm init -y && npm i opentype.js)
(mkdir -p fonttest && cd fonttest && npm init -y && npm i @fontsource/caveat)
apt-get install -y espeak-ng mbrola mbrola-tr1 mbrola-tr2 ffmpeg
cd engine && node build_engine.mjs
```

Teslim sırası kullanıcı isteğiyle: önce fonksiyon, sonra kimya, sonra üçgen.
