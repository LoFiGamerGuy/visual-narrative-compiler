from pathlib import Path
import json,math,hashlib,html
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'production/anchor-return/controls'; PLAN=ROOT/'production/anchor-return/plan.json'; P=json.loads(PLAN.read_text()); E={e['id']:e for e in P['entries'] if e['category']=='encounter'}
W,H=1200,800
C={'ink':'#233344','muted':'#85909a','ground':'#e4e8e6','a':'#d6e2df','b':'#c49caa','right':'#a46b16','left':'#367891','force':'#de7047','tether':'#00a3bb'}
def esc(t):return html.escape(str(t))
def poly(p,fill,stroke=None,width=2,extra=''):return f'<polygon points="{" ".join(f"{x},{y}" for x,y in p)}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{width}" {extra}/>'
def line(p,color=None,w=4,dash=None):return f'<polyline points="{" ".join(f"{x},{y}" for x,y in p)}" fill="none" stroke="{color or C["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def ellipse(x,y,rx,ry,fill,stroke=None,w=3):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{w}"/>'
def text(x,y,t,size=17,color=None):return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color or C["ink"]}">{esc(t)}</text>'
def path(d,fill='none',stroke=None,w=4):return f'<path d="{d}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
def arrow(a,b,color=None,w=5):
 color=color or C['force'];x,y=b;ang=math.atan2(y-a[1],x-a[0]);size=14
 return line([a,b],color,w)+poly([(x,y),(x-size*math.cos(ang-.45),y-size*math.sin(ang-.45)),(x-size*math.cos(ang+.45),y-size*math.sin(ang+.45))],color,color,1)
def contact(p,label=None,ringonly=False):
 x,y=p;s=ellipse(x,y,17,17,'#fff8e8',C['force'],4)+line([(x-6,y),(x+6,y)],C['force'],2)+line([(x,y-6),(x,y+6)],C['force'],2)
 if ringonly:s=ellipse(x,y,25,25,'none',C['force'],3)
 return s+(text(x+22,y-19,label,15,C['force']) if label else '')
def support(p):
 x,y=p;return line([(x-19,y+8),(x+19,y+8)],'#407662',5)+poly([(x,y+10),(x-6,y+21),(x+6,y+21)],'#407662','#407662')
def labelhand(p,label,side,dx=15,dy=-15):
 x,y=p;co=C['right' if side=='R' else 'left'];return line([(x,y),(x+dx,y+dy)],co,1.5)+text(x+dx+2,y+dy-2,label,14,co)
def human(p,name='A',fill=None,face=1,scale=1,tear=None,gauntlet=False,charged=False,chip=False,coat=False):
 fill=fill or C['a'];s=''; lw=24*scale; armw=16*scale;shR,shL=p['rs'],p['ls'];hipR,hipL=p['rh'],p['lh'];hx,hy=p['head']
 # complete far-side leg/arm before torso, then near chains. Both sides remain traceable.
 for side in ['l','r']:
  s+=line([p[side+'h'],p[side+'k'],p[side+'f']],C['ink'],lw+5)+line([p[side+'h'],p[side+'k'],p[side+'f']],fill,lw)
  fx,fy=p[side+'f'];s+=line([(fx-8*scale,fy),(fx+18*scale*face,fy)],C['ink'],10*scale)
 s+=poly([shR,shL,hipL,hipR],fill,C['ink'],3)
 if coat:
  a=hipL;b=hipR;s+=poly([a,(a[0]-18*face,a[1]+65*scale),(a[0]-42*face,a[1]+86*scale),(b[0]-14*face,b[1]+15*scale)],fill,C['ink'],2)
 for side in ['l','r']:
  pts=[p[side+'s'],p[side+'e'],p[side+'w']];s+=line(pts,C['ink'],armw+4)+line(pts,fill,armw)
  s+=line(pts,C['left' if side=='l' else 'right'],2.5)
  wx,wy=p[side+'w'];s+=ellipse(wx,wy,(16 if gauntlet else 8)*scale,(16 if gauntlet else 8)*scale,('#c76559' if gauntlet else '#eee9df'),C['ink'],2)
  if gauntlet:
   if side=='r':s+=ellipse(wx,wy,8*scale,8*scale,'#fff5d8',C['right'],1.4)
   else:s+=path(f'M {wx+5*scale},{wy-9*scale} A {10*scale},{10*scale} 0 1 0 {wx+5*scale},{wy+9*scale} A {7*scale},{9*scale} 0 0 1 {wx+5*scale},{wy-9*scale}', '#fff5d8','#fff5d8',1)
   if side=='l' and chip:s+=poly([(wx-15*scale,wy),(wx-4*scale,wy+6*scale),(wx-13*scale,wy+13*scale)],'#f5f4ed',C['ink'],1)
  s+=labelhand((wx,wy),name+' '+side.upper(),side.upper(),20*scale if side=='r' else -36*scale,-18*scale if side=='r' else 27*scale)
 s+=line([((shR[0]+shL[0])/2,(shR[1]+shL[1])/2),(hx,hy+21*scale)],C['ink'],12*scale)
 s+=ellipse(hx,hy,24*scale,29*scale,'#eee9df',C['ink'],3)
 s+=poly([(hx+face*18*scale,hy-5*scale),(hx+face*32*scale,hy+5*scale),(hx+face*17*scale,hy+9*scale)],'#eee9df',C['ink'],2)
 s+=ellipse(hx+face*10*scale,hy-4*scale,2.5*scale,2.5*scale,C['ink'],C['ink'],1)
 if tear:
  tx,ty=tear;s+=poly([(tx-8,ty-8),(tx+13,ty),(tx-4,ty+14)],'#f5f4ed',C['force'],2)
 if charged:
  x,y=p['rw'];s+=ellipse(x,y,23*scale,23*scale,'none','#fffdf2',6)+ellipse(x,y,26*scale,26*scale,'none',C['tether'],2)
 return '<g id="pose-'+name+'">'+s+'</g>'
