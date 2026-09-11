import json
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4]; B=R/'production/structural-pilot/finishing/S/P14'; O=B/'F01-v3';O.mkdir()
src=Image.open(R/'production/structural-pilot/candidates/C00007-05e9227e2675c85a.png').convert('RGBA')
def piece(name,box,poly,div):
 im=src.crop(box); m=Image.new('L',im.size);d=ImageDraw.Draw(m)
 for p in poly:d.polygon([(x/div,y/div) for x,y in p],fill=255)
 im.putalpha(m);im.save(O/(name+'.png'));m.save(O/(name+'-mask.png'))
piece('odo-hand',(894,842,1038,1053),[[(213,11),(391,65),(387,182),(376,327),(345,405),(280,473),(210,531),(173,530),(173,511),(231,481),(153,504),(94,487),(92,466),(204,432),(255,393),(150,435),(95,444),(77,427),(77,406),(156,373),(205,337),(242,308),(260,263),(260,221),(224,239),(217,204),(222,173),(210,144),(194,127)],[(62,259),(72,283),(84,343),(68,366),(43,374),(37,360),(44,327),(38,300)]],3)
piece('nera-hand',(448,900,550,1055),[[(112,130),(247,69),(284,221),(354,341),(353,462),(328,472),(302,431),(277,408),(268,462),(248,503),(219,510),(204,496),(198,423),(190,376),(177,342),(158,311),(140,261),(103,230)],[(105,356),(117,357),(125,382),(118,404),(151,373),(167,391),(159,420),(181,430),(189,463),(203,486),(211,519),(183,536),(149,525),(139,484),(108,478),(100,451),(92,451),(82,432),(87,399)]],4)
# Conventional clone from unobstructed fabric, under the erased original vial region.
p=src.crop((772,1010,892,1220)).resize((160,345));p.save(O/'trouser-source-clone.png')
s=json.loads((B/'F01-v2/P14-F01-v2.spec.json').read_text());s['id']='SC-20260907-01-S-P14-F01-v3';s['output_svg']=str((O/'P14-F01-v3.svg').relative_to(R))
for l in s['layers']:
 if l['id']=='odo-trouser-underpaint-in-removed-prop-region':
  l.clear();l.update(id='odo-source-bound-trouser-clone',path=str((O/'trouser-source-clone.png').relative_to(R)),width=160,height=345,transform='translate(855 975)',kind='explicit-conventional-source-clone')
 if l['id']=='nera-anatomical-left-forearm-and-grip':
  lines=l['svg'].splitlines();l['svg']='\n'.join(lines[:3]+lines[-1:])
 if l['id']=='odo-right-forearm-and-flask-grip':
  l['svg']='<path d="M1022 766 Q1055 790 1045 827 L1037 858 L986 843 L984 798 Z" fill="#224b8b" stroke="#172331" stroke-width="3"/><path d="M983 784 L1042 805 L1036 832 L980 811 Z" fill="#d8c8a5" stroke="#2c2b28" stroke-width="3"/>'
for name,w,h,transform in [('nera-hand',102,155,'matrix(.7 0 0 .7 553.2 1082.5)'),('odo-hand',144,211,'matrix(.8 0 0 .8 927.4 762.8)')]:
 s['layers'].append(dict(id='source-drawn-'+name,path=str((O/(name+'.png')).relative_to(R)),width=w,height=h,transform=transform,kind='explicit-source-hand-mask-and-affine'))
(O/'P14-F01-v3.spec.json').write_text(json.dumps(s,indent=2)+'\n')
(O/'revision-receipt.json').write_text(json.dumps(dict(source='C00007-05e9227e2675c85a.png',revision='Replace crude vector palms with original source-drawn hand regions; retain independent fixed metric staff and flask; clone original trouser fabric beneath removed source prop.',generation_calls=0,source_clone_crop=[772,1010,892,1220],source_masks='Saved alpha masks alongside hand crops; mask polygon coordinates in refine_p14_v3.py.',limitation='Hands are manually registered; cannot infer acceptance from anchor mapping.'),indent=2)+'\n')
