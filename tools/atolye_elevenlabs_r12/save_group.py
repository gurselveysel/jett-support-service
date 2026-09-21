from pathlib import Path
import json,datetime,hashlib,shutil,zipfile,sys,subprocess
ROOT=Path(__file__).resolve().parent
num=int(sys.argv[1]);tag=f'Grup{num:02d}';folder=ROOT/f'Atolye_R12_{tag}';items=json.loads((ROOT/f'batch{num:02d}.json').read_text());statepath=ROOT/'calisma_durumu.json'
s=json.loads(statepath.read_text() if statepath.exists() else (ROOT.parent/'current_r12/Atolye_SBS_Cozumleri/calisma_durumu.json').read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
s.setdefault('onceki_ozet_R11',s['ozet'].copy());s['surum']=f'6.1-R12-{tag}-125-unique';s['guncelleme']=now
new=[]
for i in items:
 q=folder/i['metadata']['klasor'];qc=json.loads((q/'kalite_kontrol.json').read_text());out=q/'cozum.mp4';r=json.loads((q/'report.json').read_text());assert qc['full_decode_pass']
 assert hashlib.sha256(out.read_bytes()).hexdigest()==qc['sha256'],i['id']
 qc.update(visual_review='passed_actual_beginning_each_note_and_result_frames',auditory_review='not_performed',final_acceptance=False);(q/'kalite_kontrol.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2))
 entry=dict(conditional_analysis=bool(i.get('conditional_analysis')),legacy_upgrade=bool(i.get('legacy_upgrade')),soru_kimligi=i['id'],eslesen_soru=i['pair'][1],mp4_path=i['metadata']['klasor']+'/cozum.mp4',paket=folder.name,provider='elevenlabs',voice_id=r['voice_id'],model_id=r['model_id'],run_id=r['run_id'],run_url='https://github.com/gurselveysel/jett-support-service/actions/runs/'+r['run_id'],audio_commit=r['commit'],video_completed=True,audio_sha256=r['sha256'],audio_duration_seconds=r['duration_seconds'],duration=qc['duration_seconds'],bytes=qc['bytes'],sha256=qc['sha256'],full_decode_pass=True,resolution=[1080,1920],fps='30/1',video_codec='h264',audio_codec='aac',visual_review_pass=True,auditory_review_this_turn=False,final_acceptance=False,source_pair_visually_verified=True,source_A_pdf_page=i['metadata']['pdf_sayfasi'],source_B_pdf_page=i['partner_metadata']['pdf_sayfasi'],timing_source='ElevenLabs provider character alignment: explicit spoken phrase intervals',pen_method='Manual pen centerlines; no font contours or fill')
 assert i.get('legacy_upgrade') or not any(x.get('soru_kimligi')==i['id'] for x in s['video_teslim_manifesti']),i['id']
 s['video_teslim_manifesti'].append(entry);new.append(entry)
 for key in ['metadata','partner_metadata']:
  m=i[key];sq=next(x for x in s['sorular'] if x['soru_kimligi']==m['soru_kimligi']);sq.update({k:m[k] for k in ['soru_kirpma_konumu_pt','dogru_secenek']})
  sq.update(ses_uretildi=True,ses_dosyasi_yerel=True,zamanli_cizim_hazir=True,video_uretildi=True,video_kontrol_edildi=True,gorsel_montaj_uretildi=True,nihai_video_tamamlandi=False,video_durumu='ElevenLabs sesli MP4: teknik ve örnek kare görsel kontrol geçti; işitsel kabul yapılmadı',ses_saglayici='elevenlabs',ortak_anlatim_master_id=i['id'],mp4_path=entry['mp4_path'],teslim_paketi=folder.name,teknik_kontrol=True,gorsel_kontrol=True,isitsel_kabul=False,run_url=entry['run_url'])
  if i.get('conditional_analysis'):sq.update(akademik_nihai_kabul=False,video_turu='kosullu_cozum_ve_sorun_analizi',video_durumu='Sesli koşullu çözüm/sorun analizi üretildi; akademik engel sürüyor; işitsel kabul yok')
  if i.get('academic_correction'):sq['akademik_duzeltme_R12']=i['academic_correction']
  # Linked B records point to the same A video, not a second render.
  if key=='partner_metadata':sq['ortak_video_baglantisi']=i['id']
 s.setdefault('r12_elevenlabs_uretimleri',[]).append(entry)
 allnew=s['r12_elevenlabs_uretimleri'];physical=len(s['video_teslim_manifesti'])
 idmap={x['soru_kimligi']:(x['soru_kimligi'] if x['kitapcik']=='A' else x['eslesen_soru']) for x in s['sorular']}
 unique=len({idmap.get(x['soru_kimligi'],x['soru_kimligi']) for x in s['video_teslim_manifesti']})
 eleven=len({idmap.get(x['soru_kimligi'],x['soru_kimligi']) for x in s['video_teslim_manifesti'] if x.get('provider')=='elevenlabs'})
 legacy=unique-eleven
 made={x['soru_kimligi'] for x in s['video_teslim_manifesti']}
pending=[x for x in s['sorular'] if x['kitapcik']=='A' and x['soru_kimligi'] not in made and x['akademik_durum']=='dogrulandi']
order={'Temel_Matematik':0,'Fen_Bilimleri':1,'Turkce':2,'Sosyal_Bilimler':3}
blocked=[x for x in s['sorular'] if x['kitapcik']=='A' and x['akademik_durum']!='dogrulandi']
queue=pending or [x for x in blocked if x['soru_kimligi'] not in made] or blocked
nq=min(queue,key=lambda x:(order[x['test_kodu']],x['basili_soru_numarasi'])) if queue else {'soru_kimligi':'ISITSEL_KABUL','eslesen_soru':''};nextid=nq['soru_kimligi']
blockedtext=', '.join(x['soru_kimligi'] for x in blocked)
s['ozet'].update(toplam_soru=125,hedef_sesli_video=125,sesli_mp4_mevcut=physical,sesli_mp4_mevcut_benzersiz_soru=unique,onceki_mp4_dosyasi=8,onceki_benzersiz_sesli_soru=5,bu_tur_yeni_sesli_mp4=len(allnew),mevcut_benzersiz_elevenlabs_kaydi=eleven,yeni_ses_kaydi_gereken_benzersiz_soru=125-unique,yeni_video_uretim_kalan=125-unique,nihai_kabul_bekleyen_mevcut_benzersiz_soru=unique-1,bu_tur_teknik_ve_gorsel_kontrol_gecen=len(allnew),bu_tur_nihai_kabul=0,elevenlabs_bu_tur_yeni_ses=len(allnew),siradaki_kesin_video_sorusu=nextid,eslesen_siradaki_B_sorusu=nq['eslesen_soru'],elevenlabs_sesine_gecis_bekleyen_onceki_benzersiz_video=legacy,akademik_engelli_benzersiz_soru=len(blocked),akademik_inceleme_bekleyen_benzersiz_soru=len(blocked),akademik_inceleme_bekleyen_kaynak_kaydi=len(blocked)*2,bagimsiz_dogrulanan_benzersiz=125-len(blocked),kosullu_analiz_videosu=sum(bool(x.get('conditional_analysis')) for x in allnew),akademik_dogrulanmis_video_sayisi=unique-sum(bool(x.get('conditional_analysis')) for x in allnew))
s['siradaki_islem']=nextid+' / '+nq['eslesen_soru']+'. A11/B19 akademik engeli korundu. Mevcut MP3 ve zaman damgalarını yeniden kullan; güncel workflow son grubun seslerini içerir, tekrar çalıştırma.'
s['video_sayim_yontemi']=f'125 A sorusu hedefi. B kayıtları aynı çözüme bağlıdır. {physical} fiziksel MP4 varyantı = {unique} benzersiz soru; kopyalar sayılmaz. {eleven} benzersiz ElevenLabs sesi ve korunmuş {legacy} önceki sağlayıcı çözümü vardır. Nihai kabul 1 önceki kayıt; bu tur işitsel kabul yok.'
s['son_yeniden_kontrol']=dict(tarih=now,revizyon='R12',onceki_mp4_hash_ve_stream_kontrolu=8,yeni_mp4_tam_decode_sayisi=len(allnew),yeni_ses=len(allnew),yeni_mp4=len(allnew),yeniden_ses_uretimi=0,isitsel_yeni_kabul=False)
s['r12_arac_hatalari']=[dict(operation='Local source background PNG write',error='OSError: image file is truncated',resolved=True,resolution='Görsel yeniden oluşturuldu; atomik yazma ve tekrar okuma eklendi. MP3 yeniden üretilmedi.'),dict(operation='Group05 local answer timing binding',error="AssertionError: provider cue missing: E seçeneğini",resolved=True,resolution='Seçeneğidir ve seçeneğini biçimleri için ortak gerçek ifade kökü eşleştirildi; mevcut ses yeniden kullanılınca kalan çizelgeler tamamlandı.')]
s['yapilamayan_kontroller']=['İnsan kulağıyla dinleme / telaffuz ve ses benzerliği onayı yapılmadı.','Yayıncının resmi cevap anahtarı kaynak pakette yok; karşılaştırma yapılmadı.','Son TTS sonrası güncel kredi ayrıca okunmadı; her istek öncesindeki API kota kaydı report.json içinde.']
s['r12_gruplar']=s.get('r12_gruplar',[])+[dict(grup=num,yeni_soru=len(new),run_url=new[0]['run_url'],tarih=now)]
statepath.write_text(json.dumps(s,ensure_ascii=False,indent=2))
text=f'''ATÖLYE SBS — R12 {tag} — {now}
HEDEF: A kitapçığında 125 benzersiz soru, 125 ayrı sesli MP4. B eşleşmeleri aynı videoya bağlı.
GERÇEK DOSYA SAYIMI: {unique} benzersiz soru, {physical} fiziksel MP4 varyantı.
Bu tur: {len(allnew)} yeni ElevenLabs sesi + MP4. Mevcut toplam ElevenLabs çözümü: {eleven}.
Önceki tüm varyantlar korundu. ElevenLabs geçişi bekleyen benzersiz soru: {legacy}.
Yeni video üretimi kalan: {125-unique}. Önceki nihai kabul: 1. Nihai kabul bekleyen toplam: 124.
Akademik engelli: {len(blocked)} benzersiz soru ({blockedtext}). Erişim engeli: 0.
Yeni MP4'ler: 1080×1920,30fps,H264/AAC; tam çözümleme başarılı.
Gerçek başlangıç, işlem ve sonuç kareleri incelendi. İşitsel dinleme yapılmadı; nihai kabul verilmedi.

KESİN DEVAM: {nextid} / {nq['eslesen_soru']}.
A11/B19 belirsizliğini çözmeden tek cevap dayatma. Tüm derslerde kalan sıra, calisma_durumu.json içindeki A ana kimlikleri ve video_uretildi durumlarından izlenir.
Mevcut akademik arşivi baştan hazırlama. Özgün soru ve seçenekleri kontrol et; kayıtlı cevap harfi tek başına kanıt değildir.
Son iş akışı yeni grup metinlerini içerir. Aynı sesleri üretmek için yeniden çalıştırma.
Başarılı speech.mp3, alignment.json, speech.json, zaman_cizelgesi.json dosyaları her soru klasöründe.
Görsel düzeltmede aynı sesi kullan; kredi harcama.

Repo: gurselveysel/jett-support-service
Branch: atolye-elevenlabs-20260921
Secret: ELEVENLABS_API_KEY; değer açığa çıkarılmadı, değiştirilmedi.
Voice: tZYpRZkmCNQcfmtDbhUg. Model: eleven_v3. Ses/model erişimi gerçek üretimle doğrulandı.
Son run: {new[0]['run_url']}
Son audio commit: {new[0]['audio_commit']}
Mevcut dahilî kredi sınırı içinde üretim; satın alma, aşım veya fatura ayarı değişikliği yok.
Paket: {folder.name}.zip — yalnız bu grubun {len(new)} videosu, 125'in tamamı değildir.
Kapsam kaydı: calisma_durumu.json. Bu dosya çalışan bir arka plan görevi değildir.
'''
(ROOT/'DEVAM_NOKTASI.txt').write_text(text)
for name in ['calisma_durumu.json','DEVAM_NOKTASI.txt']:shutil.copy2(ROOT/name,folder/name)
# A/B map and a portable list of all questions produced so far.
(folder/'BU_PAKET.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
(folder/'AC.txt').write_text('Bu kısmi paket '+str(len(new))+' yeni soru videosu içerir. A/ders/soru/cozum.mp4 dosyalarını açın. B sorusu aynı MP4 sonunda kendi özgün görseli, soru numarası ve PDF sayfasıyla gösterilir. İşitsel kabul yapılmadı.\n')
zp=ROOT/(folder.name+'.zip')
ztmp=zp.with_suffix('.pending.zip')
with zipfile.ZipFile(ztmp,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for f in folder.rglob('*'):
  if f.is_file() and '.tmp' not in f.name and '.pending' not in f.name and '.muxing' not in f.name:z.write(f,str(Path(folder.name)/f.relative_to(folder)))
assert zipfile.ZipFile(ztmp).testzip() is None
ztmp.replace(zp)
print(json.dumps({'group':num,'unique':unique,'physical':physical,'new':len(new),'remaining':125-unique,'zip_bytes':zp.stat().st_size},ensure_ascii=False))
