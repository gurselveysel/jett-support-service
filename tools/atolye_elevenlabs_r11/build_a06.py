from pathlib import Path
import json,math,shutil,hashlib,sys,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pen_glyphs as pen
from pen_renderer import Renderer
ROOT=Path(os.environ.get('ATOLYE_PRODUCTION_ROOT',str(Path(__file__).resolve().parent))).resolve();Q=ROOT/'A/Temel_Matematik/A-Temel_Matematik-06';Q.mkdir(parents=True,exist_ok=True)
for f in ((ROOT/'audio_A06').iterdir() if (ROOT/'audio_A06').exists() else []):shutil.copy2(f,Q/f.name)
speech=json.loads((Q/'speech.json').read_text());words=speech['word_timestamps'];pen.WORDS=words
strokes=pen.strokes;bindings=pen.bindings

def ink(txt,x,y,size,i,j=None,label='math',color='#184e69'):
    j=i if j is None else j;a=words[i]['start'];b=words[j]['end']
    source={'text':' '.join(w['text'] for w in words[i:j+1]),'start':a,'end':b}
    return pen.ink(txt,x,y,size,a,b,label,color,source)
def eq(txt,x,y,size,start,end,label):return pen.ink(txt,x,y,size,start,end,label)
def formula(events,x,y,size,label):
    for txt,i,j,raised in events:
        if raised:
            ink(txt,x,y-17,size*.64,i,j,label);x+=size*.55
        else:x=ink(txt,x,y,size,i,j,label)
    return x