def pose(head,rs,ls,re,le,rw,lw,rh,lh,rk,lk,rf,lf):return dict(zip(['head','rs','ls','re','le','rw','lw','rh','lh','rk','lk','rf','lf'],[head,rs,ls,re,le,rw,lw,rh,lh,rk,lk,rf,lf]))
def standing(x,y,s=1,face=1):
 def q(a,b):return (x+a*s,y+b*s)
 return pose(q(0,-220),q(-20,-182),q(20,-184),q(-43,-130),q(49,-132),q(-22,-90),q(67,-90),q(-15,-95),q(15,-95),q(-37,-42),q(49,-43),q(-45,0),q(61,0))
def sword(hand,tip):
 x,y=hand;dx=tip[0]-x;dy=tip[1]-y;n=math.hypot(dx,dy);ux,uy=dx/n,dy/n;px,py=-uy,ux;pom=(x-ux*27,y-uy*27);start=(x+ux*17,y+uy*17)
 s=line([pom,start],C['ink'],7)+line([(start[0]-px*10,start[1]-py*10),(start[0]+px*10,start[1]+py*10)],C['ink'],4)
 s+=poly([(start[0]-px*6,start[1]-py*6),(tip[0]-ux*12-px*10,tip[1]-uy*12-py*10),tip,(start[0]+px*6,start[1]+py*6)],'#f8faf9',C['ink'],2)
 s+=ellipse(*pom,5,5,C['tether'],C['ink'],1);return s,pom
 defunused=0
def spear(a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy);ux,uy=dx/n,dy/n;px,py=-uy,ux;neck=(b[0]-ux*35,b[1]-uy*35)
 return line([a,neck],C['ink'],7)+poly([b,(neck[0]+px*10,neck[1]+py*10),(neck[0]-ux*7,neck[1]-uy*7),(neck[0]-px*10,neck[1]-py*10)],'#f7f7f0',C['ink'],2)
def tether(pom,anchor,slack=False):
 s=ellipse(*anchor,9,9,'#f5f4ed',C['tether'],3)
 if slack:s+=path(f'M {pom[0]} {pom[1]} Q {(pom[0]+anchor[0])/2} {max(pom[1],anchor[1])+110} {anchor[0]} {anchor[1]}',stroke=C['tether'],w=4)
 else:s+=line([pom,anchor],C['tether'],4)
 return s

