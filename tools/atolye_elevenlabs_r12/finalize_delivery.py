"""Build an audited current selection; keep historical variants and acceptance separate."""
from pathlib import Path
import json,hashlib,shutil,zipfile,datetime,collections,os
ROOT=Path(__file__).resolve().parent
state=json.loads((ROOT/'calisma_durumu.json').read_text())
old=ROOT.parent/'production_r11/Atolye_5_Soru_8_MP4_R11'
selected={};physical=[]
for e in state['video_teslim_manifesti']:
 f=(ROOT/e['paket']/e['mp4_path']) if e.get('paket') else old/e['mp4_path']
 assert f.is_file(),f
 assert hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256'],f
 assert f.stat().st_size==e['bytes'],f
 physical.append((e,f))
 if e['soru_kimligi'].startswith('A-'):selected[e['soru_kimligi']]=(e,f)
assert len(physical)==131 and len(selected)==125
qs={x['soru_kimligi']:x for x in state['sorular']}
blocked=[q for q in qs.values() if q['kitapcik']=='A' and q['akademik_durum']!='dogrulandi']
assert len(blocked)==3
out=ROOT/'Atolye_SBS_Mevcut_Videolar_R12';out.mkdir(exist_ok=True)
audiofolder=ROOT/'Atolye_SBS_Ses_ve_Zamanlamalar_R12';audiofolder.mkdir(exist_ok=True)
manifest=[];subjects=collections.Counter();reports=[]
for ident,(e,f) in sorted(selected.items()):
 q=qs[ident];rel=Path(q['klasor']);dest=out/rel;dest.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(f,dest/'cozum.mp4')
 friendly=ROOT/'videolar'/(ident+('_R12.mp4' if e.get('paket') else '_R11.mp4'))
 if not friendly.exists():shutil.copyfile(f,friendly)
 asrc=f.parent;adest=audiofolder/rel;adest.mkdir(parents=True,exist_ok=True)
 for name in ['speech.mp3','alignment.json','speech.json','report.json','narration.txt','zaman_cizelgesi.json','soru_ve_kaynak.json','kalite_kontrol.json','kaynak_A.png','kaynak_B.png']:
  if (asrc/name).is_file():shutil.copyfile(asrc/name,adest/name)
 assert (adest/'speech.mp3').is_file() and (adest/'alignment.json').is_file()
 assert hashlib.sha256((adest/'speech.mp3').read_bytes()).hexdigest()==e['audio_sha256']
 r=json.loads((asrc/'report.json').read_text());reports.append(r)
 conditional=q['akademik_durum']!='dogrulandi';subjects[q['ders']]+=1
 entry=dict(soru=ident,ders=q['ders'],A_numara=q['basili_soru_numarasi'],B_eslesme=q['eslesen_soru'],A_pdf_sayfa=q['pdf_sayfasi'],B_pdf_sayfa=qs[q['eslesen_soru']]['pdf_sayfasi'],mp4=str(rel/'cozum.mp4'),sha256=e['sha256'],bytes=f.stat().st_size,sure_saniye=e['duration'],voice_id=e['voice_id'],model=e['model_id'],run_url=e['run_url'],teknik_kontrol=True,gorsel_ornek_kare_kontrolu=True,isitsel_kabul=False,nihai_kabul=False,kosullu_analiz=conditional,akademik_durum=q['akademik_durum'],akademik_engel=q.get('engel',''),tekil_indirme_yolu=str(friendly))
 manifest.append(entry)
 (dest/'soru_kaydi.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2))
 (adest/'secili_video_kaydi.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2))
assert all(e['voice_id']=='tZYpRZkmCNQcfmtDbhUg' and e['model']=='eleven_v3' for e in manifest)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
state['surum']='6.2-R12-125-MP4-3-academic-holds';state['guncelleme']=now
state['ozet'].update(sesli_nihai_video_tamamlanan=0,sesli_nihai_video_kalan=125,nihai_kabul_bekleyen_mevcut_benzersiz_soru=125,onceki_arsiv_nihai_kabul=1,guncel_secili_mp4=125,guncel_secili_teknik_kontrol=125,guncel_secili_gorsel_ornek_kare_kontrolu=125,guncel_secili_isitsel_kabul=0,guncel_secili_nihai_kabul=0,akademik_dogrulanmis_video_sayisi=122,kosullu_analiz_videosu=3,akademik_cozumu_tamamlama_bekleyen=3,guncel_secili_elevenlabs_sesi=125,yeni_video_uretim_kalan=0,elevenlabs_sesine_gecis_bekleyen_onceki_benzersiz_video=0,siradaki_kesin_video_sorusu=None,eslesen_siradaki_B_sorusu=None,siradaki_akademik_kontrol='A-Temel_Matematik-02',siradaki_isitsel_kabul='A-Temel_Matematik-01')
state['secili_video_manifesti']=manifest
state['ders_bazinda_secili_video']=dict(subjects)
state['siradaki_islem']='A-Temel_Matematik-02 / B-Temel_Matematik-15: a doğal sayı koşulunu yayıncıdan doğrula. Koşullu analiz videosu hazır. Sonra A-Matematik11/B19 ve A-Fen01/B07. Yeni ses üretimi gerekmiyor. İşitsel kabul sırası A-Matematik01/B14 ile başlar.'
state['guncel_engel']={'erisim':None,'akademik_sorular':[q['soru_kimligi'] for q in blocked],'isitsel_kabul':'Dinleme yeteneği olmadığı için 125 güncel sürümde yapılmadı.'}
state['video_sayim_yontemi']='125 A kimliği için seçili 125 ElevenLabs MP4:122 doğrulanmış çözüm+3 koşullu analiz. B eşleşmeleri bu dosyalara bağlı. Arşivde131 teslim MP4 varyantı;8 eski dosya korundu,123 R12 dosyası eklendi. Kopyalanmış teslim konumları ve geçici dosyalar yeniden sayılmaz. Güncel seçili nihai kabul0;eski arşivde kabul edilmiş1 sürüm ayrı korunuyor.'
state['ses_saglayici_gecis_kontrolu']['runs']=list(dict.fromkeys(e['run_url'] for e in manifest))
state['ses_saglayici_gecis_kontrolu']['latest_run']='https://github.com/gurselveysel/jett-support-service/actions/runs/35651947588'
state['r12_son_dosya_denetimi']=dict(tarih=now,hash_ve_boyut_eslesen_fiziksel_varyant=131,secili_benzersiz_mp4=125,gercek_ses_ve_alignment=125,bos_olmayan_credential_ve_gercek_api=True,son_grup_tts_run='35651947588',ses_yeniden_uretim_gorsel_duzeltme=0,eski_saglayicidan_elevenlabs_gecisi=3,teknik_decode_kayitlari=125,gorsel_ornek_kare_incelemesi=125,isitsel_dinleme=False)
state['r12_arac_hatalari'] += [dict(operation='ZIP packaging',error='BadZipFile on group08/09 and temporary muxing entries in earlier packages',resolved=True,resolution='ZIP atomik yazma ile yeniden oluşturuldu; tüm üyeler CRC ile okundu; geçici muxing dosyaları paketlerden çıkarıldı. MP3/MP4 yeniden üretilmedi.'),dict(operation='Source PDF browser screenshot',error='TimeoutError / Internal Error for some MEB PDF requests',resolved=True,resolution='MEB kaynak metni erişilebilir resmi PDF üzerinden doğrulandı. Erişilemeyen ekran görüntüleri görülmüş sayılmadı.')]
state['not']='125 video dosyası hazır; akademik çözüm kabulü3 soruda bekliyor. İşitsel dinleme yapılmadığı için güncel sürümler nihai kabul almadı. Çalışan arka plan görevi yok.'
state['teslim_paketleri']=dict(video='Atolye_SBS_Mevcut_Videolar_R12.zip',ses_ve_zamanlama='Atolye_SBS_Ses_ve_Zamanlamalar_R12.zip',indeks='VIDEO_LISTESI.md')
(ROOT/'calisma_durumu.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
continuation=f'''ATÖLYE SBS — R12 güncel dosya teslimi — {now}
HEDEF:125 benzersiz A sorusu. B eşleşmeleri aynı çözüme bağlı;250 video hedefi yok.
DOSYALAR:125 seçili ElevenLabs sesli MP4 hazır.122 doğrulanmış çözüm+3 koşullu çözüm/sorun analizi.
ARŞİV:131 teslim MP4 varyantı;8 önceki MP4 aynen korundu,123 R12 MP4 üretildi.
KALAN YENİ MP4:0. AKADEMİK TAMAMLAMA BEKLEYEN:3. ERİŞİM ENGELİ:0.
TEKNİK KONTROL:125. GÖRSEL ÖRNEK KARE KONTROLÜ:125. İŞİTSEL KABUL:0.
GÜNCEL SEÇİLİ NİHAİ KABUL:0/125. ÖNCEKİ ARŞİVDE KABUL EDİLMİŞ SÜRÜM:1; yeni sürüme taşınmadı.

KESİN DEVAM NOKTASI: A-Temel_Matematik-02 / B-Temel_Matematik-15.
İşlem: a doğal sayı koşulunun eksikliğini yayıncıdan doğrula. Koşullu video hazır; koşulsuz B işaretlenmedi.
Ardından A-Temel_Matematik-11 / B-Temel_Matematik-19: bölmenin tam sayı bölmesi tanımını doğrula.
Ardından A-Fen_Bilimleri-01 / B-Fen_Bilimleri-07: B ve E satırlarının birlikte sorunlu oluşunu yayıncıya teyit ettir.
İŞİTSEL KABUL SIRASI: A-Temel_Matematik-01 / B-Temel_Matematik-14, sonra A soru kimlikleri.
Yayıncının resmi cevap anahtarı mevcut kaynaklarda yok. Teyit için mesaj gönderilmedi.

Ses: GOGO Hoca / tZYpRZkmCNQcfmtDbhUg. Model: eleven_v3.
Son gerçek TTS: https://github.com/gurselveysel/jett-support-service/actions/runs/35651947588
Ses commit:4e5076fd54901a39eb9ca886afadf1eae409d25f
Repo:gurselveysel/jett-support-service. Branch:atolye-elevenlabs-20260921.
Secret:ELEVENLABS_API_KEY; gerçek üretimde boş değil, API erişimi doğrulandı. Gizli değer yazılmadı/değiştirilmedi.
Mevcut kredi dahilinde üretildi; satın alma/aşım/abonelik/limit değişikliği yok.
Son istek öncesi dahilî kredi:317946. Son istek sonrası kota ayrıca okunmadı.
Mevcut speech.mp3 ve alignment.json dosyalarını kullan. Görsel düzeltmede ses üretimini tekrarlama.
Tüm MP4:1080×1920,30fps,H264/AAC. Ses gerçek sağlayıcı zamanlarıyla bağlı ince merkez çizgisi kalem yolları.
Teknik çözümleme dinleme değildir; telaffuz/ses benzerliği insan kulağıyla onaylanmadı.

PAKETLER:Atolye_SBS_Mevcut_Videolar_R12.zip; Atolye_SBS_Ses_ve_Zamanlamalar_R12.zip.
Video paketi:A/ders/soru/cozum.mp4. VIDEO_LISTESI.md tekil bağlantıları içerir.
Bu dosya çalışan arka plan görevi değildir.125 sorunun tamamı nihai kabul aldı iddiası yoktur.
'''
(ROOT/'DEVAM_NOKTASI.txt').write_text(continuation)
index=['# Atölye SBS — Video listesi','', '125 seçili sesli MP4:122 doğrulanmış çözüm,3 koşullu analiz. İşitsel kabul ve güncel nihai kabul yapılmadı.','', '| Ders | A soru | B soru | MP4 | Akademik durum |','|---|---:|---:|---|---|']
order={'Turkce':0,'Sosyal_Bilimler':1,'Temel_Matematik':2,'Fen_Bilimleri':3}
for e in sorted(manifest,key=lambda e:(order[qs[e['soru']]['test_kodu']],e['A_numara'])):
 status='Koşullu analiz;teyit bekliyor' if e['kosullu_analiz'] else 'Çözüm doğrulandı'
 index.append(f"| {e['ders']} | {e['A_numara']} | {e['B_eslesme'].rsplit('-',1)[1]} | [Videoyu aç](sandbox:{e['tekil_indirme_yolu']}) | {status} |")
(ROOT/'VIDEO_LISTESI.md').write_text('\n'.join(index)+'\n')
for folder in [out,audiofolder]:
 for name in ['calisma_durumu.json','DEVAM_NOKTASI.txt']:shutil.copyfile(ROOT/name,folder/name)
 (folder/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(out/'AC.txt').write_text('ZIP dosyasını çıkarın. A/ders/soru/cozum.mp4 dosyasını açın.125 dosya vardır;3 soruda koşullu analiz bulunur. İşitsel ve nihai kabul bekler.\n')
for folder in [out,audiofolder]:
 final=ROOT/(folder.name+'.zip');tmp=ROOT/(folder.name+'.pending.zip')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for f in folder.rglob('*'):
   if f.is_file():z.write(f,str(Path(folder.name)/f.relative_to(folder)))
 with tmp.open('rb') as f:os.fsync(f.fileno())
 with zipfile.ZipFile(tmp) as z:
  assert z.testzip() is None
  assert len([x for x in z.namelist() if x.endswith('.mp4' if folder==out else '/speech.mp3')])==125
 tmp.replace(final);print(final.name,final.stat().st_size,flush=True)
print(json.dumps(dict(selected=125,physical=131,academic_solved=122,conditional=3,technical=125,visual_samples=125,auditory=0,current_final_acceptance=0,old_archive_final_acceptance=1,subjects=subjects,total_video_seconds=round(sum(e['sure_saniye'] for e in manifest),3)),ensure_ascii=False))
