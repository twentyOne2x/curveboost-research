"""One source-pixel identity master, shared by every chart; no redrawn logo/type."""
from pathlib import Path
import json,re
BASE=Path(__file__).resolve().parent
SPEC=json.loads((BASE/'clip-regions.json').read_text())
def svg_header(x=68,y=35):
 svg=(BASE/'curveboost-header.svg').read_text()
 return svg.replace('<svg ',f'<svg x="{x}" y="{y}" ',1)
def paste_header(canvas,x=68,y=35,scale=2):
 from PIL import Image,ImageDraw
 master=Image.open(BASE/'cover-master.png').convert('RGB')
 for part in SPEC['parts']:
  box=part['sourceBox'];crop=master.crop(box)
  if part.get('sourceClipPolygon'):
   mask=Image.new('L',crop.size,0);ImageDraw.Draw(mask).polygon([(px-box[0],py-box[1]) for px,py in part['sourceClipPolygon']],fill=255)
   clean=Image.new('RGB',crop.size,'black');clean.paste(crop,(0,0),mask);crop=clean
  dx,dy,dw,dh=part['targetBox'];factor=min(dw/crop.width,dh/crop.height);w=round(crop.width*factor*scale);h=round(crop.height*factor*scale)
  crop=crop.resize((w,h),Image.Resampling.LANCZOS)
  canvas.paste(crop,(round((x+dx+dw/2)*scale-w/2),round((y+dy+dh/2)*scale-h/2)))
