"""Portable native SVG recreation; optional Pillow PNG. No network."""
from pathlib import Path
from html import escape
import argparse,json
PACKAGE=Path(__file__).resolve().parents[1]
ROOT=PACKAGE
# Resolve the same accepted-cover identity asset from the enclosing repository.
import importlib.util
brand_dir=next(p/'article/brand' for p in [ROOT,*ROOT.parents] if (p/'article/brand/brand_header.py').is_file())
brand_spec=importlib.util.spec_from_file_location('curveboost_shared_brand',brand_dir/'brand_header.py')
brand=importlib.util.module_from_spec(brand_spec);brand_spec.loader.exec_module(brand)

p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=PACKAGE/'results/vamp-review.json');p.add_argument('--out',type=Path,default=PACKAGE/'charts/rebuilt');p.add_argument('--svg-only',action='store_true');args=p.parse_args();OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
data=json.loads(args.results.read_text());cohort=next(c for c in data['cohorts'] if c['label']=='contested');den=cohort['races'];members=cohort['members'];opening=cohort['leaderWins1h']['yes'];first=cohort['firstLaunchWins1h']['yes']
assert (members,den,opening,first)==(5534,1219,1007,577)
try:
 if args.svg_only:raise ImportError
 from PIL import Image,ImageDraw,ImageFont
except ImportError:
 Image=ImageDraw=ImageFont=None
W,H=1600,1300
BG='#000000';WHITE='#F4F3EF';MUTED='#C7CAD0';BLUE='#70D99C';SILVER='#E1E3E6';RULE='#30343A'
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
if im:brand.paste_header(im)
s.append(brand.svg_header())
line(70,110,1530,110,RULE)
text(70,148,f'{members:,} tokens across {den:,} contested vamp races',31,bold=True)
text(68,216,'Who led the first hour?',80,bold=True)
text(72,323,'Share of races where each token had the most first-hour volume',32)
x0=72;chartw=1456
rows=[('Most volume in its first 2 minutes','Also led first-hour volume',opening,BLUE,429),
      ('First token launched','Led first-hour volume',first,SILVER,669)]
for label,sub,n,color,y in rows:
 pct=100*n/den
 text(72,y,label,43,bold=True)
 text(74,y+64,sub,31)
 text(1210,y-5,f'{pct:.1f}%',79,color=color,bold=True)
 text(1214,y+83,f'{n:,} of {den:,} races',26,color=MUTED)
 rect(x0,y+133,chartw,39,'#24282D')
 rect(x0,y+133,chartw*n/den,39,color)
for v in [0,50,100]:
 x=x0+chartw*v/100
 text(x-24 if v==50 else x-68 if v==100 else x,861,str(v)+'%',26,color=MUTED)
text(72,921,'Two separate comparisons of the same races; the groups can overlap.',29,color=MUTED)
line(70,985,1530,985)
text(70,1020,'In 82.6% of races, the 2-minute volume leader',39,bold=True)
text(70,1072,'also had the most first-hour volume.',39,bold=True)
text(70,1150,'At least two tokens per race with $1,000+ first-hour volume.',26,color=MUTED)
text(70,1192,"Each token's windows start at its own first trade.",26,color=MUTED)
text(70,1234,'@Circular_fi · non-exhaustive sample, 22–23 Oct 2026 · @attndotmarkets',25,color=MUTED)

(OUT/'curveboost-opening-volume-v5.svg').write_text(''.join(s)+'</svg>')
if im:im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'curveboost-opening-volume-v5.png')
print('SVG written; PNG '+('written with installed font fallback' if im else 'not requested or optional Pillow unavailable'))
