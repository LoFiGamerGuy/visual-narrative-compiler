import json
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P14';O=B/'F01-v4';O.mkdir()
s=json.loads((B/'F01-v3/P14-F01-v3.spec.json').read_text());s['id']='SC-20260907-01-S-P14-F01-v4';s['output_svg']=str((O/'P14-F01-v4.svg').relative_to(R))
# Clip source cloth clone to a trouser silhouette and extend to frame edge.
p=Image.open(B/'F01-v3/trouser-source-clone.png').convert('RGBA').resize((165,370));m=Image.new('L',p.size);ImageDraw.Draw(m).polygon([(0,0),(133,17),(159,47),(156,370),(0,370)],fill=255);p.putalpha(m);p.save(O/'trouser-source-clone.png');m.save(O/'trouser-clone-mask.png')
for l in s['layers']:
 if l['id']=='odo-source-bound-trouser-clone':l.update(path=str((O/'trouser-source-clone.png').relative_to(R)),width=165,height=370,transform='translate(855 950)')
 if l['id']=='nera-anatomical-left-forearm-and-grip':l['svg']='<path d="M423 1008 Q440 994 458 1013 L543 1115 L530 1149 Q513 1147 494 1128 L430 1070 Z" fill="#303239" stroke="#17191e" stroke-width="3.4"/><path d="M442 1017 L454 1045 L526 1122 L514 1131 L446 1050" fill="#44474f"/><path d="M518 1105 L544 1121 L534 1150 L506 1132 Z" fill="#24262d" stroke="#17191e" stroke-width="3"/>'
 if l['id']=='source-drawn-nera-hand':l['transform']='rotate(-45 589 1158) matrix(.7 0 0 .7 553.2 1082.5)'
(O/'P14-F01-v4.spec.json').write_text(json.dumps(s,indent=2)+'\n')
