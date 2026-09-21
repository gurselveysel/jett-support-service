import json
from pathlib import Path
p=Path(__file__).parent;items=json.loads((p/'batch04_prepared.json').read_text())
data={
'A-Temel_Matematik-15':([
'Kutu grafiğini soldan sağa okuyalım. En küçük değer altı. Kutunun sol kenarı alt çeyrek dokuz, içindeki çizgi ortanca on yedi. Kutunun sağ kenarı üst çeyrek yirmi iki, en büyük değer yirmi dokuzdur.',
'Açıklık, en büyük değerle en küçük değerin farkıdır. Yirmi dokuz eksi altı, yirmi üç eder. D seçeneğinde açıklığın on altı olduğu yazılmış; bu yanlıştır.',
'Çeyrekler açıklığını da kontrol edelim: üst çeyrek eksi alt çeyrek, yani yirmi iki eksi dokuz, on üçtür. Diğer seçenekler grafiğe uyuyor. Yanlış ifade sorulduğu için D seçeneğini işaretliyoruz.'
],[('Alt:9; ortanca:17; üst:22','Kutunun sol kenarı alt çeyrek dokuz, içindeki çizgi ortanca on yedi. Kutunun sağ kenarı üst çeyrek yirmi iki'),('Açıklık=29−6=23','Yirmi dokuz eksi altı, yirmi üç eder'),('Çeyrekler açıklığı=22−9=13','yirmi iki eksi dokuz, on üçtür')]),
'A-Temel_Matematik-16':([
'Grafikte iki yaşında beş, üç yaşında altı, dört yaşında altı ve beş yaşında üç çocuk var. Toplam yirmi çocuk ediyor. Yaşları küçükten büyüğe sıraladığımızı düşünelim.',
'İlk beş sırada iki yaşındakiler var. Altıncı sıradan on birinci sıraya kadar üç yaşındakiler, on ikinci sıradan on yedinci sıraya kadar dört yaşındakiler gelir. Son üç sırada beş yaşındakiler bulunur.',
'Alt çeyrek için alt yarıdaki on verinin ortancasını alırız. Beşinci değer iki, altıncı değer üç. İkiyle üçü toplayıp ikiye böleriz, iki buçuk buluruz.',
'Üst yarının ortasındaki on beşinci ve on altıncı değerlerin ikisi de dört. Üst çeyrek dört olur. Çeyrekler açıklığı dört eksi iki buçuk, bir buçuktur. D seçeneğini işaretliyoruz.'
],[('n=5+6+6+3=20','Toplam yirmi çocuk ediyor'),('Alt çeyrek=(2+3)/2=2,5','Beşinci değer iki, altıncı değer üç. İkiyle üçü toplayıp ikiye böleriz, iki buçuk buluruz'),('Üst çeyrek=(4+4)/2=4','on beşinci ve on altıncı değerlerin ikisi de dört. Üst çeyrek dört olur'),('4−2,5=1,5','Çeyrekler açıklığı dört eksi iki buçuk, bir buçuktur')]),
'A-Temel_Matematik-18':([
'Önce ortadaki eğik parçayı inceleyelim. Bu doğru, eksi üçe beş ve üçe eksi beş noktalarından geçiyor. Eğimi, ye değerlerindeki farkın iks değerlerindeki farka bölümüdür.',
'Eksi beş eksi beş, bölü üç eksi eksi üç; eksi on bölü altı, yani eksi beş bölü üç eder. Doğru başlangıç noktasından da geçtiği için bu parçada fonksiyon eksi beş iks bölü üçtür. Birinci yargıdaki eksi üç iks bölü beş doğru değildir.',
'Beş ile yedi arasında grafik sağa giderken yükseliyor; ikinci yargı doğrudur. Eksi üç ve solundaki gösterilen parça yataydır; fonksiyonun değeri beş olarak sabittir. Üçüncü yargı da doğrudur. İkinci ve üçüncüyü veren D seçeneğini işaretliyoruz.'
],[('Eğim=(−5−5)/(3+3)=−5/3','Eksi beş eksi beş, bölü üç eksi eksi üç; eksi on bölü altı, yani eksi beş bölü üç eder'),('I: f(x)=−5x/3','bu parçada fonksiyon eksi beş iks bölü üçtür'),('II: [5,7] artan','Beş ile yedi arasında grafik sağa giderken yükseliyor'),('III: x≤−3 için sabit','Eksi üç ve solundaki gösterilen parça yataydır')]),
'A-Temel_Matematik-19':([
'Fonksiyonu önce tepe noktası biçiminde yazalım. İki iks kare eksi sekiz iks artı on bir, iki çarpı iks eksi ikinin karesi artı üçtür. Tepe noktası ikiye üçtür.',
'Grafiği üç birim sağa ve üç birim aşağı taşıyınca tepe noktası beşe sıfıra gelir. Yeni fonksiyon iki çarpı iks eksi beşin karesidir. Açarsak iki iks kare eksi yirmi iks artı elli elde ederiz.',
'Kare sıfır olduğunda iks beş olur; birinci yargı doğrudur. Katsayılar toplamını bulmak için iks yerine bir yazabiliriz. İki çarpı bir eksi beşin karesi, otuz iki eder. İkinci yargı da doğru.',
'Kareli terimin katsayısı pozitif olduğu için parabola yukarı açılır. Tepe noktasının sağında, yani beşten itibaren artandır. Üçüncü yargı da doğru. E seçeneğini işaretliyoruz.'
],[('f(x)=2(x−2)²+3','iki çarpı iks eksi ikinin karesi artı üçtür'),('g(x)=2(x−5)²','Yeni fonksiyon iki çarpı iks eksi beşin karesidir'),('Kök: 5','Kare sıfır olduğunda iks beş olur'),('g(1)=2(1−5)²=32','İki çarpı bir eksi beşin karesi, otuz iki eder'),('x≥5 için artan','Tepe noktasının sağında, yani beşten itibaren artandır')]),
'A-Temel_Matematik-20':([
'Fonksiyonun A kümesindeki değerleri sekizde bir ile üçte bir arasında. Bir bölü iks eksi iki pozitif olduğuna göre payda pozitiftir; iks ikiden büyüktür.',
'Pozitif sayılarda tersini alırken sıralama yönü değişir. Bir bölü iks eksi ikinin sekizde bir ile üçte bir arasında olması, iks eksi ikinin üç ile sekiz arasında olması demektir.',
'Her tarafa iki eklersek iks beş ile on arasında kalır, sınırlar dahil. A kümesindeki tam sayılar beş, altı, yedi, sekiz, dokuz ve ondur.',
'Bu altı sayıyı toplayalım: beş ile on, altı ile dokuz ve yedi ile sekiz çiftlerinin her biri on beş eder. Üç çarpı on beş, kırk beş. C seçeneğini işaretliyoruz.'
],[('x>2','iks ikiden büyüktür'),('3 ≤ x−2 ≤ 8','iks eksi ikinin üç ile sekiz arasında olması demektir'),('5 ≤ x ≤ 10','iks beş ile on arasında kalır, sınırlar dahil'),('5+6+7+8+9+10=45','Üç çarpı on beş, kırk beş')]),
'A-Temel_Matematik-21':([
'Grafikte eğrinin yaklaştığı düşey doğru iks eşittir eksi üç. Seçeneklerde paydanın sıfır olduğu değer bu düşey asimptotu vermeli. Dolayısıyla paydası iks artı üç olan seçeneklere bakarız.',
'Şimdi ye eksenini kestiği noktayı kullanalım. İks sıfırken fonksiyonun değeri bir. Fonksiyonu ka bölü iks artı üç biçiminde yazarsak, sıfırda ka bölü üç eşittir bir olur. Buradan ka üç çıkar.',
'Fonksiyon üç bölü iks artı üçtür. İks eksi üçten büyükken pozitif, küçükken negatiftir; iki kolun konumu da grafikle uyuşur. D seçeneğini işaretliyoruz.'
],[('Asimptot: x=−3','düşey doğru iks eşittir eksi üç'),('f(x)=k/(x+3)','Fonksiyonu ka bölü iks artı üç biçiminde yazarsak'),('k/3=1 → k=3','ka bölü üç eşittir bir olur. Buradan ka üç çıkar'),('f(x)=3/(x+3)','Fonksiyon üç bölü iks artı üçtür')]),
'A-Turkce-05':([
'İki cümle arasındaki düşünce ilişkisine bakalım. İlk cümle, hayallerin yaşama amaç ve anlam kattığını söylüyor. Hayalsiz bir yaşamın geride anlamlı bir şey bırakmayacağı savunuluyor.',
'İkinci cümlede ise Addison adıyla aktarılan söz kullanılıyor. Bu sözde de gerçekleştirilecek bir düşe sahip olmanın önemi vurgulanıyor. Böylece ilk cümlenin düşüncesi destekleniyor.',
'Bir düşünceyi tanınmış bir kişinin sözüyle destekleme yöntemine tanık gösterme denir. Burada düşünceler çatışmıyor ve yaşanmış bir olay örneklenmiyor. Tanık göstermeyi belirten A seçeneğini işaretliyoruz.'
],[('İlk düşünce: hayallerin önemi','İlk cümle, hayallerin yaşama amaç ve anlam kattığını söylüyor'),('Aktarılan sözle destek','Böylece ilk cümlenin düşüncesi destekleniyor'),('Tanık gösterme','Bir düşünceyi tanınmış bir kişinin sözüyle destekleme yöntemine tanık gösterme denir')]),
'A-Turkce-06':([
'Bu soruyu, metnin anlattığı örneğin verdiği mesaja göre çözüyoruz. Metinde satış sorunu otomobilin biçimi ya da fiyatıyla değil, ürün adının hedef ülkedeki dilsel çağrışımıyla açıklanıyor.',
'Burada çıkarılmak istenen ilke, bir ürünü başka ülkede pazarlarken o ülkenin dilini ve kültürel özelliklerini dikkate almaktır. Aynı ad farklı bir dilde farklı bir anlam çağrıştırabilir.',
'Sorun metinde yazım yanlışı, ürünün üstün niteliği veya satış miktarını tahmin etme olarak sunulmuyor. Ürünün pazarlanacağı ülkenin kültürel özelliklerini belirten E seçeneğini işaretliyoruz.'
],[('Hedef ülke: dil ve kültür','o ülkenin dilini ve kültürel özelliklerini dikkate almaktır'),('Ürün adının çağrışımı','Aynı ad farklı bir dilde farklı bir anlam çağrıştırabilir'),('Kültürel özellikler','Ürünün pazarlanacağı ülkenin kültürel özelliklerini belirten E seçeneğini işaretliyoruz')]),
'A-Turkce-07':([
'Deyimlerin açıklamalarını karşılaştırıyoruz. Parası çıkışmamak, bir kişinin parasının ihtiyaçlarını karşılamaya yetmemesidir. Parasını harcamamayı kendi isteğiyle seçmesi anlamına gelmez.',
'İkinci deyimin açıklamasında gereken yerde para harcamaktan kaçınmak denmiş. Bu, yetersizlik yerine isteyerek kaçınmayı anlatıyor. Dolayısıyla açıklama deyimle uyuşmuyor.',
'Bir dediğini iki etmemek isteneni hemen yerine getirmek, ipe un sermek bahanelerle işten kaçınmak, gün saymak beklemek ve dert yanmak yakınmaktır. Yanlış açıklanan ikinci deyimi veren B seçeneğini işaretliyoruz.'
],[('Parası çıkışmamak: yetmemek','Parası çıkışmamak, bir kişinin parasının ihtiyaçlarını karşılamaya yetmemesidir'),('İsteyerek kaçınmak değil','Parasını harcamamayı kendi isteğiyle seçmesi anlamına gelmez'),('Yanlış açıklama: II','Yanlış açıklanan ikinci deyimi veren B seçeneğini işaretliyoruz')]),
'A-Turkce-08':([
'Kesin çıkarım sorularında, yalnız cümlede verilen bilgiye dayanırız. Metin batılılaşma hareketinin başlangıcını on sekizinci yüzyıla götürüyor.',
'Başlangıç birkaç yüzyıl öncesine uzandığına göre bu hareketin birkaç asırlık geçmişi vardır. D seçeneği, verilen zamanı doğrudan karşılıyor.',
'Cümlede hangi askeri yeniliklerin yapıldığı veya bu yönelişin Cumhuriyetin kuruluşuna nasıl etki ettiği açıklanmıyor. Bunlar için ek bilgi gerekir. Kesin olarak çıkarılabilen yargıyı veren D seçeneğini işaretliyoruz.'
],[('Başlangıç: 18. yüzyıl','Metin batılılaşma hareketinin başlangıcını on sekizinci yüzyıla götürüyor'),('Birkaç asırlık geçmiş','bu hareketin birkaç asırlık geçmişi vardır'),('Yalnız verilen bilgi','Bunlar için ek bilgi gerekir')]),
'A-Sosyal_Bilimler-03':([
'Sorudaki iki belirleyici ipucu zaman ve yer. Zaman beşinci yüzyıl; yer Büyük Macar Ovası, yani Orta Avrupa. Türkistandan batıya doğru gerçekleşen göçün bu bölgeye ulaşması soruluyor.',
'Bu zaman ve coğrafyada seçenekler içinde Avrupa Hunları öne çıkar. Hunlar, Orta Avrupadaki varlıklarıyla bu iki ipucuna birlikte uyar.',
'Yalnız Türkistan bağlantısına bakmak yeterli değil; topluluğun hangi dönemde nerede bulunduğunu da eşleştirmeliyiz. Hunları veren A seçeneğini işaretliyoruz.'
],[('Zaman: 5. yüzyıl','Zaman beşinci yüzyıl'),('Yer: Büyük Macar Ovası','yer Büyük Macar Ovası, yani Orta Avrupa'),('Avrupa Hunları','Bu zaman ve coğrafyada seçenekler içinde Avrupa Hunları öne çıkar')]),
'A-Sosyal_Bilimler-04':([
'Elçinin vurguladığı nokta, devletin yüksek görevlerine gelen kişilerin soylu ailelerden gelmemesidir. Sıradan insanların yetiştirilip askeri ve idari görevlere getirilebildiğini anlatıyor.',
'Seçenekler içinde insanları yetiştirerek devlet hizmetine kazandıran düzen devşirme sistemidir. Metindeki yetiştirme ve görev verme vurgusu bu sistemi işaret eder.',
'Veraset, hükümdarlığın geçişiyle; lonca esnaf örgütlenmesiyle ilgilidir. İkta toprak gelirlerine, vakıf ise belirli bir hizmete ayrılan mal ve gelire ilişkindir. Metnin vurgusuna uyan C seçeneğini işaretliyoruz.'
],[('Soyluluk şartı yok','devletin yüksek görevlerine gelen kişilerin soylu ailelerden gelmemesidir'),('Yetiştirme → devlet hizmeti','Sıradan insanların yetiştirilip askeri ve idari görevlere getirilebildiğini anlatıyor'),('Devşirme','insanları yetiştirerek devlet hizmetine kazandıran düzen devşirme sistemidir')]),
'A-Sosyal_Bilimler-05':([
'Tahrir işleminin metinde verilen işlevlerini izleyelim. Nüfus, toprak ve gelir kaynakları sayılarak kayıt altına alınıyor. Böylece vergiler ve toprak gelirlerinin dağıtımı düzenlenebiliyor.',
'Bu kayıtlar dirlik sisteminin işleyişine, gelir kaynaklarının yönetimine ve ekonomik düzenlemelere yardımcı olur. A, C, D ve E seçenekleri bu mali ve ekonomik işlemlerle bağlantılıdır.',
'Taht mücadeleleri ise hanedan içindeki hükümdarlık ve veraset meselesidir. Tahririn anlatılan işlevlerinden, taht mücadelelerini önlediği sonucu çıkarılamaz. Savunulamayacak yargıyı veren B seçeneğini işaretliyoruz.'
],[('Tahrir: nüfus, toprak, gelir','Nüfus, toprak ve gelir kaynakları sayılarak kayıt altına alınıyor'),('Vergi ve dirlik düzeni','vergiler ve toprak gelirlerinin dağıtımı düzenlenebiliyor'),('Taht mücadelesi: bağlantı yok','taht mücadelelerini önlediği sonucu çıkarılamaz')]),
'A-Sosyal_Bilimler-08':([
'Grafikte mavi sütunlar yağışı, pembe çizgi sıcaklığı gösteriyor. Sıcaklık için sağdaki derece ölçeğini okumalıyız.',
'En soğuk ay yaklaşık on derece. Diğer aylar on derecenin üstüne çıkıyor; yaz ortasında yirmi beş derecenin de üzerinde. Bütün ayların ortalaması bu durumda on dereceden büyük olur.',
'Yağışlar yaz aylarında yoğunlaşmış ve yıl içine eşit dağılmamış. En sıcak dönem yılın ortasına geldiği için Güney Yarım Küre ifadesi de grafiğe uymaz. Yıllık yağış miktarı aylık sütunların toplamıyla değerlendirilir, tek bir ayla değil.',
'Doğrudan ulaşabildiğimiz yargı, yıllık sıcaklık ortalamasının on derecenin üzerinde olmasıdır. E seçeneğini işaretliyoruz.'
],[('En düşük sıcaklık: 10','En soğuk ay yaklaşık on derece'),('Diğer aylar >10','Diğer aylar on derecenin üstüne çıkıyor'),('Yıllık ortalama >10','Bütün ayların ortalaması bu durumda on dereceden büyük olur')]),
'A-Fen_Bilimleri-04':([
'Sürtünme önemsiz olduğu için hareket boyunca mekanik enerji korunur. Ka noktasından le noktasına inerken yükseklik azalır. Yerçekimi potansiyel enerjisi azalırken kinetik enerji artar. Birinci yargı doğrudur.',
'Le noktasından em noktasına çıkarken bu dönüşüm tersine döner: kinetik enerji azalır, potansiyel enerji artar. Ancak ikisinin toplamı olan mekanik enerji azalmaz. İkinci yargı yanlıştır.',
'Ka ile le arasında yerçekimi kuvveti hareket yönünde iş yapar. Potansiyel enerjideki azalma kinetik enerjiye aktarılır; üçüncü yargı da doğrudur. Birinci ve üçüncü yargıları veren D seçeneğini işaretliyoruz.'
],[('K → L: kinetik artar','Yerçekimi potansiyel enerjisi azalırken kinetik enerji artar'),('Mekanik enerji sabit','ikisinin toplamı olan mekanik enerji azalmaz'),('Yerçekimi pozitif iş yapar','Ka ile le arasında yerçekimi kuvveti hareket yönünde iş yapar'),('I ve III','Birinci ve üçüncü yargıları veren D seçeneğini işaretliyoruz')]),
'A-Fen_Bilimleri-05':([
'Sürtünmesiz düşey atışta, cismin çıkabildiği en büyük yükseklik ilk hızın karesinin iki çarpı yerçekimi ivmesine bölümüdür. Bu bağıntıda kütle yer almaz.',
'Bu nedenle yalnız kütleyi azaltmak yüksekliği artırmaz. Birinci değişiklik işe yaramaz. İlk hızı artırırsak paydaki hızın karesi artar ve cisim daha yükseğe çıkar. İkinci değişiklik uygundur.',
'Yerçekimi ivmesini azaltırsak payda küçülür, yükseklik büyür. Üçüncü değişiklik de uygundur. Yüksekliği artıran ikinci ve üçüncü işlemleri birlikte veren D seçeneğini işaretliyoruz.'
],[('h=v₀²/(2g)','ilk hızın karesinin iki çarpı yerçekimi ivmesine bölümüdür'),('Kütle etkisiz','Bu bağıntıda kütle yer almaz'),('İlk hız artar → h artar','İlk hızı artırırsak paydaki hızın karesi artar ve cisim daha yükseğe çıkar'),('g azalır → h artar','Yerçekimi ivmesini azaltırsak payda küçülür, yükseklik büyür')])
}
for i in items:
 seg,notes=data[i['id']];i.update(segments=seg,narration='\n\n'.join(seg),notes=notes,source_pair_visual_review=True,academic_review=True,highlights=[])
 if i['id']=='A-Turkce-06':i['academic_note']='Anlatı gerçek pazarlama tarihi kanıtı olarak sunulmaz; yalnız parçanın iletisi çözümlenir.'
(p/'batch04.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));print('questions',len(items),'characters',sum(len(i['narration']) for i in items))
