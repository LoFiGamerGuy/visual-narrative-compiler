"""Build deterministic, non-final Blender stage controls from the kitchen geometry contract.

These images are adapter inputs/inspection aids only.  They do not alter the frozen
gauntlet or claim character identity, a final-art render, or a calibrated comic shot.
"""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "outputs" / "blender_kitchen_control_bundle_v2"

def material(name, color):
    item = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    item.diffuse_color = (*color, 1)
    return item

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def cube(name, loc, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

def render(scene, name):
    scene.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x, scene.render.resolution_y = 1216, 832
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.06, 0.06, 0.06)
    for name in ["Floor", "BackWall", "TableTop", "TableLegs", "Anchor_Seated_World_X_NEG", "Anchor_Seated_World_X_POS", "Camera_Table_Seated_Reference"]:
        bpy.data.objects[name].hide_render = True
    floor = material("ControlFloor", (0.22, 0.18, 0.14))
    wall = material("ControlWall", (0.30, 0.25, 0.18))
    table = material("ControlTable", (0.32, 0.12, 0.05))
    cube("ControlFloor", (0, -0.05, 0), (8, 0.1, 6), floor)
    cube("ControlWall", (0, 1.4, 3), (8, 2.8, 0.1), wall)
    cube("ControlTable", (0, 0.72, 0), (3, 0.12, 1.3), table)
    for x, z in [(-1.3, -0.5), (1.3, -0.5), (-1.3, 0.5), (1.3, 0.5)]:
        cube("ControlTableLeg", (x, 0.36, z), (0.12, 0.72, 0.12), table)
    world_x_negative = cube("ControlWorldXNegativeAnchor", (-0.95, 0.65, -0.95), (0.38, 1.3, 0.38), material("NeutralAnchorNegative", (0.35, 0.35, 0.35)))
    world_x_positive = cube("ControlWorldXPositiveAnchor", (0.95, 0.65, -0.95), (0.38, 1.3, 0.38), material("NeutralAnchorPositive", (0.35, 0.35, 0.35)))
    orange, teal = material("RoleOrange", (0.9, 0.32, 0.05)), material("RoleTeal", (0.05, 0.55, 0.65))
    camera = bpy.data.objects["StageReferenceCamera"]
    camera.location = (0, 2.2, -5.7)
    camera.data.lens = 45
    aim(camera, (0, 0.65, 0))
    scene.camera = camera
    bpy.context.view_layer.update()
    render(scene, "base-stage-r1.png")
    # For this declared camera, world X-positive projects to panel-left.
    world_x_positive.data.materials[0] = orange; world_x_negative.data.materials[0] = teal
    render(scene, "g07a-role-id-r1.png")
    render(scene, "g07a-no-change-r1.png")
    world_x_positive.data.materials[0] = teal; world_x_negative.data.materials[0] = orange
    render(scene, "g07b-role-id-r1.png")
    print("BLENDER_KITCHEN_CONTROL_BUNDLE_OK")

if __name__ == "__main__":
    main()
