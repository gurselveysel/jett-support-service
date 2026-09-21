"""A05/B12: exact provider word cues, explicit single-line pen paths, one video."""
from pathlib import Path
import json, math, shutil, hashlib, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pen_renderer import Renderer

ROOT=Path(os.environ.get('ATOLYE_PRODUCTION_ROOT',str(Path(__file__).resolve().parent))).resolve()
Q=ROOT/'A/Temel_Matematik/A-Temel_Matematik-05'
Q.mkdir(parents=True,exist_ok=True)
for f in ((ROOT/'audio_A05').iterdir() if (ROOT/'audio_A05').exists() else []): shutil.copy2(f,Q/f.name)
WORDS=json.loads((Q/'speech.json').read_text())['word_timestamps']
def cue(t):
    w=min(WORDS,key=lambda w:abs(w['start']-t))
    assert abs(w['start']-t)<.02,(t,w)
    return w
def curve(points,n=10):
    # Catmull-Rom interpolation of a pen's centerline, never a glyph outline.
    a=np.array(points,float);a=np.vstack([a[0],a,a[-1]]);out=[]
    for i in range(1,len(a)-2):
        p0,p1,p2,p3=a[i-1:i+3]
        for t in np.linspace(0,1,n,endpoint=False):
            out.append((.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)).tolist())
    return out+[points[-1]]
def C(*p):return curve(p)
G={
 '2':(.68,[C((.05,.23),(.18,.05),(.47,.03),(.6,.19),(.53,.38),(.3,.65),(.05,.91),(.57,.91))]),
 '1':(.48,[[(.04,.25),(.26,.05),(.25,.93)]]),
 '4':(.7,[[(.48,.02),(.02,.65),(.64,.65)],[(.46,.34),(.43,.95)]]),
 'p':(.6,[[(.15,.31),(.09,1.19)],C((.13,.47),(.28,.29),(.48,.33),(.5,.57),(.31,.73),(.11,.68))]),
 'k':(.6,[[(.19,.03),(.07,.94)],[(.53,.32),(.13,.62),(.48,.94)]]),
 '+':(.75,[[(.08,.5),(.66,.5)],[(.39,.21),(.37,.81)]]),
 '-':(.73,[[(.09,.52),(.62,.50)]]),
 '=':(.74,[[(.08,.37),(.64,.36)],[(.07,.64),(.64,.63)]]),
 '×':(.68,[[(.09,.24),(.58,.78)],[(.58,.23),(.1,.8)]]),
 '(':(.38,[C((.3,.02),(.15,.27),(.1,.57),(.12,.86),(.26,1.08))]),
 ')':(.38,[C((.08,.02),(.23,.27),(.27,.56),(.22,.86),(.08,1.08))]),
 ',':(.27,[[(.15,.82),(.13,.95),(.02,1.07)]]),
 ';':(.3,[[(.15,.35),(.15,.39)],[(.15,.82),(.13,.95),(.02,1.07)]]),
 '∈':(.75,[C((.65,.23),(.25,.22),(.08,.52),(.23,.79),(.64,.8)),[(.08,.5),(.58,.5)]]),
 '∉':(.75,[C((.65,.23),(.25,.22),(.08,.52),(.23,.79),(.64,.8)),[(.08,.5),(.58,.5)],[(.58,.05),(.15,.98)]]),
 'Z':(.76,[[(.09,.06),(.64,.05),(.07,.92),(.66,.92)],[(.28,.08),(.09,.35)],[(.65,.66),(.45,.91)]]),
 'A':(.76,[[(.02,.96),(.37,.04),(.67,.96)],[(.14,.63),(.55,.63)]]),
 '✓':(.72,[[(.02,.5),(.26,.85),(.67,.1)]]),
 ' ': (.34,[]),
}
strokes=[];bindings=[]
def paths(text,x,y,size):
    result=[]
    for ch in text:
        advance,gs=G[ch]
        for g in gs:result.append([[round(x+size*(a+.05*(1-b)),3),round(y+size*b,3)] for a,b in g])
        x+=size*(advance+.1)
    return result,x
