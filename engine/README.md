# Jett Jenerik El Yazısı Ders Motoru (v12)

## v12'de eklenenler (v10/v11 üzerine)

- **v11 — InkPhysics**: vuruş başına eğrilik-farkındalıklı zaman haritası (kıvrımda yavaşlar, düzlükte hızlanır) + sahne-senkron sesli anlatım (speechSynthesis).
- **v12 — CameraEngine**: kamera o an yazılan bölgeye pan/zoom yapar (sahne içi aynı-uzay koşusu başına odak, `cameraAt(t)` saf/deterministik, `Kamera: Açık/Kapalı` düğmesi).
- **v12 — Anlatım denetleyicisi**: jest kilidi (iOS/Android), tr-ses zorunluluğu, sessiz-motor tespiti ve dürüst durum etiketleri (`TR ses yok` / `Ses bulunamadı`), 🔊 canlı gösterge, sahne sınırında anlatım bitene kadar üst-sınırlı bekleme, karaoke alt yazı (kelime vurgusu).
- **v12 — Gömülü ses fallback'i**: `instantiate.mjs ... --audio` sahne caption'larını espeak-ng (tr) + ffmpeg ile MP3'e çevirip dosyaya gömer. Çalışma zamanında cihazın kendi Türkçe sesi TERCİH edilir; hiç ses yoksa gömülü parça devreye girer — anlatım her cihazda garanti.
- **v12 — Kelime ritmi + mürekkep yoğunlaşması**: kelime-başı konumlanma duraksaması, noktalama nefesi, uzun kelime ortasında hızlanma; kalemin yavaşladığı yerde çizgi hafifçe kalınlaşır (`pool(1)=1` — bitmiş harflerin dinlenme kalınlığı tekdüze).
- **v12 — render erken-çıkışı**: değişmeyen vuruşlara stil yazılmaz (kare başı yüzlerce yazım → 1-3), mobil performans.

Test: `node check_v12.mjs <ders.html> <panel|nopanel>` — deterministik speechSynthesis stub'ı altında 55+ assert.

---

# (v9 mimari dokümantasyonu — hâlâ geçerli temel)

"Girdi değişir, çıktı kalitesi değişmez" ilkesiyle tasarlanmış, soru-bağımsız
öğretmen-çözüm animasyon motoru. Tek self-contained HTML üretir; internetsiz çalışır.

## Mimari

```
jett_engine_v9_source.html     motorun kaynak kodu (5 slot açık)
        │  node build_engine.mjs
        ▼  (opentype.js + 2 Caveat WOFF gömülür)
jett_engine_v9_template.html   jenerik motor (2 slot açık: sözleşme + görsel)
        │  node instantiate.mjs <contract.json> <image> <out.html>
        ▼
jett_lesson_*.html             nihai ders (öğretmene/öğrenciye giden dosya)
```

Soruya özel TEK girdi: `contract.json` (Claude, fotoğrafa bakarak üretim anında yazar)
+ soru fotoğrafı. Motor hiçbir elle yazılmış saniye/koordinat içermez:

- **ContractGate** — sözleşmede eksik alan varsa animasyon hiç başlamaz, görünür hata ekranı çıkar ("asla tahminle doldurma").
- **SafeZoneMap** — fotoğraf çalışma zamanında canvas'ta analiz edilir (uyarlanır eşikli mürekkep-yoğunluğu ızgarası); fotoğraf-üzeri metin/rozet için boş bölgeyi motor kendisi bulur, bulamazsa içerik deftere düşer.
- **HandwritingEngine** — Caveat glyph-outline'ları gerçek kerning + basınç-taper + stroke→fill crossfade ile ÇALIŞMA ZAMANINDA üretilir (gömülü opentype.js + WOFF1). Kapsanmayan karakter = görünür hata.
- **LayoutEngine** — panel satırları gerçek glyph advance'leriyle sarılır; panel yüksekliği ve viewBox içerikten türer; alt boşluk, alt yazı overlay'inin kapladığı alana oranlı.
- **TimingEngine** — süre içerik hacminden hesaplanır (20–75 sn bandına tek tip ölçekle kelepçelenir). Değişmez (invariant): fotoğraf-üzeri öğe ile defter öğesi ASLA zaman penceresi paylaşmaz — uzay değişiminde kurgusal bariyer + yükleme sonrası assert taraması.
- **PenCursor** — v8'de kanıtlanan sistem: `getScreenCTM()` tabanlı yerel→kök koordinat dönüşümü (önbellekli), "en son başlayan kazanır" hedef seçimi, dt-bağımsız yumuşatma, tutma penceresi, sınırlı eğilim açısı.
- **SelfCheck** — yüklenince kendi kendini doğrular: zamanlama değişmezi, sözleşme alanları, glif sayısı, font kapsaması, görsel yükleme. Kırmızı varsa oynatma reddedilir.

## Sözleşme şeması (özet)

```jsonc
{
  "meta": { "title", "subject", "topic", "character": { "name", "pen_color" } },
  "academic_contract": { "given", "asked", "primary_outcome", "prerequisites": [] },
  "canonical_solution": { "steps": [...], "final_answer": { "value", "display" } },
  "scenes": [
    { "id", "caption", "items": [
      { "space": "photo", "type": "box|ellipse|check|badge|answer-circle", "anchor": {x,y,w,h} },  // 0-1 normalize
      { "space": "photo", "type": "arrow", "from": {x,y}, "to": {x,y} },
      { "space": "photo", "type": "text", "near": {x,y}, "text": "..." },   // SafeZoneMap yer bulur
      { "space": "panel", "type": "text|final-box", "text": "..." }
    ]}
  ]
}
```

Metinlerde `δ ⁺ ⁻ ₀-₉` desteklenir; ok için `=>` kullanın (font kapsaması SelfCheck'te denetlenir).

## Doğrulanmış sonuçlar (2026-07-17)

| | Kimya (gerçek fotoğraf) | Geometri (sentetik, farklı oran) |
|---|---|---|
| Süre (otomatik) | 63.3 sn | 38.4 sn |
| Glif | 487 | 220 |
| Görünür büyük kalem sıçraması | 1 (uzay geçişi) | 2 (uzay geçişi) |
| Fonksiyonel suite (320/375/1440px, gate, complete, konsol) | ALL PASS | ALL PASS |
| Dosya | 613 KB | 473 KB |

Karşılaştırma: v7 53 sıçrama, v8 8 sıçrama, v9 1-2 sıçrama (hepsi meşru sahne geçişi).
Bozuk sözleşme testi: eksik alanlar isimleriyle raporlanır, oynatma reddedilir, 0 glif üretilir.

## Kullanım

```bash
node build_engine.mjs                                  # bir kez (motor değişince)
node instantiate.mjs contract_X.json soru.jpg ders.html # her soru için
node check_v9.mjs ders.html                            # tam test paketi
```
