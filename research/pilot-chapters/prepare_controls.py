"""Small editable spatial controls for four high-risk pilot beats; not final artwork."""
from pathlib import Path
import json,hashlib
import cairosvg
R=Path(__file__).resolve().parents[2];D=R/'production/pilot-chapters/controls';D.mkdir(exist_ok=True)
header='<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000"><rect width="1000" height="1000" fill="#f5f2e9"/><g stroke-linejoin="round" stroke-linecap="round">'
def line(x1,y1,x2,y2,color='#222',width=8):return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>'
def poly(points,fill,stroke='#222'):return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'
def rect(x,y,w,h,fill):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#555" stroke-width="4"/>'
def circle(x,y,r,fill='#fff'):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#222" stroke-width="5"/>'
def label(x,y,t):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="22" fill="#222">{t}</text>'
def person(head,body,feet,arms):
 x,y=head;bx,by=body;s=circle(x,y,30)+line(x,y+30,bx,by,width=20)
 for fx,fy in feet:s+=line(bx,by,fx,fy,width=14)
 for points in arms:s+=f'<polyline points="{points}" stroke="#222" stroke-width="12" fill="none"/>'
 return s
panels={}
s=rect(740,340,260,35,'#999')+rect(790,285,25,60,'#444')+rect(140,790,410,50,'#aaa')+rect(170,840,350,120,'#ddd')
s+=person((350,510),(365,690),[(285,785),(440,785)],['350,565 430,650 475,590','360,565 320,690 350,730'])
s+=line(475,590,805,305,'#00a4b4',5)+line(475,590,535,595,'#a32132',12)+poly('530,595 665,570 640,615 555,625','#b8d9e1')
s+=poly('720,450 950,430 950,600 680,580 615,570 700,545','#73848d')+label(600,270,'one bridge anchor')+label(580,685,'blade redirects beak')+label(145,920,'lift roof supports both boots')
panels['NG10']=(s,'Bridge anchor → sword pommel; one blade/beak contact; boots braced on lift roof. Composition schematic only; preserve specified cast anatomy.')
s=rect(700,280,300,30,'#aaa')+rect(815,220,25,65,'#444')+rect(130,845,230,110,'#ddd')
s+=person((540,535),(545,625),[(515,690),(575,680)],['540,570 595,580 600,520','545,570 495,630 480,640'])
s+=person((450,635),(455,730),[(420,800),(485,805)],['450,670 455,640 480,640','450,670 405,700 415,740'])
s+=line(600,520,828,235,'#00a4b4',5)+line(600,520,640,480,'#a32132',9)+line(245,840,265,755,'#555',4)
s+=label(695,190,'safe bridge')+label(115,985,'empty falling lift')+label(600,730,'clasp stays connected')
panels['NG12']=(s,'One airborne pair linked by forearm clasp, one pommel line to bridge, separate empty falling lift. Camera must keep adults small.')
s=rect(0,720,510,280,'#bbb')+rect(510,880,490,120,'#536773')
s+=person((240,465),(245,620),[(160,715),(310,715)],['235,510 310,585 390,600','250,510 315,560 350,590'])
s+=poly('660,450 925,520 920,620 690,580 595,570','#555')+poly('615,725 950,750 925,830 650,795','#666')
s+=line(350,590,615,650,'#a32132',12)+f'<path d="M640 572 C590 580 590 700 642 720" fill="none" stroke="#a32132" stroke-width="20"/>'
s+=circle(795,650,26,'#eee')+line(815,667,885,700,'#eee',22)+label(550,390,'upper shoulder braces upper jaw')+label(525,850,'lower curve catches lower rim')+label(620,975,'body stays in water')+label(700,685,'side exit')
panels['FL11']=(s,'C-head has two jaw countercontacts, clear exit beside implement, dry support and connected water body. Not just a hook pulling lower jaw.')
s=rect(0,875,1000,125,'#ddd')+person((380,535),(390,725),[(260,875),(500,875)],['365,590 485,680 615,505','395,590 330,650 365,690'])
s+=poly('535,510 600,420 875,380 990,535 875,650 665,585 620,505','#fff')+circle(615,505,42,'#b5232e')+line(580,550,615,505,'#b5232e',38)
s+=label(35,370,'one connected attacking arm')+label(635,735,'jaw dent at fist contact')+label(55,960,'grounded force through legs and hips')
panels['RC10']=(s,'One right fist contacts dented lower jaw. Trace torso/shoulder/elbow/fist and planted feet; no detached glove or full-body effect cloud.')
rows=[]
for ident,(body,brief) in panels.items():
 svg=D/(ident+'.svg');png=D/(ident+'.png');assert not svg.exists() and not png.exists()
 svg.write_text(header+label(25,45,ident+' · editable geometry reference')+label(25,80,'Keep drawing style from original anchor; do not render these labels.')+body+'</g></svg>')
 cairosvg.svg2png(url=str(svg),write_to=str(png))
 rows.append({'id':ident,'path':str(png.relative_to(R)),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'svg_path':str(svg.relative_to(R)),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'role':brief})
(D/'manifest.json').write_text(json.dumps({'schema':'PilotGeometryControls/1','controls':rows,'method':'Four code-authored editable SVG geometry controls; rasterized with CairoSVG. These are instructions, not generated artwork or claims of correct final anatomy.'},indent=2)+'\n')
print(json.dumps({'controls':len(rows)}))
