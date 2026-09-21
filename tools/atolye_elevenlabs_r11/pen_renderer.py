"""True pen centerlines with Pillow; provider timing; no glyph contours/fills."""
from pathlib import Path
import json,math,subprocess,time,hashlib,os
import numpy as np
from PIL import Image,ImageDraw

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
class Renderer:
    def __init__(self,folder):
        self.q=folder;self.p=json.loads((folder/'zaman_cizelgesi.json').read_text());self.base=Image.open(folder/self.p['background']).convert('RGB');self.focus_key=None;self.cache=None;self.strokes=[]
        for raw in self.p['strokes']:
            s=raw.copy();s['np']=np.array(s['points'],float);s['arcs']=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(s['np'],axis=0),axis=1))];s['length']=float(s['arcs'][-1]);self.strokes.append(s)
    def line(self,im,pts,color,width):
        a=np.array(pts,float);pad=5
        box=(max(0,int(a[:,0].min())-pad),max(0,int(a[:,1].min())-pad),min(im.width,math.ceil(a[:,0].max())+pad),min(im.height,math.ceil(a[:,1].max())+pad))
        local=im.crop(box);sc=3;local=local.resize((local.width*sc,local.height*sc),Image.Resampling.NEAREST);d=ImageDraw.Draw(local)
        for i in range(len(a)-1):
            u=(i+.5)/max(1,len(a)-1);pressure=.9+.1*math.sin(math.pi*u)
            coords=[((x-box[0])*sc,(y-box[1])*sc) for x,y in a[i:i+2]]
            d.line(coords,fill=color,width=max(1,round(width*sc*pressure)))
        im.paste(local.resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS),box[:2])
    def draw_one(self,im,s,t,focused):
        if t<s['start'] or t>=s.get('until',999):return
        p=min(1,max(0,(t-s['start'])/(s['end']-s['start'])));p=p*p*(3-2*p);target=s['length']*p
        ind=int(np.searchsorted(s['arcs'],target,side='right'));pts=s['np'][:ind].copy()
        if 0<ind<len(s['np']):
            a,b=s['np'][ind-1],s['np'][ind];u=(target-s['arcs'][ind-1])/(s['arcs'][ind]-s['arcs'][ind-1] or 1);pts=np.vstack([pts,a+(b-a)*u])
        if len(pts)<2:return
        alpha=self.p['previous_ink_opacity'] if t>=s.get('fade_at',999) and s['label'] not in focused else 1.
        c=s['color'].lstrip('#');rgb=np.array([int(c[i:i+2],16) for i in [0,2,4]]);rgb=np.rint(255*(1-alpha)+rgb*alpha).astype(int)
        self.line(im,pts,tuple(int(v) for v in rgb),s['width'])
    def frame(self,t):
        focused={f['label'] for f in self.p['focus'] if f['start']<=t<f['end']}
        key=tuple((i,t>=s.get('fade_at',999) and s['label'] not in focused) for i,s in enumerate(self.strokes) if s['end']<=t<s.get('until',999))
        if key!=self.focus_key:
            base=self.base.copy()
            for i,_ in key:self.draw_one(base,self.strokes[i],t,focused)
            self.cache=base;self.focus_key=key
        im=self.cache.copy()
        for s in self.strokes:
            if s['start']<=t<s['end']:self.draw_one(im,s,t,focused)
        return im
    def render(self,visual):
        W,H=self.p['resolution'];fps=self.p['fps'];total=math.ceil(self.p['duration']*fps)
        p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(visual)],stdin=subprocess.PIPE);st=time.monotonic()
        try:
            for i in range(total):
                p.stdin.write(self.frame(i/fps).tobytes())
                if i%450==0:print('frame',i,'/',total,'seconds',round(time.monotonic()-st,1),flush=True)
        finally:p.stdin.close()
        if p.wait()!=0:raise RuntimeError('Video encoding failed')
    def mux(self,visual,audio,out):
        a=probe(audio);assert any(s.get('codec_type')=='audio' for s in a['streams']);assert abs(float(a['format']['duration'])-self.p['audio_duration'])<.25
        assert hashlib.sha256(audio.read_bytes()).hexdigest()==self.p['audio_sha256']
        pending=out.with_suffix('.muxing.mp4')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','volume=-1.5dB,apad','-t',str(self.p['duration']),'-movflags','+faststart',str(pending)],check=True)
        completed=probe(pending)
        assert {'video','audio'}<={s.get('codec_type') for s in completed['streams']}
        with pending.open('rb') as f:os.fsync(f.fileno())
        pending.replace(out)
        (self.q/'codec_bilgisi.json').write_text(json.dumps(probe(out),indent=2))