def bg(seq,wide=False,over=False):
 s='<rect width="1200" height="800" fill="#f5f4ed"/>'
 if seq=='NG':
  if wide:
   for x,y,w,h in [(240,160,65,250),(470,265,80,180),(730,225,70,260),(920,180,55,330)]:
    s+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e6eaea" stroke="#c0cccf" stroke-width="2"/>'+line([(x+w*.5,y+25),(x+w*.5,y+h-30)],'#bbd4d8',5)
  s+=poly([(0,250),(1200,360),(1200,745),(0,615)],'#e5e9e7','#b3bdc2',2) if (over or wide) else '<rect x="0" y="565" width="1200" height="185" fill="#e5e9e7"/>'
  s+=(line([(0,420),(1200,565)],'#a5b0b8',5)+line([(0,600),(1200,745)],'#a5b0b8',5) if wide else line([(0,560),(1200,560)],'#a5b0b8',5)+line([(0,685),(1200,685)],'#a5b0b8',5))
  s+='<rect x="45" y="155" width="100" height="405" fill="#d5dfe1" stroke="#7f929c" stroke-width="3"/>'
  s+=path('M 1050 560 L 1050 180 Q 1100 100 1150 180 L 1150 560',stroke='#7f929c',w=12)
  s+=text(42,135,'LIFT',14,'#7b8c96')+text(1040,120,'DOOR',14,'#7b8c96')
  for x in [110,1080]:s+=line([(x,555),(x,475)],'#7f929c',7)+ellipse(x,485,8,8,'#f5f4ed','#7f929c',2)
  if wide:s+=path('M 340 205 Q 490 125 615 182 Q 753 115 895 198 Q 700 161 615 218 Q 481 169 340 205','#dde7e8','#a4b8c0',2)
 elif seq=='BP':
  s+='<rect x="0" y="590" width="1200" height="160" fill="#e1d7dd"/>'
  s+=path('M 100 590 L 100 190 Q 155 110 210 190 L 210 590',stroke='#b1a8b1',w=9)
  s+=path('M 945 590 L 945 180 Q 1020 90 1090 172 M 1130 238 L 1130 590',stroke='#b1a8b1',w=9)
  s+=text(75,110,'PALE DOOR',14,'#8c7e8a')+text(935,95,'BROKEN ARCH',14,'#8c7e8a')
 else:
  s+=path('M 0 570 Q 300 470 570 550 Q 920 450 1200 530 L 1200 745 L 0 745 Z','#dce5d4','#b6c2ab',2)
  s+=poly([(0,610),(1200,590),(1200,745),(0,745)],'#ede3cb','#c5bca5',2)
  s+=line([(80,635),(80,455)],'#aaa08d',12)+text(40,430,'POST',14,'#9c917c')
  s+=ellipse(1100,585,70,48,'#c6d7e1','#92a9b6',3)+text(1070,520,'ROCK',14,'#8d9ea7')
  if wide:
   for x,y in [(180,495),(930,430)]:s+=line([(x,y),(x,y+65)],'#b2bbac',4)+line([(x-23,y-23),(x+23,y+23)],'#b2bbac',4)+line([(x+23,y-23),(x-23,y+23)],'#b2bbac',4)
 return s

