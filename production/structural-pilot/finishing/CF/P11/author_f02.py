"""One conventional correction round: harmonic local repair and restrained body-motion lines."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];P=Path('production/structural-pilot/finishing/CF/P11/F02');old=P.parent/'F01'
s=json.loads((ROOT/old/'spec.json').read_text());source=Path(s['layers'][0]['path']);im=Image.open(ROOT/source).convert('RGB');box=(824,452,933,584);crop=im.crop(box);mask=Image.open(ROOT/old/'arrow-removal-mask.png').convert('L');prior=Image.open(ROOT/old/'arrow-repair-patch.png').convert('RGBA');w,h=crop.size
original=list(crop.get_flattened_data());values=[list(map(float,px)) for px in original];selected=[i for i,v in enumerate(mask.get_flattened_data()) if v];selectedset=set(selected);pr=list(prior.get_flattened_data())
for i in selected:values[i]=list(map(float,pr[i][:3]))
# Conventional Laplace interpolation (Gauss-Seidel), explicit immutable boundaries.
# No model or generative API. This smooths the F01 row steps within the identical mask.
for iteration in range(600):
 delta=0.
 for i in selected:
  x=i%w;y=i//w;neighbors=[j for j in (i-1 if x else -1,i+1 if x+1<w else -1,i-w if y else -1,i+w if y+1<h else -1) if j>=0]
  new=[sum(values[j][k] for j in neighbors)/len(neighbors) for k in range(3)]
  delta=max(delta,max(abs(new[k]-values[i][k]) for k in range(3)));values[i]=new
 if delta<.025:break
patch=Image.new('RGBA',(w,h),(0,0,0,0));pix=patch.load()
# Small preserved-source high-frequency luminance residue avoids a perfectly flat patch.
blur=im.filter(ImageFilter.GaussianBlur(1.4));ip=im.load();bp=blur.load()
for i in selected:
 x=i%w;y=i//w;sx=box[0]+x;sy=box[1]+y+145
 residual=sum(ip[sx,sy][k]-bp[sx,sy][k] for k in range(3))/3*.4
 pix[x,y]=tuple(max(0,min(255,round(c+residual))) for c in values[i])+(255,)
patch.save(ROOT/P/'arrow-repair-patch.png')
(ROOT/P/'repair-recipe.json').write_text(json.dumps({'method':'Conventional Laplace harmonic interpolation, Gauss-Seidel600max, convergence .025; originalboundarypixels heldfixed','source':str(source),'source_sha256':s['layers'][0]['sha256'],'mask':str(old/'arrow-removal-mask.png'),'mask_sha256':hashlib.sha256((ROOT/old/'arrow-removal-mask.png').read_bytes()).hexdigest(),'iterations':iteration+1,'max_final_update':delta,'source_texture_residue':{'offset':[0,145],'GaussianBlur_radius':1.4,'gain':.4},'learned_model':None,'generation_calls':0},indent=2)+'\n')
s['id']='CF-P11-F02';s['output_svg']=str(P/'P11-F02.svg');s['description']='One declared correction: smooth conventional local pixel repair replaces F01 row steps. Thin body-motion trace starts behind boot and terminates short of the forelimb, avoiding an emitted slash. Original ascent/brake, pose and closed cap persist.'
s['layers'][1]['path']=str(P/'arrow-repair-patch.png')
s['layers'][2]['id']='foot-origin-future-motion-trace';s['layers'][2]['svg']='''<path d="M815 579 C858 675 824 785 746 873 C704 921 664 950 630 973" fill="none" stroke="#65c8d5" stroke-width="3.2" stroke-opacity=".76" stroke-linecap="round"/>
<path d="M825 586 C866 687 829 791 752 879 C711 925 674 950 647 967" fill="none" stroke="#b9eef1" stroke-width="1.8" stroke-opacity=".84" stroke-linecap="round"/>
<path d="M808 592 C829 660 821 722 800 768" fill="none" stroke="#8ed7de" stroke-width="1.25" stroke-opacity=".6" stroke-linecap="round"/>
'''
s['edit_intent']={'correction_of':'CF-P11-F01','target_joint_pixel':[609,1000],'motion_origin':'behind Nera forwardboot at815,579','motion_end_pixel':[630,973],'no_motion_contact_or_impact':True,'thin_no_arrowhead_no_emitted_weapon':True,'preserved_source_ascent_and_brake':True,'preserved_source_pose_and_staff':True}
with (ROOT/P/'spec.json').open('x') as f:f.write(json.dumps(s,indent=2)+'\n')
print('iterations',iteration+1,'delta',delta)
