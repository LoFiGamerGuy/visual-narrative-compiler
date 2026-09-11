"""Same bounded correction: source-guided Poisson seam blend, ordinary pixel math."""
from pathlib import Path
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];P=Path('production/structural-pilot/finishing/CF/P11/F02-v4');old=P.parent/'F02-v3'
s=json.loads((ROOT/old/'spec.json').read_text());im=Image.open(ROOT/s['layers'][0]['path']).convert('RGB');mask=Image.open(ROOT/P.parent/'F01/arrow-removal-mask.png').convert('L');w,h=mask.size;ip=im.load();selected=[i for i,v in enumerate(mask.get_flattened_data()) if v];selset=set(selected)
def predict(gx,gy):
 if gy<504:return ip[gx-50,gy-3]
 if gx<858:return ip[gx,gy+110]
 if gx>=907:return tuple(c*.94 for c in ip[gx,gy+70])
 base=ip[861+((gx-858)%35),640+((gy-504)%37)];boundary=1072-gy/3;left=boundary-14
 def blend(a,b,t):return tuple(a[k]*(1-t)+b[k]*t for k in range(3))
 l=tuple(c*.73 for c in base);band=tuple(base[k]*.55+[12,19,22][k] for k in range(3))
 if gx<left-.8:rgb=l
 elif gx<left+.8:rgb=blend(l,band,(gx-left+.8)/1.6)
 elif gx<boundary-.8:rgb=band
 elif gx<boundary+.8:rgb=blend(band,base,(gx-boundary+.8)/1.6)
 else:rgb=base
 overhead=.83+.17*min(1,max(0,(gy-504)/26))
 return tuple(c*overhead for c in rgb)
guidance=[predict(824+i%w,452+i//w) for i in range(w*h)];original=[ip[824+i%w,452+i//w] for i in range(w*h)];delta=[[original[i][k]-guidance[i][k] for k in range(3)] for i in range(w*h)]
for i in selected:delta[i]=[0.,0.,0.]
for iteration in range(600):
 change=0.
 for i in selected:
  x=i%w;y=i//w;ns=[j for j in (i-1 if x else -1,i+1 if x+1<w else -1,i-w if y else -1,i+w if y+1<h else -1) if j>=0]
  value=[sum(delta[j][k] for j in ns)/len(ns) for k in range(3)];change=max(change,max(abs(value[k]-delta[i][k]) for k in range(3)));delta[i]=value
 if change<.02:break
patch=Image.new('RGBA',(w,h),(0,0,0,0));pix=patch.load()
for i in selected:pix[i%w,i//w]=tuple(max(0,min(255,round(guidance[i][k]+delta[i][k]))) for k in range(3))+(255,)
patch.save(ROOT/P/'arrow-repair-patch.png')
recipe={'method':'Conventional Poisson seamless blend of explicit source-plane texture guidance; solve harmonic boundary correction, no learnedmodel','source':s['layers'][0]['path'],'source_sha256':s['layers'][0]['sha256'],'guidance_recipe':str(old/'repair-recipe.json'),'guidance_recipe_sha256':hashlib.sha256((ROOT/old/'repair-recipe.json').read_bytes()).hexdigest(),'mask':str(P.parent/'F01/arrow-removal-mask.png'),'mask_sha256':hashlib.sha256((ROOT/P.parent/'F01/arrow-removal-mask.png').read_bytes()).hexdigest(),'iterations':iteration+1,'max_final_update':change,'generation_calls':0}
(ROOT/P/'repair-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n');s['id']='CF-P11-F02-v4';s['output_svg']=str(P/'P11-F02-v4.svg');s['description']='Same declared correction final refinement: conventional Poisson seam blend retains explicit stone/cable texture guidance while matching immutable surrounding pixels. Thin boot-origin motiontrace and sealed cap persist.';s['layers'][1]['path']=str(P/'arrow-repair-patch.png');s['edit_intent']['repair_final']='Poisson seam blend of explicitsource-clone guidance'
with (ROOT/P/'spec.json').open('x') as f:f.write(json.dumps(s,indent=2)+'\n')
print(iteration+1,change)
