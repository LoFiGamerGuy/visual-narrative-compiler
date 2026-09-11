from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P13';O=B/'F01-v3';O.mkdir();raw=Image.open(R/'production/structural-pilot/candidates/C00011-cd2b17c39141d6ab.png').convert('RGBA');base=Image.open(B/'F01/checkerboard-alpha.png').convert('L')
s=json.loads((B/'F01-v2/P13-F01-v2.spec.json').read_text());s['id']='SC-20260907-01-S-P13-F01-v3';s['output_svg']=str((O/'P13-F01-v3.svg').relative_to(R))
polys={'nera':[(730,220),(990,220),(1000,467),(1071,478),(1080,533),(1020,535),(992,540),(992,900),(1023,930),(1022,970),(730,970)],'odo':[(1016,194),(1260,194),(1260,965),(1120,965),(1100,915),(991,928),(987,896),(1019,880),(1037,660),(1034,542),(1010,450)]}
for n in ['nera','odo']:
 m=Image.new('L',raw.size);ImageDraw.Draw(m).polygon(polys[n],fill=255);m.putdata([min(a,b) for a,b in zip(m.getdata(),base.getdata())]);im=raw.copy()
 if n=='nera':
  p=m.load();rgb=raw.load()
  for y in range(440,550):
   for x in range(990,1081):
    r,g,b,a=rgb[x,y]
    if b>r*1.2 and b>g*1.1:p[x,y]=0
 else:
  clone=raw.crop((1080,435,1130,510)).resize((70,75));im.paste(clone,(1008,470));ImageDraw.Draw(m).rectangle([1008,470,1078,545],fill=255);clone.save(O/'odo-jacket-source-clone.png')
 im.putalpha(m);im.save(O/(n+'-matte.png'));m.save(O/(n+'-mask.png'))
 for l in s['layers']:
  if l['id']==n+'-source-actor':l['path']=str((O/(n+'-matte.png')).relative_to(R))
idx=next(i for i,l in enumerate(s['layers']) if l['id']=='fixed-staff-flask')
s['layers'].insert(idx,dict(id='odo-left-arm-support-correction',kind='explicit-conventional-vector-drawing',svg='<path d="M837 508 L848 519 L831 546 L816 553 L807 544 L820 535 Z" fill="#264f8e" stroke="#182738" stroke-width="1.7"/><path d="M815 537 L825 547 L816 556 L806 547 Z" fill="#d9c9a7" stroke="#292b2c" stroke-width="1.4"/><path d="M806 544 Q810 542 815 547 L817 552 Q813 561 805 558 L801 553 Z" fill="#aa7947" stroke="#3b2c20" stroke-width="1.3"/>'))
(O/'P13-F01-v3.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'mask_polygons_source_px':polys,'odo_jacket_clone_crop':[1080,435,1130,510],'clone_resize':[70,75],'clone_place':[1008,470],'purpose':'Remove duplicated source arm/boot fragments, repair torso where Nera source arm overlaps, and conventionally connect Odo support arm.','generation_calls':0},indent=2)+'\n')
