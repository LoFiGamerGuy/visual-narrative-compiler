from pathlib import Path
from PIL import Image,ImageDraw
import json,base64
R=Path(__file__).resolve().parents[4];B=R/'production/structural-pilot/finishing/S/P09';O=B/'F01-v3';O.mkdir();raw=Image.open(R/'production/structural-pilot/candidates/C00009-65ee8e570d3cf77c.png').convert('RGBA')
s=json.loads((B/'F01-v2/P09-F01-v2.spec.json').read_text());s['id']='SC-20260907-01-S-P09-F01-v3';s['output_svg']=str((O/'P09-F01-v3.svg').relative_to(R))
m=Image.open(B/'F01/nera-mask.png').convert('L');region=Image.new('L',raw.size);ImageDraw.Draw(region).polygon([(545,514),(596,493),(635,480),(645,510),(594,552),(576,576),(550,612),(530,628),(486,678),(473,650),(503,576)],fill=255);rp=region.load();mp=m.load();rgb=raw.load()
for y in range(480,679):
 for x in range(473,646):
  r,g,b,a=rgb[x,y]
  if rp[x,y] and max(r,g,b)<160:mp[x,y]=0
im=raw.copy();im.putalpha(m);im.save(O/'nera-matte.png');m.save(O/'nera-mask.png')
cloth=raw.crop((687,686,727,720));cloth.save(O/'costume-texture-source.png');uri='data:image/png;base64,'+base64.b64encode((O/'costume-texture-source.png').read_bytes()).decode()
far='M549 479 L560 490 L533 530 L563 564 L556 581 L545 578 L513 539 Q508 530 514 520 Z'
near='M596 531 L614 532 L626 588 L619 602 L608 596 L606 576 Z'
far_svg=f'<defs><clipPath id="farArm"><path d="{far}"/></clipPath></defs><path d="{far}" fill="#30333a" stroke="#171a20" stroke-width="2"/><image href="{uri}" x="507" y="478" width="59" height="105" preserveAspectRatio="none" clip-path="url(#farArm)"/><path d="M549 488 L520 529 L552 569" fill="none" stroke="#52545a" stroke-width="1.4"/><path d="M545 563 L561 567 L557 579 L545 576 Z" fill="#272a30" stroke="#15191d" stroke-width="1.2"/>'
near_svg=f'<defs><clipPath id="nearArm"><path d="{near}"/></clipPath></defs><path d="{near}" fill="#30333a" stroke="#171a20" stroke-width="2"/><image href="{uri}" x="595" y="530" width="32" height="74" preserveAspectRatio="none" clip-path="url(#nearArm)"/><path d="M604 538 L616 582" fill="none" stroke="#515359" stroke-width="1.4"/><path d="M608 585 L624 585 L622 598 L610 598 Z" fill="#272a30" stroke="#17191e" stroke-width="1.2"/>'
for l in s['layers']:
 if l['id']=='nera-source-actor':l['path']=str((O/'nera-matte.png').relative_to(R))
 if l['id']=='two-connected-conventional-forearms':l['id']='near-arm-conventional-source-cloth';l['svg']=near_svg
idx=next(i for i,l in enumerate(s['layers']) if l['id']=='nera-source-actor');s['layers'].insert(idx,dict(id='far-arm-origin-under-cape',svg=far_svg,kind='explicit-vector-anatomy-with-source-costume-texture'))
# Native source fists, independent masks, no invented skin or generation.
for name,box,poly,transform in [('right',(800,700,840,745),[(8,0),(20,1),(25,11),(36,18),(37,32),(26,41),(13,41),(3,30),(6,20)],'matrix(.55 0 0 .55 606.55 583.25)'),('left',(485,622,530,675),[(16,4),(30,13),(35,25),(35,39),(24,47),(13,45),(2,34),(5,22)],'matrix(.55 0 0 .55 544.47 558.91)')]:
 im=raw.crop(box);hm=Image.new('L',im.size);ImageDraw.Draw(hm).polygon(poly,fill=255);im.putalpha(hm);im.save(O/(name+'-source-fist.png'));hm.save(O/(name+'-source-fist-mask.png'))
 s['layers'].insert(-1,dict(id='source-'+name+'-fist-over-fixed-shaft',path=str((O/(name+'-source-fist.png')).relative_to(R)),width=im.width,height=im.height,transform=transform,kind='explicit-source-bound-hand-crop-and-affine'))
s['layers']=[l for l in s['layers'] if l['id']!='two-gripping-hands-at-fixed-rod-anchors']
(O/'P09-F01-v3.spec.json').write_text(json.dumps(s,indent=2)+'\n');(O/'revision-receipt.json').write_text(json.dumps({'source_cloth_crop':[687,686,727,720],'methods':['Remove original unsupported far upper arm by explicit bounded dark-costume mask','Pose far arm shoulder/elbow/wrist under cape silhouette','Texture conventional arm masks with source costume pixels','Replace vector fists with separately masked source left/right fists'],'generation_calls':0,'fixed_geometry_changed':False},indent=2)+'\n')
