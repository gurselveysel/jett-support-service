from pathlib import Path
import subprocess,json,hashlib,numpy as np,sys
from PIL import Image,ImageDraw
q=Path(sys.argv[1]);p=q/'cozum.mp4'
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True,capture_output=True)
pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-ac','1','pipe:1']);a=np.frombuffer(pcm,dtype='<f4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
times=[0,17.7,28.5,37.5,43.8,54.2,63.5,69.75,71.5] if q.name.endswith('06') else [0,28.5,43,57,77.1,91.95,94.2]
r={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration':float(probe['format']['duration']),'full_decode_pass':True,'streams':[{'codec':s['codec_name'],'type':s['codec_type'],'width':s.get('width'),'height':s.get('height'),'fps':s.get('r_frame_rate')} for s in probe['streams']], 'audio_peak_dbfs':float(20*np.log10(np.max(np.abs(a)))),'audio_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(a*a)))),'clipped_samples':int(np.sum(np.abs(a)>=1)),'auditory_review':False,'visual_review_pending':True,'actual_mp4_check_seconds':times,'final_acceptance':False}
(q/'kontrol_MP4.json').write_text(json.dumps(r,indent=2));print(r)
for t in times:subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1',str(q/'kontrol_kareleri'/f'mp4_{t:06.2f}.jpg')],check=True)
files=sorted((q/'kontrol_kareleri').glob('mp4_*'));sheet=Image.new('RGB',(320*3,610*3),'#dddddd')
for i,f in enumerate(files):
 im=Image.open(f);im.thumbnail((320,570));sheet.paste(im,((i%3)*320,(i//3)*610));ImageDraw.Draw(sheet).text(((i%3)*320+5,(i//3)*610+575),f.name,fill='black')
sheet.save(q/'gercek_mp4_kontrol.jpg')
