"""Optional Pillow chart renderer from bundled article display values."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; W,H=1600,1160
BG='#0B0C0E'; WHITE='#F4F3EF'; CHROME='#BABDC3'; MUTED='#999EA7'; RULE='#30343A'; BLUE='#E1E3E6'
FONT=None
class Plate:
 def __init__(self):
  self.im=Image.new('RGB',(W*2,H*2),BG);self.d=ImageDraw.Draw(self.im);self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>']
 def text(self,x,y,t,size=32,color=WHITE,bold=False):
  f=None
  for name in (['Arial Bold.ttf','DejaVuSans-Bold.ttf','LiberationSans-Bold.ttf'] if bold else ['Arial.ttf','DejaVuSans.ttf','LiberationSans-Regular.ttf']):
   try:f=ImageFont.truetype(name,size*2);break
   except OSError:pass
  if f is None:f=ImageFont.load_default(size=size*2)
  self.d.text((x*2,y*2),t,fill=color,font=f,anchor='lt')
  self.s.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-weight="{700 if bold else 400}" font-size="{size}" fill="{color}" dominant-baseline="text-before-edge">{escape(t)}</text>')
 def line(self,x,y,x2,y2,color=RULE,width=2):
  self.d.line((x*2,y*2,x2*2,y2*2),fill=color,width=width*2);self.s.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
 def save(self):
  self.im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'curve-boost-first-hour-fees-v1.png');(OUT/'curve-boost-first-hour-fees-v1.svg').write_text(''.join(self.s)+'</svg>')
def render(data):
 assert len(data['rows'])==2
 for row in data['rows']:
  for key in ['handle','launches','actualSOL','actualUSD','recalculatedSOL','recalculatedUSD']: assert key in row
 c=Plate()
 c.line(68,110,1532,110,RULE,2)
 mark=[(70+x,55+y) for x,y in [(0, 34), (12, 33), (24, 31), (34, 27), (42, 21), (47, 13), (48, 6), (47, 0), (51, 10), (59, -10), (55, 12), (67, 0), (58, 15), (74, 10), (60, 21), (66, 27), (57, 25), (51, 26), (44, 30), (34, 34), (21, 36), (0, 36)]]
 c.d.polygon([(x*2,y*2) for x,y in mark],fill=WHITE)
 c.s.append('<polygon points="'+' '.join(str(x)+','+str(y) for x,y in mark)+'" fill="'+WHITE+'"/>')
 c.text(163,50,'Curve Boost',32,bold=True);c.text(1334,54,'attn.markets',25,color=CHROME)
 c.text(68,190,'First-hour',84,bold=True)
 c.text(68,284,'creator fees',84,color=BLUE,bold=True)
 c.text(70,402,'Same recorded trades across 854 launches',30,color=CHROME)
 c.text(563,485,'Recorded fees',27,color=CHROME,bold=True)
 c.text(1060,485,'Curve volume at 0.95%',27,color=BLUE,bold=True)
 for i,r in enumerate(data['rows']):
  y=565+i*228
  c.line(68,y-25,1532,y-25)
  c.text(68,y,r['handle'],35,bold=True)
  c.text(70,y+59,f"{r['launches']} launches",26,color=MUTED)
  c.text(560,y-7,r['actualSOL']+' SOL',57,bold=True)
  c.text(563,y+75,'('+r['actualUSD']+')',31,color=CHROME)
  c.text(1057,y-7,r['recalculatedSOL']+' SOL',57,color=BLUE,bold=True)
  c.text(1060,y+75,'('+r['recalculatedUSD']+')',31,color=CHROME)
 c.line(68,990,1532,990)
 for i,line in enumerate(data['notes']):c.text(68,1014+38*i,line,25,color=MUTED)
 c.save()
if __name__=='__main__':
 p=ROOT/'figures/chart-input.json'
 if not p.exists():raise SystemExit('Awaiting exact fee and saved USD values; no output rendered.')
 render(json.loads(p.read_text()))
