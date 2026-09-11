import json,datetime,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[4];O=R/'production/structural-pilot/finishing/S/P13/F01';O.mkdir(parents=True)
raw=R/'production/structural-pilot/candidates/C00011-cd2b17c39141d6ab.png';im=Image.open(raw).convert('RGB');w,h=im.size
A=json.loads((R/'production/structural-pilot/control/v8/P13-anchors.json').read_text())['anchors']
def det(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def solve(m,b):return [det([[b[r] if c==i else m[r][c] for c in range(3)] for r in range(3)])/det(m) for i in range(3)]
def affine(src,dst):
 m=[[x,y,1] for x,y in src];a,c,e=solve(m,[p[0] for p in dst]);b,d,f=solve(m,[p[1] for p in dst]);return [a,b,c,d,e,f]
base=Image.new('L',im.size);base.putdata([0 if max(p)-min(p)<23 and min(p)>220 else round(255*(220-min(p))/16) if max(p)-min(p)<23 and 204<min(p)<=220 else 255 for p in im.getdata()]);base.save(O/'checkerboard-alpha.png')
actors={'nera':{'region':[(730,220),(994,220),(995,462),(1080,468),(1080,535),(995,541),(996,700),(1050,996),(730,996)],'points':[[909,304],[1044,497],[961,913]],'targets':['nera.head','nera.right_hand','nera.right_ankle']},'odo':{'region':[(998,193),(1300,193),(1300,1000),(997,1000),(984,549),(1009,536),(1069,534),(1080,491),(1010,455)],'points':[[1106,270],[1170,547],[1184,903]],'targets':['odo.head','odo.right_hand','odo.right_ankle']}}
layers=[]
for name,c in actors.items():
 m=Image.new('L',im.size);ImageDraw.Draw(m).polygon(c['region'],fill=255);m.putdata([min(x,y) for x,y in zip(m.getdata(),base.getdata())]);m.save(O/(name+'-mask.png'));out=im.convert('RGBA');out.putalpha(m);out.save(O/(name+'-matte.png'))
 mat=affine(c['points'],[A[k]['pixel'] for k in c['targets']]);c['matrix']=mat;layers.append(dict(id=name+'-source-actor',path=str((O/(name+'-matte.png')).relative_to(R)),width=w,height=h,transform='matrix('+' '.join(map(str,mat))+')',kind='source-matte-independent-affine'))
control='production/structural-pilot/control/v8/'
th=Image.open(R/(control+'P13-sentinel.png')).convert('RGBA');ink=Image.new('RGBA',th.size,'#202530');ink.putalpha(th.getchannel('A').filter(ImageFilter.MaxFilter(7)));ink.save(O/'sentinel-ink.png')
props=Image.open(R/(control+'P13-props.png')).convert('RGBA');props.putdata([(r,g,b,0 if r>g*1.5 and r>b*1.5 else a) for r,g,b,a in props.getdata()]);props.save(O/'fixed-props.png')
s={'id':'SC-20260907-01-S-P13-F01','width':1170,'height':1080,'output_svg':str((O/'P13-F01.svg').relative_to(R)),'layers':[dict(id='fixed-architecture',path=control+'P13-background.png'),dict(id='fixed-three-leg-outline',path=str((O/'sentinel-ink.png').relative_to(R))),dict(id='fixed-three-leg-sentinel',path=control+'P13-sentinel.png'),*layers,dict(id='fixed-staff-flask',path=str((O/'fixed-props.png').relative_to(R))),dict(id='nera-left-sleeve-to-fixed-staff',kind='explicit-conventional-vector-drawing',svg='<path d="M752 547 L770 548 L805 598 L797 613 L783 602 L753 566 Z" fill="#282c33" stroke="#14191f" stroke-width="2"/><path d="M763 552 L793 600" fill="none" stroke="#464951" stroke-width="2"/><path d="M793 601 Q799 597 804 602 L808 609 Q809 615 803 619 Q797 619 793 614 Z" fill="#a87647" stroke="#33251c" stroke-width="1.8"/><path d="M797 602 L802 609 M794 610 L801 615" stroke="#64432a" stroke-width="1" fill="none"/>'),dict(id='fixed-physical-shutter-partition',path=control+'P13-foreground.png')]}
(O/'P13-F01.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'matte-receipt.json').write_text(json.dumps(dict(raw=str(raw.relative_to(R)),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),raw_contract_failures=['RGB baked checkerboard instead of alpha','Recentered actors and mismatched far-left grip pose'],actors=actors,fixed_geometry='v8',generation_calls=0,method='Explicit chroma-neutral background key and polygon masks; independently affine register actors to head/right-hand/right-ankle; conventionally draw far-left forearm to fixed staff grip.'),indent=2)+'\n')