def ng(n):
 s=bg('NG',n in [1,8],n==5);supports=[];contracts=[];tears=[]
 if n==1:
  a=standing(365,606,.35);b=standing(865,643,.38,-1);b['rw']=(832,589);b['lw']=(825,614);b['re']=(840,576);b['le']=(853,602);s+=human(a,'A',scale=.35)+human(b,'B',C['b'],face=-1,scale=.38,coat=True);sw,pom=sword(a['rw'],(414,571));s+=sw+spear((815,650),(846,540));supports=[a['rf'],a['lf'],b['rf'],b['lf']]
 elif n==2:
  a=pose((355,310),(331,345),(376,341),(332,405),(408,400),(390,430),(431,430),(345,453),(384,452),(290,535),(463,544),(262,626),(488,626));b=pose((853,308),(829,343),(868,344),(780,399),(843,407),(749,432),(833,438),(834,456),(870,456),(813,541),(920,548),(800,626),(946,626));s+=human(a)+human(b,'B',C['b'],face=-1,coat=True);sw,pom=sword(a['rw'],(493,409));s+=sw+spear((910,443),(635,423))+tether(pom,(110,485));supports=[a['rf'],a['lf'],b['rf'],b['lf']];s+=arrow((380,455),(318,467),C['tether'],3)
 elif n==3:
  a=pose((464,346),(426,363),(465,384),(476,375),(387,421),(544,389),(352,442),(390,447),(428,469),(327,536),(529,528),(260,608),(548,626));b=pose((786,310),(750,355),(799,349),(702,372),(813,434),(677,413),(763,466),(745,467),(788,457),(708,532),(883,524),(686,618),(945,625));s+=human(a)+human(b,'B',C['b'],face=-1,coat=True);sw,pom=sword(a['rw'],(750,442));s+=sw+spear((822,502),(605,359))+tether(pom,(110,485))+contact((718,434));supports=[a['rf'],a['lf'],b['lf']];s+=arrow((295,365),(390,360))
 elif n==4:
  a=pose((401,296),(390,350),(435,342),(298,389),(437,403),(282,452),(462,448),(373,499),(430,503),(323,625),(481,621),(320,725),(545,725));b=pose((684,266),(650,319),(704,321),(571,342),(684,390),(513,376),(660,431),(673,489),(723,474),(605,609),(801,602),(547,725),(857,725));s+=human(a,scale=1.25,tear=(439,353))+human(b,'B',C['b'],face=-1,scale=1.25,coat=True);sw,pom=sword(a['rw'],(190,506));s+=sw+spear((727,456),(386,326))+tether(pom,(110,485),True)+contact((436,345));supports=[a['rf'],a['lf'],b['rf'],b['lf']];s+=arrow((595,298),(466,318))
 elif n==5:
  a=pose((546,510),(518,542),(560,541),(450,520),(558,546),(410,482),(575,559),(520,577),(552,585),(432,612),(648,634),(388,683),(692,673));b=pose((829,290),(805,326),(851,335),(701,329),(787,372),(652,334),(755,345),(831,405),(872,415),(741,444),(958,444),(676,484),(1012,490));s+=human(a,tear=(560,541))+human(b,'B',C['b'],face=-1,coat=True);sw,pom=sword(a['rw'],(304,461));s+=sw+spear((919,364),(380,305))+tether(pom,(1080,485));supports=[a['rf'],a['lf'],b['rf'],b['lf']];s+=arrow((440,575),(525,636))+arrow((600,335),(480,324))
 elif n==6:
  a=pose((349,335),(326,370),(369,371),(398,392),(341,436),(494,410),(364,449),(334,467),(380,480),(287,550),(443,552),(246,635),(478,638));b=pose((739,337),(704,363),(759,382),(677,405),(798,427),(642,411),(760,457),(735,469),(790,473),(693,563),(866,543),(675,643),(913,603));s+=human(a,tear=(369,371))+human(b,'B',C['b'],face=-1,coat=True);sw,pom=sword(a['rw'],(755,440));s+=sw+spear((824,482),(563,380))+tether(pom,(1080,485))+contact((701,434))+arrow((510,414),(595,425),C['tether'],3);supports=[a['rf'],a['lf'],b['rf']];s+=arrow((687,315),(801,351))+arrow((950,645),(920,607),C['muted'],3)
 elif n==7:
  a=pose((353,384),(321,421),(365,420),(337,514),(372,453),(394,622),(385,477),(303,522),(351,535),(302,633),(423,573),(380,667),(452,644));b=pose((795,353),(778,398),(825,390),(860,453),(800,540),(918,481),(788,633),(820,515),(862,522),(827,632),(954,585),(900,663),(1009,640));s+=human(a,tear=(365,420))+human(b,'B',C['b'],face=-1,coat=True);sw,pom=sword(a['rw'],(486,652));s+=sw+spear((900,487),(1115,450))+line([pom,(pom[0]-29,pom[1]+3)],'#a6d9db',3);supports=[a['rk'],a['lf'],b['rk'],b['lf'],b['lw']]
 else:
  a=standing(985,666,.35);b=standing(1160,672,.35,-1);b['rw']=(1135,615);b['re']=(1140,610);b['lw']=(1128,650);b['le']=(1167,640);a['lw']=(992,608);a['le']=(1003,623);s+=human(a,scale=.35,tear=(992,602))+human(b,'B',C['b'],face=-1,scale=.35,coat=True);sw,pom=sword(a['rw'],(1041,638));s+=sw+spear((1124,674),(1147,565));supports=[a['rf'],a['lf'],b['rf'],b['lf']]
 for p in supports:s+=support(p)
 if n==4:s='<g transform="translate(-230,-160) scale(1.55)">'+s+'</g>'
 if n==5:s='<g transform="translate(110,80) skewX(-9) scale(1,.83)">'+s+'</g>'
 return s,{'support_points':supports,'anatomical_hands':{'A_RIGHT':a['rw'],'A_LEFT':a['lw'],'B_RIGHT':b['rw'],'B_LEFT':b['lw']},'weapon_ownership':'A right-hand sword; B two-handed spear except recovery single right hand','limitations':'Symbolic perspective and mannequin anatomy; control supports staging, not a final anatomy guarantee.'}

def save(id,body,meta):
 e=E[id];body+=text(26,35,id+'  /  '+e['scale'],19)+text(26,774,'STAGING ONLY  ·  R amber / L blue  ·  green = support  ·  orange = motion/contact',15,'#71818a')
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img"><title>{esc(id+" original pose and contact staging")}</title><desc>{esc(e["contact_contract"]+"; "+e["current_state"])}</desc><rect width="1200" height="800" fill="#f5f4ed"/>'+body+'</svg>'
 (OUT/(id+'.svg')).write_text(svg);data={'id':id,'svg_path':str((OUT/(id+'.svg')).relative_to(ROOT)),'png_path':str((OUT/(id+'.png')).relative_to(ROOT)),'width':W,'height':H,'contact_contract':e['contact_contract'],'current_state':e['current_state'],'camera':e['scale'],'source':'Original editable vector composition drawn from plan; no previous art or external image input','plan_sha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),**meta};(OUT/(id+'.json')).write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':
 import sys
 if any(g in ['BP','ST'] for g in sys.argv[1:]):
  from controls_more import bp
  if 'ST' in sys.argv[1:]:
   from controls_more import st
 groups=sys.argv[1:] or ['NG']
 for group in groups:
  fn=globals()[group.lower()]
  for n in range(1,9):save(f'{group}{n:02}',*fn(n))
 print('Built',groups)
