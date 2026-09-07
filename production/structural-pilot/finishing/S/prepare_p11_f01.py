"""One explicit conventional P11 actor matte/composition; no generation/inpainting."""
import hashlib,json,math,datetime
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'production/structural-pilot/finishing/S/P11/F01'
RAW=ROOT/'production/structural-pilot/candidates/C00003-7a0a3d591b58c237.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def det(m):return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
def solve(m,b):
 d=det(m);return [det([[b[row] if col==i else m[row][col] for col in range(3)] for row in range(3)])/d for i in range(3)]
def affine(src,dst):
 m=[[x,y,1] for x,y in src];a,c,e=solve(m,[p[0] for p in dst]);b,d,f=solve(m,[p[1] for p in dst]);return [a,b,c,d,e,f]
im=Image.open(RAW).convert('RGB');w,h=im.size
if (OUT/'nera-matte.png').exists():raise SystemExit('Preserve existing F01; choose a new finishing version.')
base=[]
for r,g,b in im.getdata():
 spread=max(r,g,b)-min(r,g,b);light=min(r,g,b)
 # The raw plate has a painted neutral checkerboard. Cream cuffs and colored
 # skin/costume remain because their channel spread exceeds this threshold.
 alpha=0 if spread<23 and light>220 else 255
 if spread<23 and 204<light<=220:alpha=round(255*(220-light)/16)
 base.append(alpha)
background=Image.new('L',(w,h));background.putdata(base);background.save(OUT/'checkerboard-alpha.png')
anchors=json.loads((ROOT/'production/structural-pilot/control/v8/P11-anchors.json').read_text())['anchors']
def target(k):return anchors[k]['pixel']
actors={
 'nera':{'bounds':[390,110,1110,660],'points':[[805,209],[899,400],[797,326]],'targets':[target('nera.head'),target('nera.right_hand'),target('nera.left_hand')],
  'erasures':[[[916,402],[1105,518],[1105,557],[904,424]]],
  'brown_erasure':None},
 'odo':{'bounds':[45,720,540,1320],'points':[[116,788],[461,887],[474,1230]],'targets':[target('odo.left_hand'),target('odo.right_hand'),target('odo.right_ankle')],
  'erasures':[[[101,732],[122,732],[123,765],[100,765]],[[432,825],[470,825],[473,862],[439,868]]],
  'brown_erasure':[84,816,125,1203]},
}
layers=[];results={}
for actor,cfg in actors.items():
 mask=Image.new('L',(w,h));draw=ImageDraw.Draw(mask);draw.rectangle(cfg['bounds'],fill=255)
 pixels=[min(a,b) for a,b in zip(background.getdata(),mask.getdata())];mask.putdata(pixels);draw=ImageDraw.Draw(mask)
 for poly in cfg['erasures']:draw.polygon([tuple(p) for p in poly],fill=0)
 if cfg['brown_erasure']:
  x0,y0,x1,y1=cfg['brown_erasure'];m=mask.load();rgb=im.load()
  for y in range(y0,y1):
   for x in range(x0,x1):
    r,g,b=rgb[x,y]
    if r>g*1.065 and g>b*1.08:m[x,y]=0
 mask.save(OUT/(actor+'-mask.png'))
 rgba=im.convert('RGBA');rgba.putalpha(mask);rgba.save(OUT/(actor+'-matte.png'))
 matrix=affine(cfg['points'],cfg['targets']);cfg['matrix']=matrix
 results[actor]={'source_landmarks_px':cfg['points'],'target_landmarks_px':cfg['targets'],'svg_matrix':matrix,'mask_sha256':sha(OUT/(actor+'-mask.png')),'matte_sha256':sha(OUT/(actor+'-matte.png'))}
 layers.append({'id':actor+'-generated-actor','kind':'explicit-color-key-mask-and-independent-affine','path':str((OUT/(actor+'-matte.png')).relative_to(ROOT)), 'width':w,'height':h,'transform':'matrix('+ ' '.join(str(round(v,9)) for v in matrix)+')'})
 masks=['<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">'%(w,h,w,h),'<title>Source-coordinate prop removal regions; edit these polygons and rebuild</title>','<image href="../../../../candidates/'+RAW.name+'" width="%s" height="%s"/>'%(w,h)]
 for poly in cfg['erasures']:masks.append('<polygon points="'+' '.join('%s,%s'%tuple(p) for p in poly)+'" fill="#e22" fill-opacity=".55"/>')
 if cfg['brown_erasure']:
  x0,y0,x1,y1=cfg['brown_erasure'];masks.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#e22" fill-opacity=".25"/>')
 masks.append('</svg>');(OUT/(actor+'-mask-regions.svg')).write_text('\n'.join(masks))
control='production/structural-pilot/control/v8/'
spec={'id':'SC-20260907-01-S-P11-F01','description':'Conventional actor matting and independent affine placement over fixed editable Blender architecture/threat/props. Unaccepted candidate. No generated environment or prop may replace control geometry.',
 'width':1170,'height':1500,'output_svg':str((OUT/'P11-F01.svg').relative_to(ROOT)), 'matte':'#faf7ec','layers':[
 {'id':'fixed-architecture','path':control+'P11-background.png','kind':'fixed-original-geometry'},
 {'id':'fixed-three-leg-sentinel','path':control+'P11-sentinel.png','kind':'fixed-original-geometry'},
 {'id':'fixed-staff-flask-cable','path':control+'P11-props.png','kind':'fixed-original-geometry'},
 {'id':'fixed-action-vectors','path':control+'P11-effects.png','kind':'fixed-original-geometry'},
 *layers,{'id':'fixed-shutter-partition','path':control+'P11-foreground.png','kind':'fixed-original-geometry'}]}
(OUT/'P11-F01.spec.json').write_text(json.dumps(spec,indent=2)+'\n')
receipt={'schema':'ExplicitMatteReceipt/1','panel':'P11','version':'F01','raw_path':str(RAW.relative_to(ROOT)),'raw_sha256':sha(RAW),'raw_mode':im.mode,'raw_size':[w,h],
 'raw_contract_failures':['RGB painted checkerboard instead of alpha','unwanted generated staff, flask and hanging cord','actor placement/scale differ from fixed v8 source'],
 'matte_algorithm':{'background_rule':'channel spread <23 and minimum channel >220 => alpha 0; linear alpha transition over minimum 204..220; colored pixels preserved','no_segmentation_model':True,'no_generation_or_inpaint':True},
 'actors':results,'editable_region_configuration':actors,'fixed_control_version':'v8','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'limits':['Affine placement aligns the selected hand/pose anchors, not every limb joint.','Fused prop pixels within gripping fingers may remain; visible external prop segments are explicitly removed.','Matte edges and overlap require actual-image inspection.']}
(OUT/'matte-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(results,indent=2))
