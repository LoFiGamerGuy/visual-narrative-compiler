"""Render a deterministic, non-final-art calibration view of the stage geometry."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/outputs/blender_stage_calibration_v1/kitchen-table-seated-reference-r4-solid-proxy-wide.png'
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def cube(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
def main():
 scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.render.resolution_x=1216; scene.render.resolution_y=832; scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT); OUT.parent.mkdir(parents=True,exist_ok=True)
 scene.world.color=(0.06,0.06,0.06)
 # OBJ planes/lines are structurally portable but not stable visible primitives. Build a non-final solid proxy from the same coordinates.
 for name in ['Floor','BackWall','TableTop','TableLegs','Anchor_SOREN_LEFT_SEATED','Anchor_SIGRID_RIGHT_SEATED','Camera_Table_Seated_Reference']: bpy.data.objects[name].hide_render=True
 floor=mat('FloorMat',(0.22,0.18,0.14));wall=mat('WallMat',(0.30,0.25,0.18));table=mat('TableMat',(0.32,0.12,0.05))
 cube('CalibrationFloor',(0,-.05,0),(8,.1,6),floor);cube('CalibrationWall',(0,1.4,3),(8,2.8,.1),wall);cube('CalibrationTable',(0,.72,0),(3,.12,1.3),table)
 for x,z in [(-1.3,-.5),(1.3,-.5),(-1.3,.5),(1.3,.5)]: cube('CalibrationTableLeg',(x,.36,z),(.12,.72,.12),table)
 for name,loc,color in [('CalibrationSorenAnchor',(-.95,.65,-.95),(.9,.32,.05)),('CalibrationSigridAnchor',(.95,.65,-.95),(.05,.55,.65))]: cube(name,loc,(.38,1.3,.38),mat(name+'Mat',color))
 # This is deliberately a wide diagnostic camera. It verifies the whole coordinate
 # contract; it is not the legacy comic composition nor a final-art camera.
 cam=bpy.data.objects['StageReferenceCamera'];cam.location=(0,2.20,-5.70);cam.data.lens=45;aim(cam,(0,0.65,0.0));scene.camera=cam;bpy.context.view_layer.update()
 for loc,energy,size in [((-2,-1,2.4),1200,4.0),((2,-0.5,1.6),850,3.0)]:
  data=bpy.data.lights.new('CalibrationArea','AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new('CalibrationArea',data);bpy.context.collection.objects.link(o);o.location=loc;aim(o,(0,0.6,0))
 bpy.ops.render.render(write_still=True);print('BLENDER_CALIBRATION_RENDER_OK');print(OUT)
if __name__=='__main__':main()
