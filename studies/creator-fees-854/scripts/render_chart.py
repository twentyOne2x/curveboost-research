"""Optional Pillow chart renderer from bundled article display values."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; W,H=1600,1380
BG='#0B0C0E'; WHITE='#F4F3EF'; CHROME='#BABDC3'; MUTED='#999EA7'; RULE='#30343A'; BLUE='#E1E3E6'; GAIN='#70D99C'
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
  self.im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'curveboost-first-hour-fees-v2.png');(OUT/'curveboost-first-hour-fees-v2.svg').write_text(''.join(self.s)+'</svg>')
def render(data):
 assert len(data['rows'])==2
 # Uplift is independently computed from exact lamports, never rounded display differences.
 precise=json.loads((ROOT/'results.json').read_text())
 from decimal import Decimal as D, ROUND_HALF_UP
 c=Plate()
 c.line(68,110,1532,110,RULE,2)
 mark=[(70+x,55+y) for x,y in [(0, 42), (14, 42), (28, 41), (39, 40), (47, 37), (53, 32), (57, 24), (60, 12), (62, 0), (65, 12), (70, -13), (68, 13), (80, 1), (71, 19), (85, 13), (73, 25), (79, 30), (69, 29), (65, 31), (61, 38), (51, 43), (35, 46), (14, 46), (0, 45)]]
 c.d.polygon([(x*2,y*2) for x,y in mark],fill=WHITE)
 c.s.append('<polygon points="'+' '.join(str(x)+','+str(y) for x,y in mark)+'" fill="'+WHITE+'"/>')
 c.text(163,50,'CurveBoost',32,bold=True);c.text(1170,54,'A product by attn.markets',25,color=CHROME)
 c.text(68,177,'First-hour creator fees',76,bold=True)
 c.text(70,287,'Same recorded trades across 854 launches',31,color=CHROME)
 for i,(r,exact) in enumerate(zip(data['rows'],precise['results'])):
  a=int(exact['actualFeeLamports']);b=int(exact['curveOnly95FeeLamports'])
  usd=(D(b-a)/D(1000000000)*D('107.24')).quantize(D(1),rounding=ROUND_HALF_UP)
  pct=(D(b-a)/D(a)*100).quantize(D('.1'),rounding=ROUND_HALF_UP)
  gainUSD='+$'+format(usd,',.0f');gainPct='+'+format(pct,'.1f')+'%'
  assert gainUSD==r['increaseUSD'] and gainPct==r['increasePct']
  y=385+i*405
  c.line(68,y-22,1532,y-22)
  c.text(70,y,r['handle'],36,bold=True);c.text(1150,y+5,f"{r['launches']} launches",29,color=CHROME)
  c.text(72,y+63,'INCREASE',23,color=GAIN,bold=True)
  c.text(68,y+98,gainUSD,83,color=GAIN,bold=True)
  c.text(710,y+116,gainPct,58,color=GAIN,bold=True)
  c.text(72,y+218,'Recorded fees',28,color=CHROME,bold=True)
  c.text(840,y+218,'Curve volume at 0.95%',28,color=CHROME,bold=True)
  c.text(68,y+260,r['actualSOL']+' SOL',51,bold=True)
  c.text(836,y+260,r['recalculatedSOL']+' SOL',51,bold=True)
  c.text(72,y+324,'('+r['actualUSD']+')',30,color=CHROME)
  c.text(840,y+324,'('+r['recalculatedUSD']+')',30,color=CHROME)
 c.line(68,1208,1532,1208)
 for i,line in enumerate(data['notes']):c.text(68,1235+39*i,line,26,color=MUTED)
 c.save()
if __name__=='__main__':
 p=ROOT/'figures/chart-input.json'
 render(json.loads(p.read_text()))
