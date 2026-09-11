"""Primary-composition cleanup: remove residual cord outlines and ink fixed threat."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[4];PRE=ROOT/'production/structural-pilot/finishing/S/P11/F01';OUT=PRE.parent/'F01-v2'
raw=ROOT/'production/structural-pilot/candidates/C00003-7a0a3d591b58c237.png'
if (OUT/'P11-F01-v2.spec.json').exists():raise SystemExit('Preserve existing output')
mask=Image.open(PRE/'odo-mask.png').convert('L');d=ImageDraw.Draw(mask)
polygon=[(102,818),(122,818),(108,1139),(101,1183),(83,1183),(90,1139)]
d.polygon(polygon,fill=0);mask.save(OUT/'odo-mask.png')
im=Image.open(raw).convert('RGBA');im.putalpha(mask);im.save(OUT/'odo-matte.png')
threat=Image.open(ROOT/'production/structural-pilot/control/v8/P11-sentinel.png').convert('RGBA')
alpha=threat.getchannel('A');ink=Image.new('RGBA',threat.size,'#202530');ink.putalpha(alpha.filter(ImageFilter.MaxFilter(7)));ink.save(OUT/'sentinel-ink.png')
gill=threat.copy();gill.putalpha(Image.new('L',gill.size));pixels=[]
for r,g,b,a in threat.getdata():pixels.append((r,g,b,a if r-g>35 and b-g>35 else 0))
gill.putdata(pixels);gill.save(OUT/'gill-only.png')
spec=json.loads((PRE/'P11-F01.spec.json').read_text());spec['id']='SC-20260907-01-S-P11-F01-v2';spec['output_svg']=str((OUT/'P11-F01-v2.svg').relative_to(ROOT))
for layer in spec['layers']:
 if layer['id']=='odo-generated-actor':layer['path']=str((OUT/'odo-matte.png').relative_to(ROOT))
spec['layers'].insert(1,{'id':'fixed-sentinel-silhouette-ink','path':str((OUT/'sentinel-ink.png').relative_to(ROOT)),'kind':'conventional-3px-outline-from-fixed-alpha'})
facets=json.loads((OUT/'kite-facets.json').read_text())
spec['layers'].insert(3,{'id':'fixed-kite-projected-face-shading','svg':facets['svg'],'kind':'editable-vector-facets-projected-from-frozen-mesh'})
spec['layers'].insert(4,{'id':'fixed-single-gill','path':str((OUT/'gill-only.png').relative_to(ROOT)),'kind':'original-fixed-gill-pixels'})
anchors=json.loads((ROOT/'production/structural-pilot/control/v8/P11-anchors.json').read_text())['anchors'];rings=[]
for limb in ['foreleg','sweep_leg','support_leg']:
 for j in [0,1]:
  x,y=anchors[f'sentinel.{limb}.{j}']['pixel'];radius=17 if limb=='support_leg' else 19
  rings.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="#343e50" stroke-width="2.2"/>')
spec['layers'].insert(5,{'id':'fixed-joint-ink-rings','svg':'\n'.join(rings),'kind':'editable-vector-lines-at-frozen-joint-centers'})
(OUT/'P11-F01-v2.spec.json').write_text(json.dumps(spec,indent=2)+'\n')
(OUT/'cleanup-receipt.json').write_text(json.dumps({'schema':'ConventionalPrimaryCleanup/1','preserved_previous':'../F01/P11-F01.png','reason':'Visible generated cord outline survived color removal; control machinery lacked line/value finish.','extra_odo_removal_polygon_source_px':polygon,'rod_geometry_changed':False,'threat_geometry_changed':False,'method':'Erase explicit residual-cord region from actor alpha; derive ink outline from original sentinel alpha; shade exact projected kite faces and retain original gill pixels.','generation_calls':0},indent=2)+'\n')
