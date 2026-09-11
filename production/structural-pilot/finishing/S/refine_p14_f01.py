"""Correct visible P14 masking/occlusion defects in the primary composition."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];PRE=ROOT/'production/structural-pilot/finishing/S/P14/F01';OUT=PRE.parent/'F01-v2'
mask=Image.open(PRE/'pair-mask.png').convert('L');ImageDraw.Draw(mask).rectangle([468,940,632,1200],fill=0);mask.save(OUT/'pair-mask.png')
im=Image.open(ROOT/'production/structural-pilot/candidates/C00007-05e9227e2675c85a.png').convert('RGBA');im.putalpha(mask);im.save(OUT/'pair-matte.png')
spec=json.loads((PRE/'P14-F01.spec.json').read_text());spec['id']='SC-20260907-01-S-P14-F01-v2';spec['output_svg']=str((OUT/'P14-F01-v2.svg').relative_to(ROOT))
props=next(x for x in spec['layers'] if x['id']=='fixed-staff-and-flask');spec['layers'].remove(props)
pair=next(x for x in spec['layers'] if x['id']=='connected-adult-pair');pair['path']=str((OUT/'pair-matte.png').relative_to(ROOT))
pair_index=spec['layers'].index(pair)
spec['layers'].insert(pair_index,{'id':'odo-trouser-underpaint-in-removed-prop-region','kind':'explicit-conventional-vector-clothing-repair','svg':'<path d="M866 972 L1017 1015 L1004 1320 L852 1320 Z" fill="#27282b" stroke="#191b20" stroke-width="3"/><path d="M938 1024 L921 1161 L944 1305 M978 1110 L968 1233" fill="none" stroke="#3c3e44" stroke-width="3"/>'})
pair_index=spec['layers'].index(pair);spec['layers'].insert(pair_index+1,props)
hand=next(x for x in spec['layers'] if x['id']=='odo-right-forearm-and-flask-grip')
pieces=hand['svg'].splitlines();hand['svg']='\n'.join(pieces[:3])+'\n<g transform="translate(989 940) scale(1.3) translate(-989 -940)">'+'\n'.join(pieces[3:])+'</g>'
(OUT/'P14-F01-v2.spec.json').write_text(json.dumps(spec,indent=2)+'\n')
(OUT/'cleanup-receipt.json').write_text(json.dumps({'previous':'../F01/P14-F01.png','documented_primary_failures':['Raw prop removal exposed a trouser hole','Fixed flask hidden behind actor jacket','A small generated staff remnant survived masking'],'corrections':['Explicit vector trouser underpaint beneath removed prop area','Place fixed rigid props in front of pair and behind replacement hands','Expand Nera old staff/hand erasure rectangle','Enlarge Odo replacement gripping palm by 1.3 about the fixed wrist area'],'generation_calls':0,'fixed_staff_flask_geometry_changed':False},indent=2)+'\n')
