"""Same correction round: explicit surface-aware source cloning replaces blurred repair."""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];P=Path('production/structural-pilot/finishing/CF/P11/F02-v2');old=P.parent/'F02'
s=json.loads((ROOT/old/'spec.json').read_text());im=Image.open(ROOT/s['layers'][0]['path']).convert('RGB');mask=Image.open(ROOT/P.parent/'F01/arrow-removal-mask.png').convert('L');w,h=mask.size;patch=Image.new('RGBA',(w,h),(0,0,0,0));pp=patch.load();mp=mask.load();ip=im.load();records=[]
for y in range(h):
 for x in range(w):
  if not mp[x,y]:continue
  gx,gy=824+x,452+y
  if gy<504:
   sx,sy=gx-50,gy-3;rgb=ip[sx,sy];surface='same overhead cable/wall, translated along slope'
  elif gx<858:
   sx,sy=gx,gy+110;rgb=ip[sx,sy];surface='cream wall, same vertical plane'
  elif gx<907:
   sx,sy=861+((gx-858)%35),640+((gy-504)%37);base=ip[sx,sy]
   boundary=1072-gy/3
   dark=max(0.,min(1.,(boundary-gx+.8)/1.6));gain=1-.27*dark
   rgb=tuple(round(c*gain) for c in base);surface='source gray stone texture with explicit diagonal cast-shadow gain'
  else:
   sx,sy=gx,gy+70;rgb=ip[sx,sy];surface='cream right jamb, same vertical plane'
  pp[x,y]=rgb+(255,);records.append([gx,gy,sx,sy,surface])
patch.save(ROOT/P/'arrow-repair-patch.png')
recipe={'method':'Conventional explicit source-pixel clone by four observed architectural surfaces; no learned repair','source':s['layers'][0]['path'],'source_sha256':s['layers'][0]['sha256'],'mask':str(P.parent/'F01/arrow-removal-mask.png'),'mask_sha256':hashlib.sha256((ROOT/P.parent/'F01/arrow-removal-mask.png').read_bytes()).hexdigest(),'surface_rules':['gy<504: source(gx-50,gy-3) follows unchanged cable slope','gx<858 below cable: source(gx,gy+110) cream wall','858<=gx<907: source stone atx861..895,y640..676; castshadow boundaryx=1072-y/3,gain .73..1 across1.6px','gx>=907: source(gx,gy+70) rightjamb'],'pixel_map':records,'learned_model':None,'generation_calls':0}
(ROOT/P/'repair-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n');s['id']='CF-P11-F02-v2';s['output_svg']=str(P/'P11-F02-v2.svg');s['description']='Same declared correction round final: explicit source texture cloning along cable and observed stone planes, with a drawn diagonal cast-shadow rule, replaces both row steps and harmonic blur. Thin boot-origin motion and closed cap remain. Actual-art review pending.';s['layers'][1]['path']=str(P/'arrow-repair-patch.png');s['edit_intent']['repair_final']='surface-aware source clone with exact editable recipe'
with (ROOT/P/'spec.json').open('x') as f:f.write(json.dumps(s,indent=2)+'\n')
