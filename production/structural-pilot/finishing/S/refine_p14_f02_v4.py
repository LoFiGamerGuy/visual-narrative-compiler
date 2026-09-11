from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P14';O=B/'F02-v4';O.mkdir();raw=Image.open(R/'production/structural-pilot/candidates/C00007-05e9227e2675c85a.png').convert('RGBA');s=json.loads((B/'F02-v3/P14-F02-v3.spec.json').read_text());s['id']='SC-20260907-01-S-P14-F02-v4';s['output_svg']=str((O/'P14-F02-v4.svg').relative_to(R))
base=Image.new('L',raw.size);base.putdata([0 if max(p[:3])-min(p[:3])<23 and min(p[:3])>220 else round(255*(220-min(p[:3]))/16) if max(p[:3])-min(p[:3])<23 and 204<min(p[:3])<=220 else 255 for p in raw.getdata()]);m=Image.open(B/'F02/pair-mask.png').convert('L');mp=m.load();bp=base.load()
for y in range(750,1150):
 for x in range(870,1110):mp[x,y]=bp[x,y]
erase=[(970,775),(1086,796),(1065,857),(1026,866),(1033,927),(1020,974),(998,1025),(986,1076),(920,1076),(910,1024),(913,1000),(902,966),(905,929),(914,887),(952,846)]
em=Image.new('L',raw.size);ImageDraw.Draw(em).polygon(erase,fill=255);em=em.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(3));m.putdata([min(a,255-b) for a,b in zip(m.getdata(),em.getdata())]);im=raw.copy();im.putalpha(m);im.save(O/'pair-matte.png');m.save(O/'pair-mask.png')
patch=Image.new('RGBA',raw.size);patch.paste(raw.crop((759,897,886,1119)).resize((170,270)),(885,832));patch.paste(raw.crop((950,670,1050,750)).resize((195,92)),(913,760));pa=em.filter(ImageFilter.MaxFilter(7));pa.putdata([min(a,b) for a,b in zip(pa.getdata(),base.getdata())]);patch.putalpha(pa);patch.save(O/'feathered-native-clothing-repair.png');pa.save(O/'feathered-native-clothing-repair-mask.png')
for l in s['layers']:
 if l['id']=='connected-source-pair':l['path']=str((O/'pair-matte.png').relative_to(R))
 if l['id']=='source-trouser-interior-repair':l['path']=str((O/'feathered-native-clothing-repair.png').relative_to(R))
 if l['id']=='textured-left-forearm':
  old='M423 1008 Q445 993 460 1014 L663 1099 L658 1140 Q612 1140 593 1128 L437 1067 Z';new='M423 1008 Q441 998 453 1007 Q486 1033 498 1036 L642 1094 Q652 1102 655 1112 L647 1135 Q634 1142 620 1130 L461 1074 Q440 1062 429 1055 Z';l['svg']=l['svg'].replace(old,new).replace('x="420" y="1000" width="246" height="137"','x="416" y="995" width="265" height="99" transform="rotate(21 435 1035)"')
(O/'P14-F02-v4.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'method':'Expand exact old-prop erasure enough to include its original black shadow; feather clothing repair boundary; shorten replacement blue cloth to waist seam; round local left forearm contour and orient native cloth folds along arm.','erasure_source_polygon':erase,'mask_expansion_px':12,'mask_gaussian_radius':3,'source_trouser_crop':[759,897,886,1119],'source_trouser_resize':[170,270],'source_trouser_place':[885,832],'generation_calls':0,'fixed_geometry_changed':False},indent=2)+'\n')
