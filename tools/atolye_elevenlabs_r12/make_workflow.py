import json,pathlib,textwrap,sys
num=int(sys.argv[1]) if len(sys.argv)>1 else 1
p=pathlib.Path(__file__).parent
old=(p/'workflow_previous.yml').read_text()
source=old.split('        run: |\n',1)[1].split('      - name: Install',1)[0]
source=textwrap.dedent(source).rstrip()
source=source.replace("out = pathlib.Path('atolye-elevenlabs-a06-b10')", "out = pathlib.Path('atolye-r12-batch01')/item['id']")
source=source.replace('out.mkdir(exist_ok=True)','out.mkdir(parents=True,exist_ok=True)')
source=source.replace("['A-Temel_Matematik-06','B-Temel_Matematik-10']","item['pair']")
start=source.index('text=');end=source.index('\nclass NoRedirect',start)
source=source[:start]+"text=item['narration']"+source[end:]
source=source.replace('sys.exit(2)','raise ProductionStop(status)')
source+='''
import subprocess
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'speech.mp3')]))
duration=float(probe['format']['duration'])
assert math.isfinite(duration) and duration>1
assert any(s['codec_type']=='audio' for s in probe['streams'])
assert report['last_alignment_second']<=duration+0.5
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out/'speech.mp3'),'-f','null','-'],check=True,capture_output=True)
save_report('audio_generated_and_decoded',duration_seconds=duration,audio_decode_pass=True,auditory_review=False)
'''
batch=[{k:i[k] for k in ('id','pair','narration')} for i in json.loads((p/f'batch{num:02d}.json').read_text())]
script='import json, pathlib\nclass ProductionStop(Exception): pass\ndef produce(item):\n'+textwrap.indent(source,'    ')+'\nitems='+repr(batch)+'''\nfor item in items:
    try:
        produce(item)
    except ProductionStop:
        raise SystemExit(2)
    except Exception as error:
        print('BATCH_STOP '+json.dumps({'id':item['id'],'error_type':type(error).__name__,'action':'Inspect saved artifacts before any new TTS request.'}))
        raise SystemExit(3)
'''
compile(script,'workflow-script','exec')
wf='''name: Atolye ElevenLabs R12 Batch01
run-name: Atolye R12 Batch01 - 7 unique questions - included credit
on:
  push:
    branches: [atolye-elevenlabs-20260921]
    paths: [.github/workflows/atolye-elevenlabs.yml]
  workflow_dispatch:
permissions: {}
concurrency:
  group: atolye-elevenlabs-production
  cancel-in-progress: false
jobs:
  speech:
    if: github.ref == 'refs/heads/atolye-elevenlabs-20260921'
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - name: Ensure audio verification tools
        run: |
          if ! command -v ffprobe >/dev/null || ! command -v ffmpeg >/dev/null; then
            sudo apt-get update -qq
            sudo apt-get install --no-install-recommends -y ffmpeg
          fi
      - name: Verify quota and produce seven real narrations with provider timestamps
        shell: python
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
        run: |
'''+textwrap.indent(script,'          ')+'''
      - name: Preserve all generated audio and timestamps even after partial failure
        if: always()
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
        with:
          name: atolye-r12-batch01-${{ github.run_id }}
          path: atolye-r12-batch01/
          if-no-files-found: warn
          retention-days: 30
'''
wf=wf.replace('batch01',f'batch{num:02d}').replace('Batch01',f'Batch{num:02d}').replace('7 unique',f'{len(batch)} unique').replace('seven real',f'{len(batch)} real')
(p/f'workflow_batch{num:02d}.yml').write_text(wf)
print(json.dumps({'questions':len(batch),'characters':sum(len(x['narration']) for x in batch),'syntax_valid':True,'only_remote_host':'api.elevenlabs.io'}))
