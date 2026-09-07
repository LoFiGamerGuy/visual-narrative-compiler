"""Original per-shot blocking art; editable SVG controls, never final candidates."""
from pathlib import Path
import json,math,hashlib
OUT=Path(__file__).resolve().parent/'v5'
INK='#303647';IVORY='#f5f0e5';STONE='#d3d5cb';SLATE='#8e9faa';WINE='#713750';PLUM='#785569';SKIN='#ead3c3';BROWN='#9b6353';BLUE='#313c58';PINK='#b76884';WOOD='#b28b5d'
def path(d,fill='none',stroke=INK,width=5):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
def ell(x,y,rx,ry,fill=IVORY,stroke=INK,width=5):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def line(points,color=IVORY,width=30):
 d='M'+' L'.join(f'{x},{y}' for x,y in points)
 return path(d,'none',INK,width+7)+path(d,'none',color,width)
def hand(x,y,angle=0,color=SKIN):return f'<g transform="translate({x} {y}) rotate({angle})">'+ell(0,0,15,23,color,width=4)+path('M-9,-9 L8,-9 M-10,-1 L9,-1','none',INK,2)+'</g>'
def head(x,y,scale=1,mara=False,expression='neutral'):
 c=BROWN if mara else SKIN;hair=BLUE if mara else WINE
 s=f'<g transform="translate({x} {y}) scale({scale})">'
 if mara:s+=path('M-30,-25 Q-57,45 -29,114 Q-2,126 -17,72','none',hair,23)
 else:s+=path('M-26,-27 Q-66,20 -48,130','none',hair,23)
 s+=path('M-34,-48 Q3,-68 35,-31 L39,-1 L49,7 L35,15 Q30,50 -2,45 Q-32,37 -37,6 Z',c)
 s+=path('M-37,2 Q-56,-59 -3,-65 Q35,-60 36,-26 Q8,-46 -15,-28 L-26,10 Z',hair)
 s+=ell(24,-3,3,3,INK,INK,1)
 if expression=='startled':s+=ell(22,-3,7,9,IVORY,INK,2)+ell(23,-2,2,4,INK,INK,1)+path('M13,-22 L31,-25','none',INK,3)+ell(23,25,5,7,c,INK,3)
 elif expression=='deadpan':s+=path('M16,-20 L31,-25 M18,24 L31,24','none',INK,3)
 else:s+=path('M17,23 Q26,27 32,20','none',INK,2)
 if not mara:s+=ell(-22,19,4,5,IVORY,INK,2)
 return s+'</g>'
def wheel(cx,cy,rx,ry,rotation=0,broken=False,scale=1):
 s=path(f'M{cx-23},{cy+ry-5} L{cx-30},{cy+ry+135} L{cx+33},{cy+ry+135} L{cx+24},{cy+ry-5}',SLATE)
 s+=ell(cx,cy,rx,ry,SLATE,width=7)+ell(cx,cy,rx-17,ry-20,IVORY,width=4)
 for a in (0,120,240):
  t=math.radians(a+rotation);s+=line([(cx,cy),(cx+math.cos(t)*(rx-18),cy+math.sin(t)*(ry-20))],SLATE,12)
 s+=ell(cx,cy,22,24,SLATE,width=4)
 t=math.radians(rotation);mount=(cx+math.cos(t)*rx,cy+math.sin(t)*ry)
 dx,dy=-60*scale,60*scale
 if broken:dx*=5/18;dy*=5/18
 s+=line([mount,(mount[0]+dx,mount[1]+dy)],WOOD,16*scale)
 if broken:s+=path(f'M{mount[0]+dx-7},{mount[1]+dy-6} l5,7 4,-4 5,5','none',INK,2)
 return s

def close(broken):
 s=path('M20,0 L20,850 M90,0 L90,850 M0,690 L900,690','none',STONE,5)
 s+=path('M800,100 L890,55 L890,720 L800,775 Z',STONE,SLATE,3)
 s+=wheel(600,490,165,200,broken=broken)
 # Iven torso turned toward the wheel. The two shoulder origins remain separate.
 s+=path('M340,225 Q395,202 472,245 L495,430 L454,598 L330,578 L319,397 Z',PLUM)
 s+=path('M336,566 L399,580 L389,920 L316,920 Z',INK)+path('M405,576 L463,585 L502,920 L433,920 Z',INK)
 s+=line([(359,242),(372,328),(517,317)],IVORY,45)
 s+=hand(517,317,70)
 if broken:
  s+=line([(439,264),(550,410),(381,432)],IVORY,44)
  s+=line([(403,410),(360,453)],WOOD,17)
  s+=path('M397,406 l4,9 4,-4 5,4','none',INK,2)
  s+=hand(381,432,44)
 else:
  s+=line([(439,264),(548,452),(716,538)],IVORY,44)
  s+=hand(717,537,43)
 s+=head(390,164,.98,expression='startled' if broken else 'neutral')
 return s

