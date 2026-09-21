import json,fitz
from pathlib import Path
p=Path(__file__).parent;items=json.loads((p/'batch02_prepared.json').read_text())
data={
'A-Temel_Matematik-12':([
'Akış şemasını adım adım izleyelim. Önce te değerini, iksin karesinden iks ile yenin çarpımını çıkararak buluyoruz. Te doksana eşit ya da büyükse işlem durur. Küçükse iks bir artar, ye bir azalır ve hesap tekrarlanır.',
'Başlangıçta iks üç, ye eksi dört. Üçün karesi dokuzdur. Üç ile eksi dördün çarpımı eksi on iki. Dokuzdan eksi on ikiyi çıkarınca yirmi bir buluruz. Doksandan küçük, devam.',
'İks dört ve ye eksi beş olunca on altı artı yirmi, otuz altı eder. İks beş ve ye eksi altıda yirmi beş artı otuz, elli beş eder. Her ikisi de doksandan küçük.',
'İks altı, ye eksi yedi için otuz altı artı kırk iki, yetmiş sekizdir. Henüz duramayız. İks yedi ve ye eksi sekize geçeriz. Kırk dokuz artı elli altı, yüz beş eder.',
'Yüz beş doksandan büyük olduğu için bu kez evet yolunu izleriz. Ekrana yüz beş yazılır. D seçeneğini işaretliyoruz.'
], [('3,−4 → 21','Dokuzdan eksi on ikiyi çıkarınca yirmi bir buluruz'),('4,−5 → 36','İks dört ve ye eksi beş olunca on altı artı yirmi, otuz altı eder'),('5,−6 → 55','İks beş ve ye eksi altıda yirmi beş artı otuz, elli beş eder'),('6,−7 → 78','İks altı, ye eksi yedi için otuz altı artı kırk iki, yetmiş sekizdir'),('7,−8 → 105 ≥ 90','İks yedi ve ye eksi sekize geçeriz. Kırk dokuz artı elli altı, yüz beş eder')]),
'A-Fen_Bilimleri-08':([
'Grafikte başlangıçta sıfır virgül bir mol iks bileşiği var. Tepkime sonunda iks tamamen tükenirken sıfır virgül üç mol karbondioksit ve sıfır virgül dört mol su oluşuyor.',
'Karbondioksitin her molekülünde bir karbon bulunur. Sıfır virgül üçü sıfır virgül bire bölersek, iks molekülü başına üç karbon atomu elde ederiz.',
'Suyun her molekülünde iki hidrojen vardır. İki çarpı sıfır virgül dört, bölü sıfır virgül bir, sekiz eder. Bileşiğimiz üç karbon ve sekiz hidrojen içerir. İkinci yargıdaki üç karbon dört hidrojen formülü yanlıştır.',
'Kimyasal tepkimelerde toplam kütle korunur; birinci yargı doğrudur. Grafik, yeterli oksijenle yakılan iksin tamamen tükendiğini gösterdiğinden sorunun ideal tepkime kabulünde tam verim vardır. Üçüncü yargı da doğrudur. Birinci ve üçüncüyü veren C seçeneğini işaretliyoruz.'
],[('C: 0,3/0,1=3','Sıfır virgül üçü sıfır virgül bire bölersek, iks molekülü başına üç karbon atomu elde ederiz'),('H: 2×0,4/0,1=8','İki çarpı sıfır virgül dört, bölü sıfır virgül bir, sekiz eder'),('X=C₃H₈','Bileşiğimiz üç karbon ve sekiz hidrojen içerir'),('I ve III','Birinci ve üçüncüyü veren C seçeneğini işaretliyoruz')]),
'A-Fen_Bilimleri-15':([
'Burada doğru ifadeleri değil, söylenemeyecek ifadeleri seçiyoruz. Hücresel canlılar prokaryot ya da ökaryot yapıdadır. Birinci ifade bu ayrımı doğru verir.',
'Ancak tek hücreli olmak, mutlaka prokaryot olmak demek değildir. Amip ve maya tek hücreli ökaryot örnekleridir. Bu örnekler, ikinci ifadedeki tümü sözünü geçersiz kılar.',
'Aynı örnekler üçüncü ifadeyi de çürütür. Ökaryotların hepsi çok hücreli olsaydı tek hücreli amip ve maya bulunamazdı. Ökaryotlarda hem tek hücreli hem çok hücreli canlılar vardır.',
'O halde ikinci ve üçüncü ifadeler söylenemez. D seçeneğini işaretliyoruz.'
],[('Amip, maya: ökaryot','Amip ve maya tek hücreli ökaryot örnekleridir'),('Tek hücreli de olabilir','Ökaryotlarda hem tek hücreli hem çok hücreli canlılar vardır'),('Söylenemez: II ve III','ikinci ve üçüncü ifadeler söylenemez')]),
'A-Sosyal_Bilimler-06':([
'Şekilde aynı dağın denize bakan yamacındaki bitki kuşaklarını görüyoruz. Deniz seviyesine yakın yerde geniş yapraklı ormanlar var. Yükseldikçe karma ormanlara, iğne yapraklı ormanlara ve en üstte dağ çayırlarına geçiliyor.',
'Burada karşılaştırılan yerlerin yüksekliği değişiyor. Yükseldikçe sıcaklık genel olarak azalır. Sıcaklık koşulları değişince bu koşullara uyum sağlayan bitkiler de değişir; kuşaklanma ortaya çıkar.',
'Şekil iki farklı yamacın güneşlenmesini ya da rüzgarların etkisini karşılaştırmıyor. Kara ile denizin ısınma hızını da göstermiyor. Doğrudan desteklediği bilgi, yükseldikçe sıcaklığın düşmesidir. B seçeneğini işaretliyoruz.'
],[('Yükselti artar','Burada karşılaştırılan yerlerin yüksekliği değişiyor'),('Sıcaklık azalır','Yükseldikçe sıcaklık genel olarak azalır'),('Bitki kuşakları değişir','Sıcaklık koşulları değişince bu koşullara uyum sağlayan bitkiler de değişir')]),
'A-Sosyal_Bilimler-11':([
'Parçada filozofun yaptığı iki ayrı iş anlatılıyor. Önce kendisine sunulan bilgi, deney, algı ve sezgi sonuçlarını inceliyor, yeniden düşünüyor ve analiz ediyor. Bu aşama çözümlemedir.',
'Sonra elindeki verilerden hareketle dünyayı yeniden oluşturuyor; bir birlik ve bütünlük kuruyor. Bu ikinci aşama yeniden kurucu olmayı anlatır.',
'İki aşamayı birlikte karşılayan ifade, filozofun çözümleyici ve yeniden kurucu olduğudur. Parçada yalnızca soyut düşünceye yönelme ya da bilimsel otoriteye uyumdan söz edilmiyor. C seçeneğini işaretliyoruz.'
],[('Analiz → çözümleme','yeniden düşünüyor ve analiz ediyor. Bu aşama çözümlemedir'),('Bütünlük → yeniden kurma','bir birlik ve bütünlük kuruyor. Bu ikinci aşama yeniden kurucu olmayı anlatır'),('Çözümleyici ve kurucu','filozofun çözümleyici ve yeniden kurucu olduğudur')]),
'A-Sosyal_Bilimler-16':([
'Ödevin konusu İslamda aile içi iletişim ve görevler. Soru, bu konuyla doğrudan ilgisi bulunmayan sözü soruyor. Bu nedenle seçeneklerin hangi ilişkiyi anlattığına bakalım.',
'Eşlerin karşılıklı hakları aile içi görevlerle ilgilidir. Çocuğa güzel terbiye verilmesi de ailedeki sorumlulukları anlatır. Bakmakla yükümlü olunan kişileri ihmal etmemek ve aileye iyi davranmak da aynı konunun içindedir.',
'A seçeneği ise genel olarak duanın kıymetini anlatıyor. Bu sözde aile içi iletişim veya aile üyelerinin görevleri doğrudan ele alınmıyor. Seçenekleri konuyla ilgileri bakımından karşılaştırınca A seçeneğini işaretliyoruz.'
],[('Konu: aile ve görevler','Ödevin konusu İslamda aile içi iletişim ve görevler'),('B,C,D,E: aileyle ilgili','aileye iyi davranmak da aynı konunun içindedir'),('A: Duanın kıymeti','A seçeneği ise genel olarak duanın kıymetini anlatıyor')]),
'A-Sosyal_Bilimler-21':([
'Bu soruda parçanın hangi siyaset felsefesi sorularına cevap verdiğini belirliyoruz. Metin, yönetimi tek kişinin, birkaç kişinin ya da çoğunluğun üstlenmesini karşılaştırıyor. Bu, devleti kimin yönetmesi gerektiği sorusuyla ilgilidir. İkinci maddeye ulaşırız.',
'Yönetimin iyi olması da hukuka bağlılık, bilgelik ve halkın çıkarlarını gözetme üzerinden açıklanıyor. Böylece en iyi yönetim şeklinin ne olduğu sorusuna da cevap aranıyor. Üçüncü madde de var.',
'Fakat parçada sivil toplumun anlamı tanımlanmıyor. Birinci maddeyi alamayız. İkinci ve üçüncü maddeleri birlikte veren E seçeneğini işaretliyoruz.'
],[('II: Kim yönetmeli','devleti kimin yönetmesi gerektiği sorusuyla ilgilidir'),('III: En iyi yönetim','en iyi yönetim şeklinin ne olduğu sorusuna da cevap aranıyor'),('I: Sivil toplum yok','parçada sivil toplumun anlamı tanımlanmıyor')]),
'A-Turkce-02':([
'Sözün anlamını bulunduğu bağlamla çözelim. Yazar yeni kitabının önceki romanını tekrar etmesini istemiyor; yeni ve farklı bir eser amaçlıyor. Ancak başlangıcı yapmakta zorlanıyor.',
'İğneye ipliği geçirmenin zor olması, burada yazma işine başlayıp ilk ilerlemeyi sağlamanın güçlüğünü anlatıyor. Hemen sonraki cümlede haftalar geçtiği halde ancak birkaç sayfa yazabildiğini söylüyor.',
'Demek ki hiç başlayamamış değil; güç de olsa birkaç sayfalık giriş yapmış. Özgün olma isteği metinde var ama sorulan sözün doğrudan anlamı bu değil. Kolay olmasa da yapıtına giriş yapabildiğini belirten E seçeneğini işaretliyoruz.'
],[('Başlangıç zor','Ancak başlangıcı yapmakta zorlanıyor'),('Haftalar → birkaç sayfa','haftalar geçtiği halde ancak birkaç sayfa yazabildiğini söylüyor'),('Güç de olsa giriş var','güç de olsa birkaç sayfalık giriş yapmış')])
}
for i in items:
 seg,notes=data[i['id']];i.update(segments=seg,narration='\n\n'.join(seg),notes=notes,source_pair_visual_review=True,academic_review=True,highlights=[])
 if i['id']=='A-Sosyal_Bilimler-21':
  i['answer']='E';i['academic_correction']='Eski çözüm gerekçesi II ve III olmasına rağmen D yazıyordu. Özgün A21/B23 seçeneklerinde II ve III E seçeneğidir; E olarak düzeltildi.'
  for key in ['metadata','partner_metadata']:
   m=i[key];m['dogru_secenek']='E';pg=fitz.open(Path('sources')/m['pdf_dosyasi'])[m['pdf_sayfasi']-1];m['answer_label_rects']=[list(w[:4]) for w in pg.get_text('words',clip=fitz.Rect(m['soru_kirpma_konumu_pt'])) if w[4]=='E)']
(p/'batch02.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));print('questions',len(items),'characters',sum(len(i['narration']) for i in items))