def background(book,num,page):
    im=Image.new('RGB',(1080,1920),'#0b3d59');d=ImageDraw.Draw(im)
    f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
    logo=Image.open(ROOT/'logolar/Atolye_Original_From_Cover.png').convert('RGBA');logo.thumbnail((358,275),Image.Resampling.LANCZOS);im.paste(logo,(43,15),logo)
    d.text((450,65),'SEVİYE BELİRLEME SINAVI',font=f(29),fill='#92d0df');d.text((450,117),'TEMEL',font=f(48),fill='white');d.text((450,174),'MATEMATİK',font=f(48),fill='white');d.text((450,250),'A · SORU 06   /   B · SORU 10',font=f(28),fill='white')
    d.rounded_rectangle((36,312,1044,1782),radius=32,fill='white');d.text((75,333),f'{book} kitapçığı · Soru {num:02d}',font=f(25),fill='#60767e');d.text((807,333),f'PDF s. {page}',font=f(25),fill='#60767e')
    src=Image.open(Q/f'kaynak_{book}_{num:02d}.png').convert('RGB');src=src.resize((940,round(src.height*.94)),Image.Resampling.LANCZOS);im.paste(src,(70,385));d.line((95,962,985,962),fill='#e6edef',width=1)
    d.rectangle((0,1810,1080,1920),fill='white');uz=Image.open(ROOT/'logolar/UzemGO_Original_Transparent.png').convert('RGBA');uz.thumbnail((285,91),Image.Resampling.LANCZOS);im.paste(uz,((1080-uz.width)//2,1819),uz)
    im.save(Q/f'background_{book}.png');None  # Exact source crop already preserved in question folder.
background('A',6,18);background('B',10,20)
# Coverage formula; each spoken group anchors only its own pen tokens.
x=formula([('2',25,None,False),(',',26,None,False),('43',27,28,False),('×',29,None,False),('10',30,31,False),('5',32,33,True)],135,1008,49,'coverage')
x=eq('=',x+8,1008,49,23.04,24.16,'coverage');x=ink('2',x,1008,49,47,48,'coverage');x=ink('43',x,1008,49,49,50,'coverage');x=ink('000',x,1008,49,51,52,'coverage');ink('m',x+12,1008,45,53,None,'coverage')
# Ali: expansion and comparison on a single line.
ink('Ali',130,1120,38,54,55,'ali')
x=formula([('2',56,None,False),('1',57,None,False),(',',58,None,False),('3',59,None,False),('×',60,None,False),('10',61,62,False),('4',63,None,True)],130,1185,42,'ali')
x=eq('=',x+6,1185,42,31.744,32.64,'ali');x=ink('2',x,1185,42,67,68,'ali');x=ink('13',x,1185,42,69,70,'ali');x=ink('000',x,1185,42,71,72,'ali')
comp=x+8;ink('<',comp,1185,42,84,None,'ali');x=comp+38;x=ink('2',x,1185,42,79,80,'ali');x=ink('43',x,1185,42,81,82,'ali');ink('000',x,1185,42,83,None,'ali');ink('✓',951,1185,37,86,87,'ali')
# Berna.
ink('Berna',130,1300,38,88,89,'berna')
x=formula([('23',90,91,False),(',',92,None,False),('3',93,None,False),('×',94,None,False),('10',95,96,False),('4',97,None,True)],130,1365,42,'berna')
# The equals pen mark begins with the spoken result, then the numeral follows.
x=eq('=',x+6,1365,42,44.0,44.10,'berna');x=eq('2',x,1365,42,44.10,44.24,'berna');x=ink('33',x,1365,42,100,101,'berna');x=ink('000',x,1365,42,102,103,'berna')
comp=x+8;ink('<',comp,1365,42,111,None,'berna');x=comp+38;x=ink('2',x,1365,42,106,107,'berna');x=ink('43',x,1365,42,108,109,'berna');ink('000',x,1365,42,110,None,'berna');ink('✓',951,1365,37,114,None,'berna')
# Ceyda and the counter-comparison.
ink('Ceyda',130,1490,38,115,116,'ceyda')
x=formula([('1',117,None,False),(',',118,None,False),('25',119,120,False),('×',121,None,False),('10',122,123,False),('8',124,None,True)],130,1555,42,'ceyda')
x=ink('=',x+6,1555,42,125,None,'ceyda');x=ink('1',x,1555,42,126,None,'ceyda');x=ink('25',x,1555,42,127,128,'ceyda');ink('000000',x,1555,42,129,130,'ceyda')
x=ink('125000000',130,1670,42,131,132,'comparison');ink('>',x+9,1670,42,139,None,'comparison');x+=51;x=ink('2',x,1670,42,133,134,'comparison');x=ink('43',x,1670,42,135,136,'comparison');ink('000',x,1670,42,137,138,'comparison');ink('×',951,1555,37,142,143,'ceyda')
ellipse=[[299+29*math.cos(t),891+27*math.sin(t)] for t in np.linspace(-.2,2*math.pi+.1,90)]
strokes.append(dict(points=ellipse,start=68.2,end=69.68,width=3.1,color='#146c65',label='answer',fade_at=999))
audio_duration=json.loads((Q/'report.json').read_text())['duration_seconds'];duration=73.2

timeline=dict(background='background_A.png',resolution=[1080,1920],fps=30,duration=duration,audio_duration=audio_duration,audio_sha256=hashlib.sha256((Q/'speech.mp3').read_bytes()).hexdigest(),previous_ink_opacity=.55,focus=[],strokes=strokes,check_times=[0,8,25.9,38.2,49.5,63.5,69.75,71.5],source_switches=[{'start':0,'end':5.64,'booklet':'A'},{'start':5.64,'end':13.52,'booklet':'B'},{'start':13.52,'end':69.92,'booklet':'A'},{'start':69.92,'end':duration,'booklet':'B'}],timing_source='ElevenLabs provider character alignment → exact word groups',glyph_method='explicit centerline pen paths; no outlines or fill',token_bindings=bindings)
(Q/'zaman_cizelgesi.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
class PairRenderer(Renderer):
    def __init__(self,q):
        super().__init__(q);self.bases={b:Image.open(q/f'background_{b}.png').convert('RGB') for b in ['A','B']};self.book=None
    def frame(self,t):
        book='B' if 5.64<=t<13.52 or t>=69.92 else 'A'
        if book!=self.book:self.base=self.bases[book];self.focus_key=None;self.book=book
        return super().frame(t)
if __name__=='__main__':
    r=PairRenderer(Q);(Q/'kontrol_kareleri').mkdir(exist_ok=True)
    for t in timeline['check_times']:r.frame(t).save(Q/'kontrol_kareleri'/f'{t:06.2f}.jpg',quality=95)
    if '--render' in sys.argv:
        visual=Q/'silent.tmp.mp4';r.render(visual);r.mux(visual,Q/'speech.mp3',Q/'cozum.mp4')
        with (Q/'cozum.mp4').open('rb') as f:os.fsync(f.fileno())
        visual.unlink()
