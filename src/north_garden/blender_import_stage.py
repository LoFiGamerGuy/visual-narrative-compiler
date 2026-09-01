"""Background Blender import/validation for the kitchen OBJ bootstrap."""
from __future__ import annotations
import hashlib
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
OBJ=ROOT/'assets/stages/kitchen-table-stage-v1.obj'
OUT=ROOT/'assets/stages/kitchen-table-stage-v1.blend'
EXPECTED={'Floor','BackWall','TableTop','TableLegs','Anchor_SOREN_LEFT_SEATED','Anchor_SIGRID_RIGHT_SEATED','Camera_Table_Seated_Reference'}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.wm.obj_import(filepath=str(OBJ))
 names={o.name for o in bpy.context.scene.objects}
 missing=EXPECTED-names
 if missing: raise RuntimeError(f'missing imported objects: {sorted(missing)}')
 # The OBJ camera line is retained as reference geometry; this camera is a stage asset, not a shot plan.
 cam_data=bpy.data.cameras.new('StageReferenceCameraData'); cam=bpy.data.objects.new('StageReferenceCamera',cam_data)
 bpy.context.collection.objects.link(cam); cam.location=(0.0,1.10,-2.65); cam.rotation_euler=(1.5708,0.0,0.0); cam_data.lens=50
 bpy.context.scene.camera=cam
 bpy.context.scene['north_garden_stage_id']='ng-set-kitchen-table-canonical-geometry-r1'
 bpy.context.scene['source_obj_sha256']=sha(OBJ)
 bpy.context.scene['authority_state']='GEOMETRY_BOOTSTRAP_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART'
 bpy.context.scene['shared_asset_boundary']='Set geometry only; comic and animation direction remain separate records.'
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
 print('BLENDER_STAGE_IMPORT_OK')
 print('BLENDER_VERSION='+bpy.app.version_string)
 print('OBJECTS='+','.join(sorted(names)))
 print('BLEND='+str(OUT))
if __name__=='__main__': main()
