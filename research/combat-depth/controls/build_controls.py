#!/usr/bin/env python3
"""Original code-native blocking controls, not finished illustration."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
OUT=HERE/'v1'
C={'ink':'#293843','floor':'#eeeae1','stone':'#c1c7c8','dark':'#576675','water':'#8cbdcc','riven':'#236270','ilyra':'#824253','neris':'#32757a','kellan':'#cbb58b','enemy':'#797477','hair':'#dce7eb','ice':'#c9e8ee','violet':'#9274aa'}
parts=[]
def path(d,fill='none',stroke=None,w=4,extra=''):
 parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')
def rect(x,y,w,h,fill,stroke=None):parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="4"/>')
def circle(x,y,r,fill):parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{C["ink"]}" stroke-width="3"/>')
def poly(points,fill):path('M'+' L'.join(f'{x},{y}' for x,y in points)+' Z',fill)
def line(points,color,w=6):path('M'+' L'.join(f'{x},{y}' for x,y in points),stroke=color,w=w)
def limb(points,color,w=22):line(points,C['ink'],w+7);line(points,color,w)
def arrow(a,b,color=C['ink'],w=6):
 import math
 x,y=b;u,v=a;theta=math.atan2(y-v,x-u);line([a,b],color,w)
 poly([(x,y),(x-20*math.cos(theta-.5),y-20*math.sin(theta-.5)),(x-20*math.cos(theta+.5),y-20*math.sin(theta+.5))],color)
def start():
 parts.clear();rect(0,0,1200,800,'#faf9f4','#faf9f4')
def save(name):
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">'+''.join(parts)+'</svg>\n'
 p=OUT/(name+'.svg')
 with p.open('x') as f:f.write(svg)
 return {'id':name,'svg':str(p.relative_to(HERE)),'width':1200,'height':800,'svg_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def top_actor(x,y,color,facing=1,weapon=None):
 circle(x,y,22,color);poly([(x+facing*32,y),(x+facing*12,y-12),(x+facing*12,y+12)],C['ink'])
 if weapon=='saber':line([(x+facing*15,y+20),(x+facing*65,y+35)],C['ink'],7);line([(x+facing*25,y+22),(x+facing*65,y+33)],'#52b8ce',3)
 if weapon=='lance':line([(x-facing*35,y+25),(x+facing*85,y+25)],C['ink'],8);line([(x-facing*35,y+25),(x+facing*66,y+25)],'#f1efe1',4)
 if weapon=='shield':path(f'M{x+35},{y-30} Q{x+66},{y} {x+35},{y+30} Q{x+48},{y} {x+35},{y-30}',C['dark'])
def camera(x,y):poly([(x-22,y+18),(x+22,y+18),(x,y-18)],'#a3b0b4');line([(x,y-25),(x,y-52)],'#a3b0b4',3)
def person(head,shoulders,hips,arms,legs,color,hair=None):
 # Named projected joints remain editable. Head/hand shapes intentionally have no faces.
 for hip,knee,ankle,toe in legs:limb([hip,knee,ankle],C['dark'],23);limb([ankle,toe],C['ink'],20)
 poly([shoulders[0],shoulders[1],hips[1],hips[0]],color)
 for shoulder,elbow,hand in arms:limb([shoulder,elbow,hand],color,20);circle(*hand,12,'#ded2bf')
 neck=((shoulders[0][0]+shoulders[1][0])/2,(shoulders[0][1]+shoulders[1][1])/2)
 line([neck,head],color,24);circle(*head,27,'#e1d9c9')
 if hair:path(f'M{head[0]-25},{head[1]} Q{head[0]-28},{head[1]-35} {head[0]+8},{head[1]-27} Q{head[0]+28},{head[1]-20} {head[0]+25},{head[1]}',hair,w=2)
def sword(hilt,tip,cyan=False):
 dx,dy=tip[0]-hilt[0],tip[1]-hilt[1];n=(dx*dx+dy*dy)**.5;ux,uy=dx/n,dy/n;px,py=-uy,ux
 line([(hilt[0]-ux*34,hilt[1]-uy*34),hilt],C['ink'],10)
 line([(hilt[0]+px*20,hilt[1]+py*20),(hilt[0]-px*20,hilt[1]-py*20)],C['ink'],8)
 poly([(hilt[0]+px*7,hilt[1]+py*7),(tip[0],tip[1]),(hilt[0]-px*7,hilt[1]-py*7)],C['ink'])
 line([(hilt[0]+px*5,hilt[1]+py*5),tip],'#56c2d6' if cyan else '#e9e7dc',3)
def lance(base,tip,grip):
 line([base,tip],C['ink'],12);line([base,tip],'#e9e6d8',7)
 dx,dy=tip[0]-base[0],tip[1]-base[1];n=(dx*dx+dy*dy)**.5;ux,uy=dx/n,dy/n;px,py=-uy,ux
 poly([tip,(tip[0]-ux*65+px*20,tip[1]-uy*65+py*20),(tip[0]-ux*52,tip[1]-uy*52),(tip[0]-ux*65-px*20,tip[1]-uy*65-py*20)],C['dark'])
 line([(grip[0]-ux*24,grip[1]-uy*24),(grip[0]+ux*24,grip[1]+uy*24)],C['ink'],14)
def duel_floor():
 poly([(120,305),(1040,305),(1160,735),(40,735)],C['floor'])
 rect(110,205,130,190,C['stone']);poly([(80,415),(265,415),(295,460),(65,460)],'#dadad1')
 rect(1015,120,125,545,C['stone']);path('M1035,565 L1035,265 Q1077,195 1118,265 L1118,565',fill='#edece5')
 line([(245,305),(990,305)],C['stone'],24);line([(240,272),(990,272)],C['ink'],4)
 poly([(55,700),(1148,700),(1165,735),(40,735)],C['water'])
def shield(x,y):
 # Rear opening and real handle face LEFT. Convex solid face faces RIGHT.
 path(f'M{x-8},{y-110} Q{x+83},{y} {x-8},{y+110} Q{x+25},{y} {x-8},{y-110}',C['dark'],w=5)
 line([(x+2,y-25),(x+2,y+25)],C['ink'],9);line([(x-24,y),(x+2,y)],C['ink'],7)

OUT.mkdir(parents=True,exist_ok=False)
records=[]
start();rect(110,160,1010,500,C['floor']);rect(135,210,135,175,C['stone']);rect(120,410,190,80,'#dadad1');rect(1010,215,90,320,C['stone']);path('M1025,500 L1025,285 Q1055,230 1085,285 L1085,500',fill='#edece5');line([(300,175),(970,175)],C['stone'],28);rect(120,600,980,42,C['water']);top_actor(390,435,C['riven'],1,'saber');top_actor(790,435,C['ilyra'],-1,'lance');camera(600,742);records.append(save('map-duel'))
start();rect(120,165,960,485,C['floor']);rect(105,230,80,340,C['stone']);rect(105,330,80,125,'#faf9f4');rect(660,205,115,95,C['stone']);rect(185,565,875,45,C['water']);top_actor(555,425,C['neris'],1,'shield');top_actor(425,415,C['riven'],1,'saber');top_actor(450,530,C['kellan'],1,'saber');top_actor(820,400,C['enemy'],-1,'saber');top_actor(795,580,C['enemy'],-1,'saber');circle(1010,415,29,C['enemy']);poly([(987,400),(949,386),(949,443),(987,427)],'#b9a773');camera(600,740);records.append(save('map-squad'))
start();rect(0,125,210,445,C['stone']);rect(40,260,170,175,C['floor']);rect(210,285,940,140,C['floor']);rect(195,285,25,140,C['stone']);rect(465,285,25,140,C['stone']);rect(705,285,25,140,C['stone']);rect(945,285,25,140,C['stone']);rect(90,500,1080,185,C['water']);poly([(125,470),(255,470),(325,525),(195,525)],C['floor']);top_actor(480,350,C['neris'],1,'shield');top_actor(420,320,C['kellan'],1,'saber');top_actor(505,410,C['ilyra'],1,'lance')
for x in [280,315,350]:
 for y in [330,370]:circle(x,y,9,'#b5c2bb')
for x in [760,795,830]:
 for y in [322,355,388]:poly([(x-9,y),(x+8,y-9),(x+8,y+9)],C['enemy'])
# Four separate leg feet, one broad body, mouth faces WEST.
for x,y in [(985,298),(1080,298),(985,412),(1080,412)]:rect(x-13,y-14,26,28,C['dark'])
parts.append(f'<ellipse cx="1040" cy="355" rx="88" ry="45" fill="{C["dark"]}" stroke="{C["ink"]}" stroke-width="4"/>');rect(935,330,43,50,'#b9a773');arrow((675,460),(275,460),'#899f9d',4);camera(600,754);records.append(save('map-war'))

# D04: upright architecture; pull and falling water turn toward EAST/right wall.
start();duel_floor()
person((380,345),[(350,385),(408,385)],[(360,500),(407,500)],[((350,385),(326,448),(337,498)),((408,385),(452,433),(508,470))],[((360,500),(332,598),(300,690),(345,690)),((407,500),(420,592),(443,690),(485,690))],C['ilyra'],'#b46b4c');lance((525,697),(506,215),(516,469));circle(516,469,12,'#ded2bf')
person((795,333),[(746,370),(788,403)],[(656,500),(688,523)],[((746,370),(682,395),(674,441)),((788,403),(829,452),(845,489))],[((656,500),(627,554),(587,619),(632,617)),((688,523),(713,568),(690,640),(735,637))],C['riven'],C['hair']);sword((849,501),(991,573),True)
path('M650,255 C650,330 650,370 689,400 C750,435 860,434 1006,434',stroke=C['water'],w=19);arrow((772,570),(960,570),C['violet'],7);line([(584,645),(683,645)],'#b4b8b6',5);records.append(save('D04-gravity-east'))
# D10: kick physically meets planted butt; butt has a small new ground gap.
start();duel_floor()
person((386,300),[(354,345),(413,345)],[(391,480),(440,480)],[((354,345),(331,414),(344,465)),((413,345),(463,370),(527,388))],[((391,480),(360,590),(319,695),(370,698)),((440,480),(565,550),(676,631),(752,666))],C['riven'],C['hair']);sword((531,390),(702,278),True)
person((882,302),[(851,344),(909,346)],[(854,473),(901,475)],[((851,344),(825,394),(806,431)),((909,346),(869,433),(800,465))],[((854,473),(831,581),(811,688),(764,688)),((901,475),(951,580),(986,688),(1030,688))],C['ilyra'],'#b46b4c');lance((752,667),(848,156),(807,432));circle(807,432,12,'#ded2bf');circle(800,465,12,'#ded2bf');circle(752,667,8,'#da9c63');line([(735,692),(785,692)],'#b0b5b4',4);records.append(save('D10-butt-kick'))
# G03: rear grip left of shield, near shoulder displaced, outgoing load spills north.
start();poly([(100,320),(1100,320),(1160,725),(40,725)],C['floor']);rect(748,160,123,160,C['stone']);rect(160,640,930,45,C['water'])
person((530,290),[(493,335),(551,335)],[(504,463),(553,463)],[((493,335),(480,420),(465,466)),((551,335),(601,388),(636,422))],[((504,463),(442,559),(414,675),(459,675)),((553,463),(593,550),(639,622),(679,614))],C['neris'],'#514b49');shield(660,420);circle(636,422,12,'#ded2bf')
person((340,367),[(310,412),(366,398)],[(385,517),(426,498)],[((310,412),(388,383),(497,353)),((366,398),(416,453),(486,447))],[((385,517),(300,584),(232,703),(281,702)),((426,498),(489,594),(520,704),(562,704))],C['enemy'],'#5b5c60')
path('M706,411 Q801,402 834,328 Q845,289 800,258',stroke='#b3a48d',w=30);poly([(751,235),(774,256),(746,277)],'#9c9790');poly([(659,310),(675,323),(664,337)],'#faf9f4');arrow((404,335),(473,345),'#a9988d',4);records.append(save('G03-brace-break'))
# G04: both hilt grips, continuous water contact, one wedge under loaded foot.
start();poly([(100,300),(1110,300),(1175,730),(30,730)],C['floor']);rect(80,620,1085,65,C['water']);rect(1070,160,78,210,C['stone'])
person((390,292),[(353,333),(413,333)],[(371,467),(423,467)],[((353,333),(393,382),(471,409)),((413,333),(458,374),(489,432))],[((371,467),(313,580),(265,706),(310,706)),((423,467),(464,582),(500,706),(548,706))],C['kellan'],'#343b44');sword((500,451),(605,648));circle(471,409,12,'#ded2bf');circle(489,432,12,'#ded2bf')
poly([(634,660),(702,637),(808,565),(873,660)],C['ice']);line([(605,649),(661,648)],'#d6eff1',10)
person((965,281),[(917,325),(965,349)],[(823,459),(871,479)],[((917,325),(895,382),(916,419)),((965,349),(1013,388),(1034,434))],[((823,459),(795,519),(795,568),(842,585)),((871,479),(921,568),(974,686),(1019,686))],C['enemy'],'#5b5c60');arrow((896,477),(1000,460),'#a9988d',4);records.append(save('G04-water-foot-wedge'))
manifest={'schema':'CombatDepthCodeNativeControls/1','status':'Unreviewed initial code-native controls; actual PNG review required before use','not_final_art':True,'records':records,'legend':{'petrol':'Riven','burgundy':'Ilyra','teal':'Neris','sand':'Kellan','gray':'opponents/architecture','pale_blue':'existing water or opaque ice as shape indicates','violet_arrow':'physical direction of gravity; do not draw diagram arrow in final art'},'camera':'Maps north at top, south camera below; west is image-left and east image-right. Contacts are projected staging suggestions, not a 3D rig.','damage':{'D03_onward':'one notch in Ilyra ivory mantle','D05_onward':'Riven anatomical left sleeve abrasion plus one broad east-wall impact scar','G03_onward':'one upper shield rim chip'},'source_restriction':'No raster art or third-party visual input; original SVG paths generated by this source. PNGs must be rendered from these exact SVG hashes.'}
with (OUT/'manifest.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'output':str(OUT),'controls':len(records)}))
