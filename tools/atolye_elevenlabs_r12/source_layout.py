"""Preserve shared reading passages and original PDF coordinates in one question panel."""
import fitz,io,math
from PIL import Image
def sections(m):
 r=m['soru_kirpma_konumu_pt']
 if m.get('ortak_paragraf_dahil'):
  return [fitz.Rect(m['kaynak_gorsel_bolumleri'][0]),fitz.Rect(r)]
 return [fitz.Rect(r)]
def render_source(pg,m):
 rs=sections(m);left=min(r.x0 for r in rs);right=max(r.x1 for r in rs);factor=3.2;offset=0;parts=[];layout=[]
 for r in rs:
  r=fitz.Rect(left,r.y0,right,r.y1);pm=pg.get_pixmap(clip=r,matrix=fitz.Matrix(factor,factor));im=Image.open(io.BytesIO(pm.tobytes('png'))).convert('RGB');parts.append((im,round(offset*factor)));layout.append((list(r),offset));offset+=im.height/factor+8
 out=Image.new('RGB',(max(i.width for i,y in parts),max(y+i.height for i,y in parts)),'white')
 for im,y in parts:out.paste(im,(0,y))
 return out,layout,right-left
def map_point(layout,px,py):
 for (x0,y0,x1,y1),offset in layout:
  if y0-3<=py<=y1+3:return px-x0,offset+py-y0
 raise ValueError(('PDF point outside included source sections',px,py))
