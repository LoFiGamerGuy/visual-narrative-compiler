"""Project the frozen kite's actual face polygons; never modify saved geometry."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'production/structural-pilot/finishing/S/P11/F01-v2'
bpy.context.window.scene=bpy.data.scenes['P11'];scene=bpy.context.scene;bpy.context.view_layer.update()
camera=scene.camera;w,h=scene.render.resolution_x,scene.render.resolution_y
body=next(o for o in scene.objects if o.name.startswith('sentinel.kite_body'))
faces=[]
colors=['#404751','#707789','#454d5c','#a0a6b3','#626b80','#303945']
for i,p in enumerate(body.data.polygons):
 verts=[body.matrix_world@body.data.vertices[j].co for j in p.vertices]
 normal=(verts[1]-verts[0]).cross(verts[2]-verts[0]);center=sum(verts,Vector())/len(verts)
 if normal.dot(camera.location-center)<=0:continue
 points=[];depth=0
 for v in verts:
  q=world_to_camera_view(scene,camera,v);points.append([round(q.x*w,3),round((1-q.y)*h,3)]);depth+=q.z
 faces.append({'points':points,'depth':depth/len(verts),'fill':colors[i]})
faces.sort(key=lambda f:-f['depth'])
svg='\n'.join('<polygon points="'+' '.join(f'{x},{y}' for x,y in f['points'])+'" fill="'+f['fill']+'" stroke="#1d222c" stroke-width="3" stroke-linejoin="round"/>' for f in faces)
(OUT/'kite-facets.json').write_text(json.dumps({'source_blend':'production/structural-pilot/control/v8/scene-all.blend','panel':'P11','faces':faces,'svg':svg},indent=2)+'\n')
print('EXACT_KITE_FACETS_EXPORTED',len(faces))
