from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P13';O=B/'F01-v2';O.mkdir();raw=Image.open(R/'production/structural-pilot/candidates/C00011-cd2b17c39141d6ab.png').convert('RGBA')
s=json.loads((B/'F01/P13-F01.spec.json').read_text());s['id']='SC-20260907-01-S-P13-F01-v2';s['output_svg']=str((O/'P13-F01-v2.svg').relative_to(R))
for n in ['nera','odo']:
 m=Image.open(B/('F01/'+n+'-mask.png')).convert('L');pix=m.load();rgb=raw.load()
 if n=='nera':
  for y in range(440,550):
   for x in range(990,1081):
    r,g,b,a=rgb[x,y]
    if b>r*1.2 and b>g*1.1:pix[x,y]=0
 else:
  ImageDraw.Draw(m).polygon([(1008,478),(1056,477),(1074,519),(1060,538),(1040,531),(1028,512),(1008,520)],fill=0)
 m.save(O/(n+'-mask.png'));im=raw.copy();im.putalpha(m);im.save(O/(n+'-matte.png'))
 for l in s['layers']:
  if l['id']==n+'-source-actor':l['path']=str((O/(n+'-matte.png')).relative_to(R));l['transform']='matrix(.38 0 0 .38 410.5 358.3)' if n=='nera' else 'matrix(.38 0 0 .38 448.14 330.98)'
(O/'P13-F01-v2.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'previous':'F01/P13-F01.png','failure_observed':'Three-point affine over-constrained nearly collinear anchors and severely sheared actor silhouettes.','correction':'Use uniform similarity scale .38 for readable bodies. Local arm control handled separately.','exact_joint_registration':False,'generation_calls':0},indent=2)+'\n')
