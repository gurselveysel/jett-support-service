"""Create source-faithful frames and actual-provider-timed centerline strokes."""
from pathlib import Path
import json,sys,hashlib,shutil,math,re,unicodedata
import fitz,numpy as np
import io,os
from PIL import Image,ImageDraw,ImageFont
from glyphs import G,paths
ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
NAVY='#0b3d59';INK='#184e69'
def ft(n):return ImageFont.truetype(FONT,n)
def save_image(im,path):
 buf=io.BytesIO();im.save(buf,format='PNG');tmp=path.with_suffix('.pending.png')
 with tmp.open('wb') as f:f.write(buf.getvalue());f.flush();os.fsync(f.fileno())
 tmp.replace(path)
 Image.open(path).load()

def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower().replace('ı','i')) if c.isalnum())
class Timing:
 def __init__(self,folder):
  raw=json.loads((folder/'alignment.json').read_text());a=raw.get('normalized_alignment') or raw['alignment'];self.a=a
  self.text=''.join(a['characters']);self.norm='';self.index=[]
  for i,c in enumerate(self.text):
   nc=norm(c);self.norm+=nc;self.index.extend([i]*len(nc))
 def cue(self,text,last=False):
  n=norm(text);i=self.norm.rfind(n) if last else self.norm.find(n)
  assert i>=0,('provider cue missing',text)
  l=self.index[i];r=self.index[i+len(n)-1]
  return float(self.a['character_start_times_seconds'][l]),float(self.a['character_end_times_seconds'][r])