def svg(name,w,h,vb,content):
 text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}"><rect x="-3000" y="-3000" width="7000" height="7000" fill="{IVORY}"/>{content}</svg>\n'
 p=OUT/(name+'.svg')
 with p.open('x') as f:f.write(text)
 return p

def landing(raised=0):
 s=path('M0,360 L1200,270 L1200,570 L0,660 Z','#bdd0cf',SLATE,3)
 s+=path('M0,660 L1200,570 L1200,1300 L0,1300 Z',IVORY,SLATE,4)
 s+=path('M0,360 L1200,270 L1200,220 L0,310 Z',STONE,SLATE,3)
 s+=path('M0,680 L1200,590 M100,900 L530,620 M730,950 L950,605','none',STONE,3)
 # One arch. Sluice retracts upward behind it; open region stays visibly water.
 near=598-raised;far=361-raised
 s+=path(f'M772,208 L929,86 L929,{far} L772,{near} Z',SLATE)
 for t in (.25,.5,.75):
  x=772+157*t;y=208-122*t;b=near+(far-near)*t
  if b>y:s+=path(f'M{x},{y} L{x},{b}','none','#6b8290',3)
 s+=path('M730,616 L730,285 Q736,195 850,110 Q960,45 960,174 L960,351 L929,368 L929,190 Q929,134 865,174 Q772,230 772,311 L772,604 Z',STONE)
 s+=path('M730,285 L772,311 M850,110 L865,174 M960,174 L929,190','none',SLATE,3)
 return s

def creature(x,y,scale=1):
 s=f'<g transform="translate({x} {y}) scale({scale})">'
 for d in ['M-65,15 C-105,65 -165,30 -205,55','M-15,27 C-40,90 -115,55 -145,98','M35,28 C10,100 -45,95 -55,122','M85,12 C115,55 100,100 50,125']:
  s+=path(d,'none',INK,25)+path(d,'none','#acb9c7',18)
 s+=ell(0,0,111,40,'#80939f',INK,4)
 s+=path('M-114,-4 Q-127,-125 -15,-135 Q94,-137 119,-18 Q81,13 8,2 Q-65,19 -114,-4 Z','#d8d1e0',INK,4)
 s+=path('M-98,-31 Q-15,-56 99,-33','none','#a99caf',3)
 s+=ell(109,3,38,28,'#b6c1bd',INK,4)+ell(122,-4,3,4,INK,INK,1)+path('M122,17 Q134,20 141,11','none',INK,2)
 return s+'</g>'

def actor(x,y,scale=1,mara=False,arms=None,remnant=False,expression='neutral',look_left=False,open_left=False,open_right=False):
 # Coordinates local to floor center; all arms supplied shoulder-elbow-contact.
 s=f'<g transform="translate({x} {y}) scale({scale})">';skin=BROWN if mara else SKIN
 if mara:
  s+=path('M-53,-159 L6,-145 L-37,-16 L-72,-16 Z',PINK)+path('M4,-148 L56,-160 L90,-15 L55,-15 Z',PINK)
  s+=path('M-58,-239 Q-13,-259 52,-230 Q79,-190 53,-151 Q5,-122 -63,-154 Z',IVORY)
  s+=line([(-70,-12),(-37,-12)],BROWN,16)+line([(55,-12),(92,-12)],BROWN,16)
  s+=path('M-67,-22 L-47,-4 M65,-22 L82,-4','none',INK,3)
 else:
  s+=path('M-33,-151 L2,-145 L-10,-4 L-43,-4 Z',INK)+path('M6,-147 L38,-154 L52,-4 L19,-4 Z',INK)
  s+=path('M-38,-235 Q0,-256 39,-229 L42,-147 L-40,-145 Z',PLUM)
  s+=line([(-42,-4),(-7,-4)],INK,15)+line([(21,-4),(57,-4)],INK,15)
 if arms is None:arms=[[(-38,-227),(-58,-172),(-49,-120)],[(38,-225),(66,-176),(63,-120)]]
 for a in arms:s+=line(a,skin if mara else IVORY,23 if mara else 25)
 if remnant:
  hx,hy=arms[1][-1];s+=line([(hx-5,hy-13),(hx+5,hy+13)],WOOD,10)
 for index,a in enumerate(arms):
  hx,hy=a[-1]
  if index==1 and open_right:
   s+=f'<g transform="translate({hx} {hy}) scale(.8)">'+path('M-9,12 L-19,-2 Q-23,-9 -18,-10 L-9,-3 L-12,-22 Q-12,-28 -7,-26 L-3,-11 L-3,-30 Q0,-36 4,-31 L5,-11 L10,-28 Q15,-31 16,-25 L12,-7 L19,-18 Q24,-19 23,-13 L16,9 Q4,20 -9,12 Z',skin,INK,3)+'</g>'
  elif index==0 and open_left:
   s+=f'<g transform="translate({hx} {hy})">'+path('M-9,11 L-9,-7 Q-9,-13 -5,-13 L-4,-20 Q-1,-24 2,-20 L3,-14 Q8,-17 10,-12 L12,3 L7,14 Z',skin,INK,3)+'</g>'
  else:s+=f'<g transform="translate({hx} {hy}) scale(.6)">'+hand(0,0,0,skin)+'</g>'
 s+=('<g transform="scale(-1 1)">' if look_left else '')+head(0,-285,.8,mara,expression)+('</g>' if look_left else '')
 if mara:s+=path('M-50,-222 L-37,-221','none','#627c9f',9)
 return s+'</g>'