def ink(text,x,y,size,start,end,label,color='#184e69',source=None):
    pp,nx=paths(text,x,y,size)
    lens=[float(np.linalg.norm(np.diff(np.array(p),axis=0),axis=1).sum()) for p in pp]
    total=sum(lens);elapsed=0
    for p,l in zip(pp,lens):
        a=start+(end-start)*elapsed/total;elapsed+=l;b=start+(end-start)*elapsed/total
        strokes.append(dict(points=p,start=a,end=max(a+.015,b),width=3.2,color=color,label=label,fade_at=999))
    if source:bindings.append(dict(written=text,source_word=source['text'],source_start=source['start'],source_end=source['end'],ink_start=start,ink_end=end,label=label))
    return nx
def word(text,x,y,t,size=57,label=''):
    w=cue(t);end=w['end']-.27 if text=='k' and t in (33.44,47.387,62.853) else w['end'];return ink(text,x,y,size,w['start'],end,label,source=w)
def row(y,events,label):
    x=128
    for text,t in events:x=word(text,x,y,t,label=label)
    return x

# Header and source versions occupy the same single work surface.
navy='#0b3d59';white='#ffffff';gray='#60767e'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
logo=Image.open(ROOT/'logolar/Atolye_Original_From_Cover.png').convert('RGBA')
logo.thumbnail((358,275),Image.Resampling.LANCZOS)
uzem=Image.open(ROOT/'logolar/UzemGO_Original_Transparent.png').convert('RGBA')
uzem.thumbnail((285,91),Image.Resampling.LANCZOS)
for book,num,page in [('A',5,18),('B',12,20)]:
    im=Image.new('RGB',(1080,1920),navy);d=ImageDraw.Draw(im)
    im.paste(logo,(43,15),logo)
    d.text((450,65),'SEVİYE BELİRLEME SINAVI',font=font(29),fill='#92d0df')
    d.text((450,117),'TEMEL',font=font(48),fill=white)
    d.text((450,174),'MATEMATİK',font=font(48),fill=white)
    d.text((450,250),'A · SORU 05   /   B · SORU 12',font=font(28),fill=white)
    d.rounded_rectangle((36,312,1044,1782),radius=32,fill=white)
    d.text((75,333),f'{book} kitapçığı · Soru {num:02d}',font=font(25),fill=gray)
    d.text((807,333),f'PDF s. {page}',font=font(25),fill=gray)
    src=Image.open(Q/f'kaynak_{book}_{num:02d}.png').convert('RGB')
    src=src.resize((940,round(src.height*940/src.width)),Image.Resampling.LANCZOS)
    im.paste(src,(70,385))
    d.line((95,1030,985,1030),fill='#e6edef',width=1)
    d.rectangle((0,1810,1080,1920),fill=white);im.paste(uzem,((1080-uzem.width)//2,1819),uzem)
    im.save(Q/f'background_{book}.png')
    None  # Exact source crop already preserved in question folder.

# Every mathematical token is anchored to its actual spoken word.
x=word('2',128,1060,20.12,47,'base');x=word('p',x,1060,20.613,47,'base')
x=word(',',x,1060,20.987,47,'base');x=word('2',x+20,1060,21.28,47,'base');word('k',x,1060,21.627,47,'base')
x=word('p',525,1060,23.68,43,'base');x=word(',',x,1060,23.92,43,'base');x=word('k',x,1060,24.16,43,'base');x=word('∈',x+10,1060,24.4,43,'base');word('Z',x,1060,25.088,43,'base')
end_sum=row(1170,[('2',27.62),('p',28.),('+',28.28),('2',28.72),('k',29.04),('=',29.52),('2',30.12),('×',30.56),('(',31.41),('p',32.64),('+',32.9),('k',33.44)],'sum')
ink(')',end_sum,1170,57,34.02,34.24,'sum')
word('✓',929,1170,38.24,45,'sum')
end_diff=row(1300,[('2',41.68),('p',42.107),('-',42.56),('2',42.92),('k',43.173),('=',43.76),('2',44.3),('×',44.8),('(',45.54),('p',46.667),('-',46.96),('k',47.387)],'difference')
ink(')',end_diff,1300,57,47.79,48.,'difference')
word('✓',929,1300,53.493,45,'difference')
# Slightly smaller full multiplication identity fits without a second panel.
x=128
for txt,t in [('2',56.13),('p',56.507),('×',56.784),('2',57.2),('k',57.547),('=',58.08),('2',58.62),('×',59.12),('(',59.92),('2',61.1),('×',61.344),('p',61.813),('×',62.176),('k',62.853)]:x=word(txt,x,1430,t,49,'product')
ink(')',x,1430,49,63.5,63.76,'product');word('✓',929,1430,65.728,45,'product')
# Proper handwritten fractions, numerator / bar / denominator in spoken order.
word('2',155,1556,76.76,46,'division')
strokes.append(dict(points=[[144,1612],[214,1612]],start=76.94,end=77.32,width=3.2,color='#184e69',label='division',fade_at=999))
word('4',158,1628,77.36,46,'division')
word('=',250,1589,77.787,56,'division')
word('1',356,1556,78.46,46,'division')
strokes.append(dict(points=[[333,1612],[405,1612]],start=78.7,end=78.96,width=3.2,color='#184e69',label='division',fade_at=999))
word('2',351,1628,79.06,46,'division')
word('∉',475,1589,83.84,56,'division');word('A',536,1589,84.142,56,'division')
# Correct option C is marked on the unmodified source image.
ellipse=[[137+29*math.cos(t),815+27*math.sin(t)] for t in np.linspace(-.2,2*math.pi+.1,90)]
strokes.append(dict(points=ellipse,start=90.36,end=91.92,width=3.1,color='#146c65',label='answer',fade_at=999))

duration=95.4
timeline=dict(background='background_A.png',resolution=[1080,1920],fps=30,duration=duration,audio_duration=91.95102,audio_sha256=hashlib.sha256((Q/'speech.mp3').read_bytes()).hexdigest(),previous_ink_opacity=.55,focus=[],strokes=strokes,check_times=[0,8,23,34.3,48.2,63.9,79.9,91.95,94.2],source_switches=[{'start':0,'end':5.24,'booklet':'A'},{'start':5.24,'end':18.74,'booklet':'B'},{'start':18.74,'end':92.1,'booklet':'A'},{'start':92.1,'end':95.4,'booklet':'B'}],timing_source='ElevenLabs provider character alignment → exact word cues',glyph_method='explicit centerline pen paths; no outlines or fill',token_bindings=bindings)
(Q/'zaman_cizelgesi.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
class PairRenderer(Renderer):
    def __init__(self,q):
        super().__init__(q);self.bases={b:Image.open(q/f'background_{b}.png').convert('RGB') for b in ['A','B']};self.book=None
    def frame(self,t):
        book='B' if 5.24<=t<18.74 or t>=92.1 else 'A'
        if book!=self.book:self.base=self.bases[book];self.focus_key=None;self.book=book
        return super().frame(t)
if __name__=='__main__':
    r=PairRenderer(Q)
    (Q/'kontrol_kareleri').mkdir(exist_ok=True)
    for t in timeline['check_times']:r.frame(t).save(Q/'kontrol_kareleri'/f'{t:06.2f}.jpg',quality=95)
    if '--render' in sys.argv:
        visual=Q/'silent.tmp.mp4';r.render(visual);r.mux(visual,Q/'speech.mp3',Q/'cozum.mp4');visual.unlink()
