import json,fitz
from pathlib import Path
p=Path(__file__).parent;items=json.loads((p/'batch03_prepared.json').read_text())
data={
'A-Temel_Matematik-13':([
'Akış şemasındaki toplam değişkeni sıfırdan başlıyor. Boş bırakılan yerde, toplama hangi sayıları hangi sırayla ekleyeceğimizi belirleyen döngü bulunmalı.',
'Soru, ikiden kırka kadar olan çift sayıların toplamını istiyor. İlk sayı iki, son sayı kırk. Bir çift sayıdan sonrakine geçerken iki ekleriz. Dolayısıyla döngünün başlangıcı iki, bitişi kırk, artış miktarı iki olmalıdır.',
'B seçeneğindeki döngü bu üç bilgiyi doğru verir. Birer artırsaydık araya tek sayılar da girerdi. Birden başlasaydık yine istenen çift sayı dizisini elde edemezdik.',
'Kontrol edelim: iki, dört, altı diye devam edip kırkta biten yirmi terim var. Toplamları, yirmi çarpı iki artı kırk, bölü iki; yani dört yüz yirmidir. B seçeneğini işaretliyoruz.'
],[('Başlangıç: 2','döngünün başlangıcı iki'),('Bitiş: 40; artış: 2','bitişi kırk, artış miktarı iki olmalıdır'),('i=2,40,2','B seçeneğindeki döngü bu üç bilgiyi doğru verir'),('20×(2+40)/2=420','yirmi çarpı iki artı kırk, bölü iki; yani dört yüz yirmidir')]),
'A-Temel_Matematik-14':([
'Döngü ikiyle başlıyor, yetmiş dörde kadar üçer artarak ilerliyor. İ değişkeninin aldığı ilk değerler iki, beş ve sekizdir. Her turda, bu sayının üçe bölümünden kalan iki mi diye bakılıyor.',
'İlk sayı ikinin kalanı iki. Üç eklemek kalanı değiştirmez. Bu yüzden döngüdeki bütün değerler koşulu sağlar. Sayaç her turda bir artar.',
'Kaç tur olduğunu bulalım. Son terimden ilk terimi çıkarıp artış miktarına böleriz: yetmiş dört eksi iki, bölü üç, yirmi dört eder. Bu sayı aralıkların sayısıdır. Başlangıç terimini de saymak için bir ekleriz.',
'Yirmi dört artı bir, yirmi beş. Sayaç sıfırdan başladığına göre ekrana yirmi beş yazılır. E seçeneğini işaretliyoruz.'
],[('2,5,8,...,74','İ değişkeninin aldığı ilk değerler iki, beş ve sekizdir'),('Her tur: kalan 2','döngüdeki bütün değerler koşulu sağlar'),('(74−2)/3=24','yetmiş dört eksi iki, bölü üç, yirmi dört eder'),('24+1=25','Yirmi dört artı bir, yirmi beş')]),
'A-Turkce-03':([
'Sözcük gruplarını yanlarındaki açıklamalarla karşılaştıralım. Özgün sözcüğü orijinal anlamında, ihtiras ise tutku anlamında kullanılmış. Bu iki eşleştirme uygundur.',
'Üçüncü gruptaki içten içe, duygu veya düşüncenin dışarıya belli edilmeden, gizlice yaşanmasını anlatır. İyiden iyiye ise iyice, oldukça veya bütünüyle anlamına gelir.',
'Birinde gizlilik, diğerinde derece ve yoğunluk anlatılıyor. Bu iki söz birbirinin açıklaması olamaz. Meta, mal anlamını; reaksiyon göstermek de tepki vermek anlamını karşılar. Uyuşmayan eşleştirme üçüncüdür. C seçeneğini işaretliyoruz.'
],[('İçten içe: gizlice','İçten içe, duygu veya düşüncenin dışarıya belli edilmeden, gizlice yaşanmasını anlatır'),('İyiden iyiye: iyice','İyiden iyiye ise iyice, oldukça veya bütünüyle anlamına gelir'),('Gizlilik ≠ derece','Birinde gizlilik, diğerinde derece ve yoğunluk anlatılıyor')]),
'A-Turkce-04':([
'Cümlede sanatın hangi işlevleri vurgulanıyor, onları ayıralım. Sanatın yalnız insanı avutup büyüleyen bir güç olarak görülmesine karşı çıkılıyor. İnsanı uyarması ve harekete geçirmesi öne çıkarılıyor.',
'Harekete geçirmek, eylem yönüdür. Ufkumuzu genişletmek ve yaşadıklarımıza daha anlamlı bakmamızı sağlamak ise düşünce yönünü anlatır. Yani sanatın hem düşünce hem eylem bakımından işlevi vardır.',
'A seçeneği zevk vermenin ötesinde düşünce ve eylem işlevlerini birlikte söylüyor. Diğer seçeneklerdeki evrensel dil, eserin değerini ölçme ya da yeni dünyaların kapısını açma anlatımları bu iki vurguyu birlikte karşılamıyor. A seçeneğini işaretliyoruz.'
],[('Harekete geçirme → eylem','Harekete geçirmek, eylem yönüdür'),('Ufku genişletme → düşünce','Ufkumuzu genişletmek ve yaşadıklarımıza daha anlamlı bakmamızı sağlamak ise düşünce yönünü anlatır'),('Düşünce + eylem','hem düşünce hem eylem bakımından işlevi vardır')]),
'A-Sosyal_Bilimler-02':([
'Sorudaki anahtar bilgi, geçmişte ve günümüzde konuşulan dillerin gelişiminin incelenmesi. Dillerin tarihini, yapısını ve gelişimini inceleyen, bu yolla tarihe yardımcı olan alan filolojidir.',
'Benzer görünen seçeneği ayıralım: paleografya eski yazıların biçimlerini inceler. Dilin gelişimi ile yazı biçimini birbirine karıştırmıyoruz. Kronoloji olayların zamanını ve sırasını; heraldik ise armaları ele alır.',
'Burada sorulan yazının şekli veya olayların tarihi değil, diller ve gelişimleridir. Bu nedenle filolojiyi veren E seçeneğini işaretliyoruz.'
],[('Dil ve gelişimi → filoloji','Dillerin tarihini, yapısını ve gelişimini inceleyen, bu yolla tarihe yardımcı olan alan filolojidir'),('Eski yazı → paleografya','paleografya eski yazıların biçimlerini inceler'),('Zaman → kronoloji','Kronoloji olayların zamanını ve sırasını')]),
'A-Sosyal_Bilimler-07':([
'Pasifik Ateş Çemberi, Büyük Okyanusu çevreleyen levha sınırları boyunca uzanır. Haritadaki yerlerin hangi okyanusun kenarında olduğuna bakalım.',
'Birinci yer Kuzey Amerikanın batı kıyısındadır. Bu kıyı Pasifik Okyanusuna bakar. Dördüncü yer de Pasifikin batı kenarındaki ada kuşağında bulunur. Her ikisi de Ateş Çemberi üzerindedir.',
'İkinci yer İzlanda çevresinde, Atlas Okyanusundadır. Üçüncü yer ise Akdeniz çevresindedir. Aktif volkan bulunması, bir yerin mutlaka Pasifik Ateş Çemberinde olması demek değildir.',
'Bu yüzden birinci ve dördüncü yerleri birlikte seçeriz. C seçeneğini işaretliyoruz.'
],[('I: Pasifik kıyısı','Birinci yer Kuzey Amerikanın batı kıyısındadır'),('IV: Pasifik ada kuşağı','Dördüncü yer de Pasifikin batı kenarındaki ada kuşağında bulunur'),('II: Atlas; III: Akdeniz','İkinci yer İzlanda çevresinde, Atlas Okyanusundadır. Üçüncü yer ise Akdeniz çevresindedir'),('I ve IV','birinci ve dördüncü yerleri birlikte seçeriz')]),
'A-Fen_Bilimleri-03':([
'Üç barometre aynı ortamda olduğu için aynı açık hava basıncını ölçüyor. Boruların üst kısmında boşluk var. Sıvı sütununun basıncı, sıvının özkütlesi, yerçekimi ivmesi ve sütun yüksekliğinin çarpımıdır.',
'Basınç ve yerçekimi aynı olduğuna göre özkütle ile yükseklik ters orantılıdır. Daha kısa bir sıvı sütunu aynı basıncı dengeliyorsa, o sıvının özkütlesi daha büyüktür.',
'Yükseklikleri sıralayalım. Be sütunu altmış dört santimetreyle en kısa. Ce sütunu seksen santimetre. A sütunu ise yüz on santimetreyle en uzun.',
'Özkütle sırası bunun tersidir: be, ce, a. Be sıvısının özkütlesi ceden, ceninki de a sıvısından büyüktür. A seçeneğini işaretliyoruz.'
],[('P=d×g×h','özkütlesi, yerçekimi ivmesi ve sütun yüksekliğinin çarpımıdır'),('hB < hC < hA','Be sütunu altmış dört santimetreyle en kısa. Ce sütunu seksen santimetre. A sütunu ise yüz on santimetreyle en uzun'),('dB > dC > dA','Be sıvısının özkütlesi ceden, ceninki de a sıvısından büyüktür')]),
'A-Fen_Bilimleri-09':([
'Üç kapta da aynı tuzun sulu çözeltisi var. Aynı koşullarda kaynama sıcaklıkları eşit olduğuna göre çözeltilerin bileşim derişimleri aynıdır. Aynı tuz söz konusu olduğu için iyon derişimleri de eşittir. Birinci yargı doğrudur.',
'Üçüncü kapta yarım mol tuz, yarım litre çözeltide bulunuyor. Litre başına bir mol düşer. Birinci kaptaki bir mol tuz için bir litre, ikinci kaptaki iki mol için iki litre çözelti gerekir. Yani iks bin, ye iki bin mililitredir. İkinci yargı da doğrudur.',
'Her kaba bir litre su eklemek, hacimleri aynı oranda artırmaz. Sorunun hacimleri toplama kabulüyle yeni hacimler iki litre, üç litre ve bir buçuk litre olur. Yalnız ilk kabın hacmi iki katına çıkar; üç çözeltinin birden derişimi yarıya inmez.',
'Üçüncü yargı yanlış. Birinci ve ikinci yargıları birlikte veren B seçeneğini işaretliyoruz.'
],[('Aynı tuz, aynı derişim','çözeltilerin bileşim derişimleri aynıdır'),('0,5/0,5=1 mol/L','Üçüncü kapta yarım mol tuz, yarım litre çözeltide bulunuyor. Litre başına bir mol düşer'),('x=1000; y=2000 mL','iks bin, ye iki bin mililitredir'),('Yeni hacim: 2;3;1,5 L','yeni hacimler iki litre, üç litre ve bir buçuk litre olur')])
}
for i in items:
 seg,notes=data[i['id']];i.update(segments=seg,narration='\n\n'.join(seg),notes=notes,source_pair_visual_review=True,academic_review=True,highlights=[])
 if i['id']=='A-Temel_Matematik-13':
  for key in ['metadata','partner_metadata']:
   m=i[key];pg=fitz.open(Path('sources')/m['pdf_dosyasi'])[m['pdf_sayfasi']-1];r=fitz.Rect(m['soru_kirpma_konumu_pt']);elabels=[w for w in pg.get_text('words',clip=r) if w[4]=='E)'];r.y1=min(r.y1,min(w[3] for w in elabels)+28);m['soru_kirpma_konumu_pt']=list(r);pg.get_pixmap(clip=r,matrix=fitz.Matrix(3.2,3.2)).save(p/(m['soru_kimligi']+'.png'))
 if i['id']=='A-Turkce-03':i['source_typo_note']='Kaynakta son sözcük grubu V yerine ikinci kez IV basılmış. Üçüncü grup ve doğru C seçeneği açık; özgün görüntü korunur.'
(p/'batch03.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));print('questions',len(items),'characters',sum(len(i['narration']) for i in items))