def wide_start():
 s=landing(0)+creature(350,470,.8)+wheel(640,510,60,78,scale=.4)
 s+=actor(150,766,1.0,True)
 s+=actor(557,735,1.05,open_right=True,arms=[[(-38,-227),(-52,-170),(-37,-120)],[(38,-225),(94,-261),((611-557)/1.05,(405-735)/1.05)]])
 return s

def action():
 s='<g transform="translate(-70 60) scale(.86)">'+landing(100)+'</g>'
 s+=creature(215,425,.59)
 s+=wheel(610,650,95,120,45,True,.63)
 s+=actor(170,975,.85,remnant=True,arms=[[(-38,-227),(-58,-174),(-49,-115)],[(38,-225),(76,-196),(76,-150)]])
 # Both hands land exactly on left rim and upper-right rim.
 s+=actor(418,1030,1.4,True,arms=[[(-38,-227),(-14,-248),((515-418)/1.4,(650-1030)/1.4)],[(38,-225),(106,-263),((657.5-418)/1.4,(546.077-1030)/1.4)]])
 return s

def passage():
 s=landing(175)+wheel(640,510,60,78,90,True,.4)
 s+=creature(948,480,.77)
 s+=actor(537,733,1.0,remnant=True,arms=[[(-38,-227),(-57,-175),(-40,-120)],[(38,-225),(69,-185),(79,-135)]])
 # Mara's open left palm meets the near shell edge, feet remain on dry ledge.
 s+=actor(1090,690,1.1,True,open_left=True,arms=[[(-38,-227),((1025-1090)/1.1,(470-690)/1.1),((982-1090)/1.1,(499-690)/1.1)],[(38,-225),(79,-175),(77,-120)]])
 return s

def payoff():
 s=path('M-500,0 L2200,0 L2200,700 L-500,950 Z','#bdd0cf',SLATE,3)
 s+=path('M-500,900 L2200,700 L2200,1600 L-500,1600 Z',IVORY,SLATE,3)
 # Small open arch placed in the inter-person gap, visible above the held remnant.
 s+='<g transform="translate(263 340) scale(.4)">'
 s+=path('M772,208 L929,86 L929,186 L772,423 Z',SLATE)
 s+=path('M730,616 L730,285 Q736,195 850,110 Q960,45 960,174 L960,351 L929,368 L929,190 Q929,134 865,174 Q772,230 772,311 L772,604 Z',STONE)
 s+='</g>'
 s+=actor(390,1060,2.0,remnant=True,arms=[[(-38,-227),(-65,-184),(-52,-135)],[(38,-225),(90,-196),(97,-247)]])
 s+=actor(730,1060,2.0,True,look_left=True,expression='deadpan',arms=[[(-38,-227),(-69,-184),(-50,-135)],[(38,-225),(68,-183),(54,-135)]])
 return s

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 svg('P01',1200,800,'0 0 1200 800',wide_start())
 svg('P02',1000,1000,'0 0 900 900',close(False))
 svg('P03',1200,900,'230 70 800 600',close(True))
 svg('P04',900,1125,'0 0 900 1125',action())
 svg('P05',1200,800,'0 0 1200 800',passage())
 svg('P06',1200,900,'230 350 660 495',payoff())
