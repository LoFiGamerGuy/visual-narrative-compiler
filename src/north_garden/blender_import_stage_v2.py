"""Background import of the neutral-anchor kitchen geometry revision."""
from pathlib import Path
import hashlib
import bpy

ROOT = Path(__file__).resolve().parents[2]
OBJ = ROOT / "assets/stages/kitchen-table-stage-v2-neutral-anchors.obj"
OUT = ROOT / "assets/stages/kitchen-table-stage-v2-neutral-anchors.blend"
EXPECTED = {"Floor", "BackWall", "TableTop", "TableLegs", "Anchor_Seated_World_X_NEG", "Anchor_Seated_World_X_POS", "Camera_Table_Seated_Reference"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.obj_import(filepath=str(OBJ))
    names = {obj.name for obj in bpy.context.scene.objects}
    missing = EXPECTED - names
    if missing: raise RuntimeError(f"missing imported objects: {sorted(missing)}")
    data = bpy.data.cameras.new("StageReferenceCameraData")
    camera = bpy.data.objects.new("StageReferenceCamera", data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, 1.10, -2.65)
    camera.rotation_euler = (1.5708, 0.0, 0.0)
    data.lens = 50
    bpy.context.scene.camera = camera
    bpy.context.scene["north_garden_stage_id"] = "ng-set-kitchen-table-canonical-geometry-r2"
    bpy.context.scene["source_obj_sha256"] = sha(OBJ)
    bpy.context.scene["authority_state"] = "GEOMETRY_BOOTSTRAP_NEUTRAL_ANCHORS_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART"
    bpy.context.scene["shared_asset_boundary"] = "Set geometry only; role binding belongs to comic or animation direction records."
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print("BLENDER_STAGE_V2_IMPORT_OK")

if __name__ == "__main__": main()
