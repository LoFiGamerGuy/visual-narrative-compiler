from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P13';O=B/'F01-v4';O.mkdir()
s=json.loads((B/'F01-v3/P13-F01-v3.spec.json').read_text());s['id']='SC-20260907-01-S-P13-F01-v4';s['output_svg']=str((O/'P13-F01-v4.svg').relative_to(R))
facets=json.loads((B/'F01-v3/kite-facets.json').read_text());s['layers'].insert(3,dict(id='fixed-kite-projected-facets',svg=facets['svg'],kind='frozen-Blender-face-projection'))
th=Image.open(R/'production/structural-pilot/control/v8/P13-sentinel.png').convert('RGBA');th.putdata([(r,g,b,a if r-g>35 and b-g>35 else 0) for r,g,b,a in th.getdata()]);th.save(O/'gill-only.png');s['layers'].insert(4,dict(id='fixed-violet-slit',path=str((O/'gill-only.png').relative_to(R))))
# Keep original injured dorsal hand above Odo's supporting palm.
im=Image.open(B/'F01-v3/nera-matte.png').convert('RGBA').crop((1020,477,1077,534));m=im.getchannel('A');d=ImageDraw.Draw(m);d.rectangle([0,0,57,3],fill=0);im.putalpha(m);im.save(O/'original-right-wound-hand.png')
s['layers'].insert(-1,dict(id='original-right-injured-hand-over-support',path=str((O/'original-right-wound-hand.png').relative_to(R)),width=57,height=57,transform='matrix(.38 0 0 .38 798.1 539.56)',kind='source-bound-crop'))
(O/'P13-F01-v4.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'fixed_geometry_changed':False,'methods':['Exact frozen kite mesh face shading and original slit restored','Original right dorsal wounded hand cropped from registered matte and placed above supporting palm'],'generation_calls':0},indent=2)+'\n')
