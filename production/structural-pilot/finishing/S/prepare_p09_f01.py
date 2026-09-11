import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[4];O=R/'production/structural-pilot/finishing/S/P09/F01';O.mkdir(parents=True);raw=R/'production/structural-pilot/candidates/C00009-65ee8e570d3cf77c.png';im=Image.open(raw).convert('RGB');w,h=im.size
A=json.loads((R/'production/structural-pilot/control/v8/P09-anchors.json').read_text())['anchors']
def det(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def solve(m,b):return [det([[b[r] if c==i else m[r][c] for c in range(3)] for r in range(3)])/det(m) for i in range(3)]
def affine(src,dst):
 m=[[x,y,1] for x,y in src];a,c,e=solve(m,[p[0] for p in dst]);b,d,f=solve(m,[p[1] for p in dst]);return [a,b,c,d,e,f]
base=Image.new('L',im.size);base.putdata([0 if max(p)-min(p)<23 and min(p)>220 else round(255*(220-min(p))/16) if max(p)-min(p)<23 and 204<min(p)<=220 else 255 for p in im.getdata()]);base.save(O/'checkerboard-alpha.png')
nera_matrix=affine([[730,430],[445,880],[851,880]],[A[k]['pixel'] for k in ['nera.head','nera.left_ankle','nera.right_ankle']])
actors={'nera':{'bounds':[390,340,940,970],'matrix':nera_matrix,'erasures':[[(556,551),(589,565),(527,647),(531,682),(478,690),(473,630)],[(777,655),(805,647),(844,716),(845,753),(800,754),(785,714)]]},'odo':{'bounds':[65,185,378,975],'matrix':[.4,0,0,.36,127.9,325.15],'erasures':[]}}
layers=[]
for n,c in actors.items():
 m=Image.new('L',im.size);d=ImageDraw.Draw(m);d.rectangle(c['bounds'],fill=255);m.putdata([min(a,b) for a,b in zip(m.getdata(),base.getdata())]);d=ImageDraw.Draw(m)
 for p in c['erasures']:d.polygon(p,fill=0)
 m.save(O/(n+'-mask.png'));out=im.convert('RGBA');out.putalpha(m);out.save(O/(n+'-matte.png'));layers.append(dict(id=n+'-source-actor',path=str((O/(n+'-matte.png')).relative_to(R)),width=w,height=h,transform='matrix('+' '.join(map(str,c['matrix']))+')',kind='source-bound-matte-and-affine'))
control='production/structural-pilot/control/v8/';th=Image.open(R/(control+'P09-sentinel.png')).convert('RGBA');ink=Image.new('RGBA',th.size,'#202530');ink.putalpha(th.getchannel('A').filter(ImageFilter.MaxFilter(7)));ink.save(O/'sentinel-ink.png')
# Hands wrap the exact frozen staff axis at the two named grip anchors.
arms='<path d="M519 519 Q527 519 533 529 L562 565 L555 581 L545 578 L516 541 Z" fill="#30333a" stroke="#171a20" stroke-width="2"/><path d="M524 525 L548 559 L544 566 L523 540" fill="#474a51"/><path d="M607 548 L625 550 L626 588 L619 602 L608 596 L608 575 Z" fill="#30333a" stroke="#171a20" stroke-width="2"/><path d="M615 554 L620 556 L620 580 L615 585 Z" fill="#474a51"/>'
hands=''
for x,y in [A['nera.left_hand']['pixel'],A['nera.right_hand']['pixel']]:
 hands+=f'<g transform="translate({x} {y}) rotate(20)"><path d="M-8 -8 Q-3 -14 4 -10 L10 -4 Q12 4 6 10 Q0 14 -7 8 L-11 0 Z" fill="#ac7a49" stroke="#35271d" stroke-width="1.7"/><path d="M-8 -7 Q-2 -12 2 -5 L3 1 Q1 5 -3 2 L-8 -2 Z" fill="#c4915a" stroke="#563b26" stroke-width="1.2"/><path d="M7 -2 L4 6 M2 7 L-1 10 M-4 4 L-6 7" stroke="#66482e" stroke-width="1.1" fill="none"/></g>'
s={'id':'SC-20260907-01-S-P09-F01','width':1170,'height':900,'output_svg':str((O/'P09-F01.svg').relative_to(R)),'layers':[dict(id='fixed-architecture',path=control+'P09-background.png'),dict(id='fixed-threat-ink',path=str((O/'sentinel-ink.png').relative_to(R))),dict(id='fixed-three-leg-threat',path=control+'P09-sentinel.png'),dict(id='fixed-props-under-actors',path=control+'P09-props.png'),dict(id='fixed-action-effects',path=control+'P09-effects.png'),*layers,dict(id='two-connected-conventional-forearms',svg=arms,kind='explicit-vector-correction'),dict(id='two-gripping-hands-at-fixed-rod-anchors',svg=hands,kind='explicit-vector-correction'),dict(id='fixed-partition',path=control+'P09-foreground.png')]}
(O/'P09-F01.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'matte-receipt.json').write_text(json.dumps(dict(raw=str(raw.relative_to(R)),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),raw_mode=im.mode,raw_contract_failures=['RGB painted checkerboard instead of alpha','Retry still lacks two hands aligned to staff shaft'],actors=actors,correction='Remove unsupported source forearms/hands; draw separate traceable sleeves and two grips at frozen rod anchors; preserve exact rod-to-toe contact and three limbs.',generation_calls=0,fixed_geometry_changed=False),indent=2)+'\n')
print('NERA_MATRIX',nera_matrix)