def write_json(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2))
def build(item,batch='batch01'):
 ident=item['id'];num=int(batch[-2:]);q=ROOT/f'Atolye_R12_Grup{num:02d}'/item['metadata']['klasor'];q.mkdir(parents=True,exist_ok=True)
 for name in ['speech.mp3','alignment.json','speech.json','report.json','narration.txt']:
  shutil.copy2(ROOT/f'audio{num:02d}'/ident/name,q/name)
 timing=Timing(q);report=json.loads((q/'report.json').read_text());ad=report['duration_seconds'];duration=math.ceil((ad+5.2)*30)/30;switch=ad+.6
 images={};transforms={};endbottom=[]
 for b,m in [('A',item['metadata']),('B',item['partner_metadata'])]:
  src=Image.open(ROOT/(m['soru_kimligi']+'.png')).convert('RGB');src.save(q/f'kaynak_{b}.png')
  maxh=995;w=min(940,round(maxh*src.width/src.height));h=round(src.height*w/src.width);x=(1080-w)//2;y=385
  transforms[b]=(x,y,w/(m['soru_kirpma_konumu_pt'][2]-m['soru_kirpma_konumu_pt'][0]))
  endbottom.append(y+h)
  im=Image.new('RGB',(1080,1920),NAVY);d=ImageDraw.Draw(im)
  logo=Image.open(ROOT/'atolye_logo.png').convert('RGB');logo.thumbnail((350,268));im.paste(logo,(45,20))
  d.text((445,55),'SBS • VİDEO ÇÖZÜM',font=ft(25),fill='#d7e7ed')
  subject=item['metadata']['ders']; subject='Din Kültürü' if subject=='Din Kültürü ve Ahlak Bilgisi' else subject
  d.text((445,108),subject,font=ft(31),fill='white')
  a=item['metadata']['basili_soru_numarasi'];bn=item['partner_metadata']['basili_soru_numarasi']
  d.text((445,165),f'A {a:02d}  ↔  B {bn:02d}',font=ft(37),fill='white')
  d.text((445,225),'125 benzersiz soru',font=ft(22),fill='#d7e7ed')
  d.rounded_rectangle((36,310,1044,1783),20,fill='white')
  label=f'{b} KİTAPÇIĞI • Soru {m["basili_soru_numarasi"]} • PDF sayfa {m["pdf_sayfasi"]}'
  if b=='B':label='EŞLEŞEN '+label
  d.text((70,333),label,font=ft(24),fill=NAVY)
  im.paste(src.resize((w,h),Image.Resampling.LANCZOS),(x,y))
  d.rectangle((0,1810,1080,1920),fill='white')
  uz=Image.open(ROOT/'uzemgo_logo.png').convert('RGBA');uz.thumbnail((285,91));im.paste(uz,((1080-uz.width)//2,1819),uz)
  images[b]=im
 top=max(endbottom)+65;bottom=1680;n=len(item['notes']);rowgap=min(139,(bottom-top)/(max(1,n-1)));size=min(53,rowgap/1.55)
 assert size>=30,(ident,top,rowgap,size)
 for im in images.values():
  d=ImageDraw.Draw(im);d.line((92,top-31,988,top-31),fill='#d5dfe3',width=1)
 for b,im in images.items():save_image(im,q/f'background_{b}.png')
 strokes=[];bindings=[]
 def addpath(pp,s,e,label,color=INK,width=3.1,**kwargs):
  lengths=[float(np.linalg.norm(np.diff(np.array(p),axis=0),axis=1).sum()) for p in pp];tot=sum(lengths);cur=0
  for p,L in zip(pp,lengths):
   a=s+(e-s)*cur/tot;cur+=L;b=s+(e-s)*cur/tot
   strokes.append(dict(points=p,start=a,end=max(a+.006,b),label=label,width=width,color=color,fade_at=999,**kwargs))
 def ink(txt,x,y,s,e,label,fs=size):
  pp,nx=paths(txt,x,y,fs);addpath(pp,s,e,label)
  return nx
 # Every note uses the actual char-alignment interval of a named spoken phrase.
 # Within each short phrase, the pen follows sequential centerline arc length.
 for k,(written,spoken) in enumerate(item['notes']):
  s,e=timing.cue(spoken);fs=min(size,880/sum(G[c][0]+.1 for c in written));x=105;y=top+k*rowgap
  ink(written,x,y,s,e,'note'+str(k),fs)
  bindings.append(dict(written=written,spoken=spoken,start=s,end=e,source='ElevenLabs normalized character alignment'))
 # Source underlines: only actually printed text, in the currently displayed A source.
 m=item['metadata'];doc=fitz.open(ROOT.parent/'sources'/m['pdf_dosyasi']);pg=doc[m['pdf_sayfasi']-1];clip=fitz.Rect(m['soru_kirpma_konumu_pt']);x,y,scale=transforms['A']
 def xy(px,py):return [x+(px-clip.x0)*scale,y+(py-clip.y0)*scale]
 for target,cue in item.get('highlights',[]):
  rects=[r for r in pg.search_for(target,clip=clip) if r.width>0]
  s,e=timing.cue(cue)
  for r in rects:addpath([[xy(r.x0,r.y1+1),xy(r.x1,r.y1+1)]],s,min(e,s+.8),'source_'+target,color='#b66432',width=2.5,until=switch)
 # Correct option is circled at its original printed label, independently for A and B.
 ans=item['answer'];s,e=timing.cue(ans+' seçeneğini',last=True)
 for b,m in [('A',item['metadata']),('B',item['partner_metadata'])]:
  r=m['answer_label_rects'];assert len(r)==1,(ident,b,r);r=r[0];x,y,scale=transforms[b];clip=fitz.Rect(m['soru_kirpma_konumu_pt'])
  cx=x+((r[0]+r[2])/2-clip.x0)*scale;cy=y+((r[1]+r[3])/2-clip.y0)*scale
  rx=max(24,(r[2]-r[0])*scale*.8);ry=max(25,(r[3]-r[1])*scale*.75)
  pp=[[[cx+rx*math.cos(t),cy+ry*math.sin(t)] for t in np.linspace(-.5,math.tau-.3,70)]]
  addpath(pp,s if b=='A' else switch+.05,min(e,s+1.2) if b=='A' else switch+1.0,'original_option_'+b,color='#bc572c',width=3.3,until=switch if b=='A' else duration)
 # Physics direction arrow drawn directly on the original diagram.
 if ident=='A-Fen_Bilimleri-02':
  m=item['metadata'];clip=fitz.Rect(m['soru_kirpma_konumu_pt']);x,y,scale=transforms['A']
  words=pg.get_text('words',clip=clip);labels={w[4]:w for w in words if w[4] in ('K','L')}
  if set(labels)=={'K','L'}:
   K,L=labels['K'],labels['L'];p1=xy(K[0]-3,K[1]);p2=xy(L[0]-3,L[1])
   s,e=timing.cue('Başlangıç olan ka noktasından bitiş olan le noktasına doğru tek bir ok çizeriz')
   addpath([[p1,p2],[[p2[0]-15,p2[1]-9],p2,[p2[0]-15,p2[1]+9]]],s,e,'displacement_on_source',color='#b66432',width=2.9,until=switch)
 timeline=dict(resolution=[1080,1920],fps=30,duration=duration,audio_duration=ad,audio_sha256=hashlib.sha256((q/'speech.mp3').read_bytes()).hexdigest(),background='background_A.png',source_switches=[dict(booklet='A',start=0,end=switch),dict(booklet='B',start=switch,end=duration+.1)],previous_ink_opacity=1,focus=[],strokes=strokes,bindings=bindings,timing_source='ElevenLabs actual character alignment; explicit spoken phrase intervals',question_pair=item['pair'])
 write_json(q/'zaman_cizelgesi.json',timeline);write_json(q/'soru_ve_kaynak.json',item)
 print(ident,round(ad,2),'s',len(strokes),'strokes',flush=True)
 return q
if __name__=='__main__':
 num=int(sys.argv[1]) if len(sys.argv)>1 else 1
 for item in json.loads((ROOT/f'batch{num:02d}.json').read_text()):build(item,f'batch{num:02d}')
