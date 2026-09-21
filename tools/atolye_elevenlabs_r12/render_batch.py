from pathlib import Path
import sys,json,subprocess,hashlib,concurrent.futures
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(next(x for x in [ROOT.parent/'production_r11',ROOT.parent/'atolye_elevenlabs_r11'] if x.exists())))
from render_saved_timeline import SavedPairRenderer
from pen_renderer import probe
from PIL import Image,ImageDraw

def render(q):
 r=SavedPairRenderer(q);out=q/'cozum.mp4';visual=q/'render_silent.tmp.mp4'
 if not out.exists():
  r.render(visual);r.mux(visual,q/'speech.mp3',out);visual.unlink()
 p=probe(out);v=next(s for s in p['streams'] if s['codec_type']=='video');assert(v['width'],v['height'],v['r_frame_rate'])==(1080,1920,'30/1')
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True,capture_output=True)
 ts=[.7]+[(x['start']+x['end'])/2 for x in r.p['bindings']]+[r.p['audio_duration']-.2,r.p['duration']-1]
 qc=q/'kontrol';qc.mkdir(exist_ok=True)
 for i,t in enumerate(ts):
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(out),'-frames:v','1',str(qc/f'kare_{i:02}.jpg')],check=True,capture_output=True)
 small=[]
 for f in sorted(qc.glob('kare_*.jpg')):
  im=Image.open(f);im.thumbnail((360,640));small.append(im)
 sheet=Image.new('RGB',(360*4,670*((len(small)+3)//4)),'#ddd');d=ImageDraw.Draw(sheet)
 for i,im in enumerate(small):sheet.paste(im,((i%4)*360,(i//4)*670));d.text(((i%4)*360+5,(i//4)*670+642),f'{ts[i]:.2f}s',fill='black')
 sheet.save(qc/'kontrol_kareleri.jpg')
 report=dict(question_id=q.name,technical_pass=True,resolution=[1080,1920],fps=30,audio_stream=True,full_decode_pass=True,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,duration_seconds=float(p['format']['duration']),visual_review='pending',auditory_review='not_performed',final_acceptance=False,checked_times=ts)
 (q/'kalite_kontrol.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE',q.name,flush=True)
 return report
if __name__=='__main__':
 num=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else 1
 qs=sorted((ROOT/f'Atolye_R12_Grup{num:02d}').glob('A/*/*/zaman_cizelgesi.json'))
 if '--drafts' in sys.argv:
  for p in qs:
   r=SavedPairRenderer(p.parent);r.frame(r.p['audio_duration']-.2).save(ROOT/(p.parent.name+'_draft.png'))
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
   for result in ex.map(render,[p.parent for p in qs]):print(result['question_id'],result['duration_seconds'],flush=True)
