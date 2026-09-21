"""Re-render a saved question without any API call or new speech credits."""
from pathlib import Path
import argparse,json
from PIL import Image
from pen_renderer import Renderer
class SavedPairRenderer(Renderer):
    def __init__(self,q):
        super().__init__(q);self.book=None
        self.bases={b:Image.open(q/f'background_{b}.png').convert('RGB') for b in ('A','B')}
    def frame(self,t):
        period=next(s for s in self.p['source_switches'] if s['start']<=t<s['end'])
        book=period['booklet']
        if book!=self.book:self.base=self.bases[book];self.focus_key=None;self.book=book
        return super().frame(t)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('question_folder',type=Path);a=ap.parse_args();q=a.question_folder.resolve();r=SavedPairRenderer(q)
    visual=q/'render_silent.tmp.mp4';r.render(visual);r.mux(visual,q/'speech.mp3',q/'cozum.mp4');visual.unlink()
