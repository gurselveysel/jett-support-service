from pathlib import Path
import json,fitz,sys
from PIL import Image
ROOT=Path(__file__).resolve().parent
num=int(sys.argv[1]);ids=sys.argv[2:]
s=json.loads((ROOT/'calisma_durumu.json').read_text());qs=[]
for ident in ids:
 q=next(x.copy() for x in s['sorular'] if x['soru_kimligi']==ident);b=next(x.copy() for x in s['sorular'] if x['soru_kimligi']==q['eslesen_soru']);images=[]
 assert not any(x['soru_kimligi']==ident for x in s['video_teslim_manifesti'])
 for m in [q,b]:
  r=fitz.Rect(m['soru_kirpma_konumu_pt']);r.x1+=7;r.y0-=5;m['soru_kirpma_konumu_pt']=list(r)
  pg=fitz.open(ROOT.parent/'sources'/m['pdf_dosyasi'])[m['pdf_sayfasi']-1];pg.get_pixmap(clip=r,matrix=fitz.Matrix(3.2,3.2)).save(ROOT/(m['soru_kimligi']+'.png'));images.append(Image.open(ROOT/(m['soru_kimligi']+'.png')))
  m['answer_label_rects']=[list(w[:4]) for w in pg.get_text('words',clip=r) if q['dogru_secenek'] and w[4]==q['dogru_secenek']+')']
 sheet=Image.new('RGB',(sum(x.width for x in images),max(x.height for x in images)),'#ddd');sheet.paste(images[0],(0,0));sheet.paste(images[1],(images[0].width,0));sheet.save(ROOT/(ident+f'_pair{num:02d}.jpg'))
 sol=json.loads((ROOT.parent/'current_r12/original_package/Atolye_Teslim'/q['klasor']/'cozum.json').read_text());print(ident,json.dumps({k:sol[k] for k in ['dogru_secenek','gerekceli_cozum','tahta_adimlari','akademik_durum']},ensure_ascii=False))
 qs.append(dict(id=ident,metadata=q,partner_metadata=b,pair=[ident,b['soru_kimligi']],answer=q['dogru_secenek'],original_solution=sol))
(ROOT/f'batch{num:02d}_prepared.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2))
