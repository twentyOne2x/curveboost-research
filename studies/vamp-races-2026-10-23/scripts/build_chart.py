"""Portable native SVG recreation; optional Pillow PNG. No network."""
from pathlib import Path
from html import escape
import argparse,json
PACKAGE=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=PACKAGE/'results/vamp-review.json');p.add_argument('--out',type=Path,default=PACKAGE/'charts/rebuilt');p.add_argument('--svg-only',action='store_true');args=p.parse_args();OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
data=json.loads(args.results.read_text());cohort=next(c for c in data['cohorts'] if c['label']=='contested');den=cohort['races'];opening=cohort['leaderWins1h']['yes'];first=cohort['firstLaunchWins1h']['yes']
assert (den,opening,first)==(1219,1007,577)
try:
 if args.svg_only:raise ImportError
 from PIL import Image,ImageDraw,ImageFont
except ImportError:
 Image=ImageDraw=ImageFont=None
W,H=1600,1000
BG='#0B0E12';WHITE='#F1F4F8';MUTED='#ABB4C1';BLUE='#8BAEE2';SILVER='#B9C0CB';RULE='#303844'
im=Image.new('RGB',(W*2,H*2),BG) if Image else None;d=ImageDraw.Draw(im) if im else None
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>']
def font(size,bold):
 for name in (['Arial Bold.ttf','DejaVuSans-Bold.ttf','LiberationSans-Bold.ttf'] if bold else ['Arial.ttf','DejaVuSans.ttf','LiberationSans-Regular.ttf']):
  try:return ImageFont.truetype(name,size*2)
  except OSError:pass
 return ImageFont.load_default(size=size*2)
def text(x,y,t,size=32,color=WHITE,bold=False):
 if d:d.text((x*2,y*2),t,font=font(size,bold),fill=color,anchor='lt')
 s.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" dominant-baseline="text-before-edge">{escape(t)}</text>')
def line(x,y,x2,y2,color=RULE,width=2):
 if d:d.line((x*2,y*2,x2*2,y2*2),fill=color,width=width*2)
 s.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
def rect(x,y,w,h,color):
 if d:d.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),fill=color)
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
text(70,56,f'{den:,} CONTESTED VAMP RACES',27,color=MUTED,bold=True)
text(70,124,'Opening volume and',73,bold=True)
text(70,211,'first-hour leadership',73,bold=True)
text(72,325,'Share that also led first-hour volume',34,color=MUTED)
x0=72;chartw=1456
for v in [0,50,100]:
 x=x0+chartw*v/100
 line(x,441,x,772,RULE,2)
 text(x-9 if v==50 else x-62 if v==100 else x,791,str(v)+'%',24,color=MUTED)
rows=[('Strongest two-minute opening',opening,den,BLUE,416),('First token launched',first,den,SILVER,612)]
for label,n,den,color,y in rows:
 pct=100*n/den;text(72,y,label,38,bold=True)
 rect(x0,y+69,chartw*n/den,77,color)
 endpoint=x0+chartw*n/den
 text(endpoint+21,y+68,f'{pct:.1f}%',57,color=color,bold=True)
 text(endpoint+24,y+130,f'{n:,} / {den:,}',25,color=MUTED)
line(70,862,1530,862)
text(70,887,'At least two tokens with $1,000+ first-hour volume.',27,color=MUTED)
text(70,928,'Each token uses its own two-minute and one-hour windows.',27,color=MUTED)
text(70,969,'Launches: 22–23 Oct 2026 · Circular.fi export, checked by attn.markets',24,color=MUTED)

(OUT/'vamp-opening-volume-v1.svg').write_text(''.join(s)+'</svg>')
if im:im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'vamp-opening-volume-v1.png')
print('SVG written; PNG '+('written with installed font fallback' if im else 'not requested or optional Pillow unavailable'))
