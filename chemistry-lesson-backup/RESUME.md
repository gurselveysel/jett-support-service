# Kimya Dersi Animasyonu — Yedek ve Devam Notu

## Bu klasör ne içeriyor?

- `jett_lesson_kimya_en_v8_stable.html` — **nihai teslimat**. Görsel base64 olarak gömülü, tek başına (internet olmadan) çalışan, self-contained HTML dosyası. Kullanıcıya teslim edilen son sürüm budur.
- `jett_lesson_v8_template.html` — düzenlenebilir kaynak şablon. Görsel yerine `__IMAGE_BASE64__` placeholder'ı içerir; bu dosya üzerinde değişiklik yapılır.
- `build/build_premium_handwriting.mjs` — `jett_lesson_v8_template.html`'i işleyip Caveat fontundan gerçek glyph-outline path'leri (kerning + basınç-taper ile) üretip `jett_lesson_v8_glyphs.html` çıktısını yazan Node.js build script'i. Çalıştırmak için: `node build_premium_handwriting.mjs` (aynı dizindeki `../jett_lesson_v8_template.html`'i okur, `../jett_lesson_v8_glyphs.html`'e yazar — script'i çalıştırmadan önce yol referanslarını kontrol edin).

## Şu ana kadar yapılanlar (özet)

Kaynak: yüklenen bir Türkçe kimya sınav sorusu fotoğrafı (elektronegatiflik / kısmi yük, XY₂ ve ZX₂ molekülleri, soru 9, cevap E — I, II, III hepsi doğru). Bu fotoğraf üzerinde, tek dosyalık, animasyonlu bir "öğretmen çözüyor" ders videosu/oynatıcısı geliştirildi (v1 → v8), her seferinde kullanıcı geri bildirimiyle iyileştirildi:

- v3: gerçek font glyph-outline izleme (opentype.js + kerning)
- v4: profesyonel/duyarlı (responsive) UI cilası
- v5: kalem fiziği (kerning) + bağımsız doğrulama sahnesi
- v6: doğrulama rozetinin görsel netliği düzeltildi
- v7: kalem imleci senkronizasyonu (yanlış hedef seçimi düzeltildi ama yeni bir kök sorun ortaya çıktı)
- **v8 (son, teslim edilen)**: kalem imlecinin SVG koordinat-uzayı hatası kök nedeniyle düzeltildi (`penTip` kök uzayda dururken panel metnindeki harfleri +1082 birimlik ofseti hesaba katmadan takip ediyordu — `getScreenCTM()` tabanlı matris dönüşümüyle giderildi), ayrıca görsel-üzeri anotasyonlarla panel cümlelerinin zaman pencereleri artık üst üste binmiyor. Süre 40sn'den 53.6sn'ye çıkarıldı (kullanıcı "40sn şartı yok" dedi, kalite için genişletildi). Ölçüm: 300+ birimlik ani kalem sıçraması v7'de 53 iken v8'de 8'e düştü (kalanlar sadece fotoğraf↔defter arası gerçek sahne geçişleri).

v8 kullanıcıya teslim edildi ve onaylandı. Şu an bekleyen açık bir görev YOK — bu yedekleme, oturum/limit kesintisine karşı önlem amaçlı yapıldı.

## Devam Promptu (yeni oturum/hesapta yapıştırmak için)

```
Repo: gurselveysel/jett-support-service, branch: claude/jett-support-github-setup-o1u5fg

chemistry-lesson-backup/ klasöründe önceki bir oturumdan kalan iş var:
- jett_lesson_kimya_en_v8_stable.html: nihai teslim edilmiş ders animasyonu (self-contained, görsel gömülü)
- jett_lesson_v8_template.html: düzenlenebilir kaynak şablon
- build/build_premium_handwriting.mjs: glyph/kerning build script'i
- RESUME.md: bu klasördeki tüm geçmişin özeti

v8, kalem imleci koordinat-uzayı hatasını (panelLayer'ın +1082 ofseti) ve zaman penceresi çakışmalarını düzeltiyor; teslim edildi ve onaylandı. Şu an açık/bekleyen bir görev yok.

Lütfen chemistry-lesson-backup/RESUME.md dosyasını oku, sonra [BURAYA YENİ İSTEĞİNİZİ YAZIN].
```
