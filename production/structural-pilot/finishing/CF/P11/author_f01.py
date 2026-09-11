"""Conventional local pixel interpolation and editable motion/cap drawing. No model/API."""
from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib
ROOT=Path(__file__).resolve().parents[5]
P=Path('production/structural-pilot/finishing/CF/P11/F01')
source=Path('production/structural-pilot/candidates/C00013-901ccab2f920789b.png')
im=Image.open(ROOT/source).convert('RGB');W,H=im.size
bbox=(824,452,933,584);x0,y0,x1,y1=bbox
crop=im.crop(bbox);mask=Image.new('L',crop.size,0);mp=mask.load();cp=crop.load()
for y in range(crop.height):
 for x in range(crop.width):
  r,g,b=cp[x,y]
  if g>165 and b>180 and r<190 and g-r>35 and b-r>40:mp[x,y]=255
mask=mask.filter(ImageFilter.MaxFilter(5));mask.save(ROOT/P/'arrow-removal-mask.png')
# Explicit row interpolation from the nearest unchanged pixel on either side of each
# selected run; retains source pixels everywhere outside the mask. It is ordinary
# local repair, not learned/diffusion inpainting. The mask and recipe remain editable.
patch=Image.new('RGBA',crop.size,(0,0,0,0));pp=patch.load();mp=mask.load();runs=[]
for y in range(crop.height):
 x=0
 while x<crop.width:
  if not mp[x,y]:x+=1;continue
  a=x
  while x<crop.width and mp[x,y]:x+=1
  b=x-1;left=max(0,a-1);right=min(crop.width-1,b+1);c0=cp[left,y];c1=cp[right,y]
  for xx in range(a,b+1):
   t=(xx-left)/max(1,right-left)
   pp[xx,y]=tuple(round(c0[k]*(1-t)+c1[k]*t) for k in range(3))+(255,)
  runs.append([y,a,b])
patch.save(ROOT/P/'arrow-repair-patch.png')
recipe={'method':'Explicit row interpolation across cyan-only local mask','source':str(source),'source_sha256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),'bbox':bbox,'threshold':'g>165,b>180,r<190,g-r>35,b-r>40','mask_dilation':'Pillow MaxFilter5','selected_runs':runs,'learned_model':None,'generation_calls':0}
(ROOT/P/'repair-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
motion='''<path d="M967 542 C965 660 909 744 826 831 C746 913 681 958 609 991 C664 949 731 895 802 818 C888 726 943 638 967 542 Z" fill="#85edf3" fill-opacity=".86"/>
<path d="M972 547 C961 672 881 785 785 875 C724 931 658 971 611 991" fill="none" stroke="#45bdcf" stroke-width="1.6" stroke-opacity=".7"/>
<path d="M950 570 C926 681 858 776 787 844" fill="none" stroke="#d5feff" stroke-width="2.8" stroke-linecap="round"/>
<path d="M694 941 C667 962 638 980 612 990" fill="none" stroke="#cbfcff" stroke-width="1.7" stroke-linecap="round"/>
<path d="M660 947 L618 982 M647 950 L615 976" fill="none" stroke="#73dce8" stroke-width="1.3" stroke-opacity=".8"/>
'''
cap='''<path d="M452 836 Q467 829 481 837 L480 844 Q465 851 452 843 Z" fill="#8c928e" stroke="#282d2c" stroke-width="1.2"/>
<ellipse cx="466.5" cy="837.8" rx="14.5" ry="5.5" transform="rotate(7 466.5 837.8)" fill="#bfc3b9" stroke="#303735" stroke-width="1.1"/>
<path d="M455 837 Q465 833 477 837" fill="none" stroke="#e8e8d8" stroke-width="1.3"/>
<path d="M459 840 L463 841 M472 838 L476 839" stroke="#828a82" stroke-width=".65"/>
'''
s={'id':'CF-P11-F01','width':W,'height':H,'output_svg':str(P/'P11-F01.svg'),'description':'Conventional removal of doorway-pointing arrow using preserved local mask and row-interpolation recipe; explicit tapered staff/descent arc ends beside forelimb joint. Solid drawn flask cap. Actual motion/contact review pending.','layers':[{'id':'unchanged-generated-source','path':str(source),'sha256':recipe['source_sha256'],'kind':'preserved-generated-raster'}, {'id':'explicit-arrow-pixel-repair','path':str(P/'arrow-repair-patch.png'),'x':x0,'y':y0,'width':crop.width,'height':crop.height,'kind':'conventional-local-interpolation'}, {'id':'redirected-staff-descent','svg':motion,'kind':'editable-motion-ink'}, {'id':'visibly-sealed-flask-cap','svg':cap,'kind':'editable-prop-state-ink'}],'edit_intent':{'target_joint_pixel':[609,1000],'new_motion_end_pixel':[609,991],'preserved_source_ascent_and_brake':True,'local_cap_center':[466.5,837.8],'no_duplicate_body':True}}
with (ROOT/P/'spec.json').open('x') as f:f.write(json.dumps(s,indent=2)+'\n')
