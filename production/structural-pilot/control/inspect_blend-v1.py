"""Read the saved scene and image pixels; record actual bounds/alpha facts."""
import json
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'v8'
bpy.context.preferences.filepaths.temporary_directory=str(ROOT/'runtime')
def bounds(obj):
 points=[obj.matrix_world@Vector(v) for v in obj.bound_box]
 return {'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]}
report={'schema':'ActualBlenderMeshInspection/1','status':'GEOMETRY_AND_ALPHA_ONLY_NOT_VISIBLE_SEMANTIC_ACCEPTANCE','panels':{}}
for scene in bpy.data.scenes:
 if not scene.name.startswith('P'):continue
 objects=list(scene.objects)
 info={'limb_ids':sorted({o.get('limb_id') for o in objects if o.get('limb_id')}),
 'partition_bounds':{o.name:bounds(o) for o in objects if o.get('semantic_group')=='foreground'},
 'right_wound_curve_count':len([o for o in objects if 'right_hand.dorsal_scrape' in o.name]),'alpha':{}}
 if scene.name=='P11':
  boots=[bounds(o)['min'][2] for o in objects if o.get('semantic_group')=='actors' and o.name.startswith('nera.') and '.boot' in o.name]
  body=[bounds(o)['max'][2] for o in objects if o.name.startswith('sentinel.kite_body')]
  info['nera_boot_min_z']=min(boots);info['kite_apex_z']=max(body);info['minimum_world_vertical_clearance_m']=min(boots)-max(body)
 for suffix in ['full','background','sentinel','actors','props','foreground','effects']:
  file=OUT/(scene.name+'-'+suffix+'.png');im=bpy.data.images.load(str(file),check_existing=False)
  arr=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(arr);alpha=arr[3::4]
  info['alpha'][suffix]={'min':float(alpha.min()),'max':float(alpha.max()),'transparent_pixels':int((alpha==0).sum()),'pixel_count':int(alpha.size)}
  bpy.data.images.remove(im)
 report['panels'][scene.name]=info
p13=report['panels']['P13'];intervals=[]
for name,b in p13['partition_bounds'].items():
 if b['min'][2]<=.201 and b['max'][2]>=3.20:intervals.append([b['min'][1],b['max'][1]])
intervals.sort();end=intervals[0][1];gaps=[]
for a,b in intervals[1:]:
 if a>end+1e-5:gaps.append([end,a])
 end=max(end,b)
report['p13_actual_partition_y_union']={'intervals':intervals,'min':intervals[0][0],'max':end,'interior_gaps':gaps,'covers_floor_width':intervals[0][0]<=-1.9+1e-5 and end>=1.9-1e-5 and not gaps}
(ROOT/'mesh-alpha-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'partition':report['p13_actual_partition_y_union'],'P11_clearance_m':report['panels']['P11']['minimum_world_vertical_clearance_m']}))
