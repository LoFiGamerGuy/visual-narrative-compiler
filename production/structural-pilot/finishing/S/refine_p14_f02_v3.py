from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P14';O=B/'F02-v3';O.mkdir();raw=Image.open(R/'production/structural-pilot/candidates/C00007-05e9227e2675c85a.png').convert('RGBA');s=json.loads((B/'F02-v2/P14-F02-v2.spec.json').read_text());s['id']='SC-20260907-01-S-P14-F02-v3';s['output_svg']=str((O/'P14-F02-v3.svg').relative_to(R))
# Tight old prop removal, preserving native trouser pixels around it.
m=Image.open(B/'F02/pair-mask.png').convert('L');base=Image.new('L',raw.size);base.putdata([0 if max(p[:3])-min(p[:3])<23 and min(p[:3])>220 else round(255*(220-min(p[:3]))/16) if max(p[:3])-min(p[:3])<23 and 204<min(p[:3])<=220 else 255 for p in raw.getdata()]);mp=m.load();bp=base.load()
for y in range(770,1130):
 for x in range(890,1100):mp[x,y]=bp[x,y]
erase=[(970,775),(1086,796),(1065,857),(1026,866),(1033,927),(1020,974),(998,1025),(975,1046),(924,1046),(910,1024),(913,1000),(902,966),(905,929),(914,887),(952,846)]
ImageDraw.Draw(m).polygon(erase,fill=0);im=raw.copy();im.putalpha(m);im.save(O/'pair-matte.png');m.save(O/'pair-mask.png')
# Nearby intact trouser drawing at near-native resolution; limited to tight vacancy.
patch=Image.new('RGBA',raw.size);patch.paste(raw.crop((764,900,880,1088)).resize((136,202)),(902,845));patch.paste(raw.crop((950,670,1050,750)).resize((162,94)),(928,774));pa=Image.new('L',raw.size);ImageDraw.Draw(pa).polygon(erase,fill=255);pa=pa.filter(ImageFilter.MaxFilter(5));pa.putdata([min(a,b) for a,b in zip(pa.getdata(),base.getdata())]);patch.putalpha(pa);patch.save(O/'tight-source-clothing-repair.png');pa.save(O/'tight-source-clothing-repair-mask.png')
for l in s['layers']:
 if l['id']=='connected-source-pair':l['path']=str((O/'pair-matte.png').relative_to(R))
 if l['id']=='source-trouser-interior-repair':l['path']=str((O/'tight-source-clothing-repair.png').relative_to(R))
 if l['id']=='original-left-hand-registered-to-fixed-staff':
  im=Image.open(B/'F02-v2/nera-left-source-hand.png').convert('RGBA');im.putdata([(r,g,b,0 if max(r,g,b)-min(r,g,b)<25 and min(r,g,b)>170 else min(a,round(255*(170-min(r,g,b))/30)) if max(r,g,b)-min(r,g,b)<25 and 140<min(r,g,b)<=170 else a) for r,g,b,a in im.getdata()]);im.save(O/'nera-left-source-hand.png');l['path']=str((O/'nera-left-source-hand.png').relative_to(R))
 if l['id']=='fixed-staff-texture-within-exact-alpha':l['svg']=l['svg'].replace('<linearGradient id="wood" x1="0" x2="1">','<linearGradient id="wood" gradientUnits="userSpaceOnUse" x1="565" y1="1149" x2="603" y2="1171">')
 if l['id']=='textured-right-palm-supports-fixed-flask-base':l['svg']+='<path d="M950 932 Q954 930 958 935 L957 939 Q953 939 950 936 Z M957 943 L963 943 L965 948 L962 950 Z M970 954 L976 953 L980 957 L977 960 Z" fill="#b38b5e" stroke="#725335" stroke-width="1"/><path d="M1009 947 Q1003 954 991 956" fill="none" stroke="#795432" stroke-width="1.3"/>'
(O/'P14-F02-v3.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'tight_old_prop_erasure_source_px':erase,'trouser_texture_crop':[764,900,880,1088],'trouser_texture_resize':[136,202],'trouser_texture_place':[902,845],'blue_texture_crop':[950,670,1050,750],'blue_texture_resize':[162,94],'blue_texture_place':[928,774],'methods':['Restore all original trouser drawing outside exact old prop vacancy','Fill that smaller vacancy using nearby cloth at near-native resolution','Stronger neutral fringe key only on source left-hand crop','Apply cylindrical cross-width wood value shading inside fixed alpha'],'generation_calls':0,'fixed_geometry_changed':False},indent=2)+'\n')
