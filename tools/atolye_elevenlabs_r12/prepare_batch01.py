from pathlib import Path
import json
R=Path(__file__).resolve().parent
items=[]
def add(id,segments,notes,answer,marks=None):
 items.append(dict(id=id,segments=segments,notes=notes,answer=answer,marks=marks or []))
# Each note references an actual spoken substring; no whole-video equal allocation.
add('A-Temel_Matematik-07',[
 'İç içe kökü açarak işlemi sadeleştirelim. Kök yedi eksi kök otuz üç ifadesinin tamamı bir karekökün içinde. Bunu, kök on bir eksi kök üç farkının kök ikiye bölümü olarak yazabiliriz.',
 'Neden böyle yazdığımızı karesini alarak kontrol edelim. On bir artı üç eksi iki kök otuz üç ifadesini ikiye bölersek yedi eksi kök otuz üç çıkar. Fark pozitif olduğu için dönüşümümüz geçerlidir.',
 'Diğer taraftan kök yüz yirmi sekiz, sekiz kök ikiye eşittir. Çarpımda kök ikiler sadeleşir. Geriye sekiz çarpı, kök on bir eksi kök üç, bölü kök on bir artı kök üç kalır.',
 'Pay ile paydayı, paydanın eşleniği olan kök on bir eksi kök üç ile çarpalım. Paydada on bir eksi üç, yani sekiz oluşur. Baştaki sekizle sadeleşince, kök on bir eksi kök üç farkının karesi kalır.',
 'Bu kareyi açarsak on dört eksi iki kök otuz üç elde ederiz. Sorudaki artı iki kök otuz üçü de ekleyince köklü terimler birbirini götürür. Sonuç on dört. A seçeneğini işaretliyoruz.'
],[('√(7−√33)=(√11−√3)/√2','Bunu, kök on bir eksi kök üç farkının kök ikiye bölümü olarak yazabiliriz'),('√128=8√2','kök yüz yirmi sekiz, sekiz kök ikiye eşittir'),('8(√11−√3)/(√11+√3)','Geriye sekiz çarpı, kök on bir eksi kök üç, bölü kök on bir artı kök üç kalır'),('(√11−√3)²','Baştaki sekizle sadeleşince, kök on bir eksi kök üç farkının karesi kalır'),('14−2√33+2√33=14','on dört eksi iki kök otuz üç elde ederiz. Sorudaki artı iki kök otuz üçü de ekleyince köklü terimler birbirini götürür. Sonuç on dört')],'A')
add('A-Temel_Matematik-08',[
 'İki bitkinin birlikte yaşayabildiği sıcaklıkları arıyoruz. A bitkisi eksi sekiz ile yirmi iki derece arasında yaşayabiliyor. B bitkisinin aralığı ise eksi dört ile yirmi sekiz.',
 'Bir sıcaklığın her iki aralıkta da bulunması gerekir. Alt sınırların büyüğü eksi dört, üst sınırların küçüğü yirmi ikidir. Ortak aralığımız eksi dört ile yirmi iki, sınırlar dahil.',
 'Şimdi bu aralığı mutlak değerle yazalım. Orta nokta için eksi dört ile yirmi ikiyi toplayıp ikiye böleriz. On sekiz bölü iki, dokuz eder. Uç noktaların dokuza uzaklığı on üçtür.',
 'O halde iks eksi dokuzun mutlak değeri, on üçten küçük ya da eşittir. Eşitliği unutmuyoruz; en az ve en çok değerler de kabul ediliyor. A seçeneğini işaretliyoruz.'
],[('A: [−8,22]','A bitkisi eksi sekiz ile yirmi iki derece arasında yaşayabiliyor'),('B: [−4,28]','B bitkisinin aralığı ise eksi dört ile yirmi sekiz'),('−4 ≤ x ≤ 22','Ortak aralığımız eksi dört ile yirmi iki, sınırlar dahil'),('(−4+22)/2=9','eksi dört ile yirmi ikiyi toplayıp ikiye böleriz. On sekiz bölü iki, dokuz eder'),('|x−9| ≤ 13','iks eksi dokuzun mutlak değeri, on üçten küçük ya da eşittir')],'A')
add('A-Temel_Matematik-09',[
 'İki eşitsizlik aynı anda sağlanmalı. Önce iks eksi birin mutlak değeri üçten küçük ya da eşit koşulunu açalım. Eksi üç, iks eksi birden küçük ya da eşit; iks eksi bir de üçten küçük ya da eşit.',
 'Her tarafa bir ekleyince eksi iki küçük ya da eşit iks, küçük ya da eşit dört olur. Şimdi ikinci koşula bakalım. İksin mutlak değeri birden büyükse iks eksi birden küçük veya birden büyüktür.',
 'İlk aralıktan, eksi bir ile bir arasını ve bu sınır noktalarını çıkarıyoruz. Eksi ikiden eksi bire kadar olan parça ile birden dörde kadar olan parça kalır.',
 'Eksi iki ve dört dahildir; bu noktalar dolu olmalı. Eksi bir ve bir dahil değildir; bu noktalar boş olmalı. Bu gösterim C seçeneğinde var. C seçeneğini işaretliyoruz.'
],[('−3 ≤ x−1 ≤ 3','Eksi üç, iks eksi birden küçük ya da eşit; iks eksi bir de üçten küçük ya da eşit'),('−2 ≤ x ≤ 4','eksi iki küçük ya da eşit iks, küçük ya da eşit dört olur'),('x < −1 veya x > 1','iks eksi birden küçük veya birden büyüktür'),('[−2,−1) ∪ (1,4]','Eksi ikiden eksi bire kadar olan parça ile birden dörde kadar olan parça kalır')],'C')
add('A-Temel_Matematik-10',[
 'Araştırmanın evrenini, amacını ve değişkenlerini ayrı ayrı inceleyelim. Evren, araştırmanın sonuçlarını genellemek istediğimiz öğrenci topluluğudur.',
 'Metinde bazı liselerdeki öğrenciler denmiş. Hangi liseler, hangi bölge veya sınıf grubu olduğu açıklanmıyor. Bu yüzden evren açıkça tanımlanmıştır yargısını doğru kabul edemeyiz. Birinci yargı elenir.',
 'Telefon kullanımının ders çalışma süresi ve sınav kaygısıyla ilişkisini incelemek araştırmanın amacıdır. Bu amaç açıkça verilmiştir. İkinci yargı doğrudur.',
 'Telefon kullanım süresi, ders çalışma süresi ve sınav kaygısı da araştırılan değişkenlerdir. Sorularda bunları görebiliyoruz. Üçüncü yargı da doğrudur. İkinci ve üçüncü yargıyı birlikte veren C seçeneğini işaretliyoruz.'
],[('I: Evren belirsiz','Birinci yargı elenir'),('II: Amaç açık','İkinci yargı doğrudur'),('III: Değişkenler açık','Üçüncü yargı da doğrudur')],'C')
add('A-Turkce-01',[
 'Boşlukları doldururken üç sözcük grubunun cümlenin tamamına uyup uymadığını kontrol edeceğiz. Yalnız ilk boşluğa uygun sözcüğü bulmak yeterli değildir.',
 'Trafik denetiminin amacı ulaşım risklerini azaltmaktır. Bu yüzden ilk boşlukta azaltmak sözcüğü anlamı tamamlar.',
 'Fahri trafik müfettişi, sayılan resmi görevlilerin dışında görev alan kişidir. İkinci boşluğa dışında gelir. Son bölümde de kara yolu denetimine yardımcı olan kişidir deriz.',
 'Azaltmak, dışında, yardımcı olan. Bu üç ifade cümlenin hem anlamını hem dil bilgisini birlikte tamamlıyor. C seçeneğini işaretliyoruz.'
],[('Riskleri azaltmak','ulaşım risklerini azaltmaktır'),('Görevlilerin dışında','sayılan resmi görevlilerin dışında görev alan kişidir'),('Denetime yardımcı olan','kara yolu denetimine yardımcı olan kişidir')],'C')
add('A-Sosyal_Bilimler-01',[
 'Soru, verilen bilgilerden ulaşabileceğimiz sonuçları soruyor. Bildiğimiz her tarih bilgisini metne eklemek yerine, her yargının burada bir kanıtı olup olmadığına bakacağız.',
 'Sümerlerin yazıyı buldukları söyleniyor. Bu bilgi dünya uygarlığına katkı sağladıklarını gösterir. Birinci yargıya ulaşılır.',
 'Kent devletlerinin ayrı yöneticileri var ve bu kentler birbirleriyle mücadele ediyor. Dolayısıyla bütün ülkeyi tek merkezden yöneten bir siyasal birlik yok. Üçüncü yargıya da ulaşılır.',
 'Fakat coğrafi konumlarının istilaya açık olması hakkında metinde bilgi verilmemiş. İkinci yargıya bu metinden ulaşamayız. Birinci ve üçüncü yargıları birlikte veren D seçeneğini işaretliyoruz.'
],[('Yazı → I','yazıyı buldukları söyleniyor. Bu bilgi dünya uygarlığına katkı sağladıklarını gösterir. Birinci yargıya ulaşılır'),('Kent devletleri → III','bütün ülkeyi tek merkezden yöneten bir siyasal birlik yok. Üçüncü yargıya da ulaşılır'),('II: Metinde kanıt yok','İkinci yargıya bu metinden ulaşamayız')],'D')
add('A-Fen_Bilimleri-02',[
 'Alınan yol ile yer değiştirme aynı şey değildir. Kaplumbağa şeklin altından dolaşarak ka noktasından le noktasına ulaşıyor. Bu dolambaçlı yol, başlangıçla bitiş arasındaki doğrusal uzaklıktan daha uzundur. Birinci yargı doğrudur.',
 'Ortalama sürat, toplam yolun geçen süreye bölümüdür. Ortalama hızın büyüklüğü ise yer değiştirme büyüklüğünün aynı süreye bölümüdür. Paydalarda aynı pozitif süre bulunduğu için, ortalama sürat daha büyüktür. İkinci yargı da doğrudur.',
 'Yer değiştirme vektörünü, izlenen kıvrımlı yol boyunca çizmeyiz. Başlangıç olan ka noktasından bitiş olan le noktasına doğru tek bir ok çizeriz. Üçüncü yargı da doğrudur.',
 'Birinci, ikinci ve üçüncü yargıların hepsi doğru. E seçeneğini işaretliyoruz.'
],[('Yol > |KL|','Bu dolambaçlı yol, başlangıçla bitiş arasındaki doğrusal uzaklıktan daha uzundur'),('Yol/t > |KL|/t','Paydalarda aynı pozitif süre bulunduğu için, ortalama sürat daha büyüktür'),('Yer değiştirme: K → L','Başlangıç olan ka noktasından bitiş olan le noktasına doğru tek bir ok çizeriz')],'E')
state=json.loads((R.parent/'current_r12/Atolye_SBS_Cozumleri/calisma_durumu.json').read_text());index={q['soru_kimligi']:q for q in state['sorular']}
for q in items:
 meta=index[q['id']];q['pair']=[q['id'],meta['eslesen_soru']];q['narration']='\n\n'.join(q['segments']);q['metadata']=meta;q['partner_metadata']=index[meta['eslesen_soru']];q['source_pair_visual_review']=True;q['academic_review']=True
 if q['id']=='A-Temel_Matematik-07':
  q['metadata']['soru_kirpma_konumu_pt'][1]-=16;q['partner_metadata']['soru_kirpma_konumu_pt'][1]-=16
 assert not meta.get('ses_uretildi'),q['id']
(R/'batch01.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print([(x['id'],len(x['narration'])) for x in items]);print('total chars',sum(len(x['narration']) for x in items))
