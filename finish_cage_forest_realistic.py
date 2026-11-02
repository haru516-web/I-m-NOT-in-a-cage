import bpy
import os


ROOT = r"D:\I'm (NOT) in a cage"
BLEND = os.path.join(ROOT, "cage_forest_realistic.blend")
FIRST = os.path.join(ROOT, "cage_forest_realistic_firstperson.png")
OVERVIEW = os.path.join(ROOT, "cage_forest_realistic_overview.png")

scene = bpy.context.scene
far = bpy.data.objects.get("Far field | packed project photo behind the 3D play space")
if far and not far.get("cage_farfield_enlarged", False):
    # Keep the source photo's 2:1 aspect while extending it past the portrait camera's upper edge.
    far.scale.x *= 1.72
    far.scale.y *= 1.72
    far["cage_farfield_enlarged"] = True

player = bpy.data.objects.get("Player eye | sharp near-field view")
overview_camera = bpy.data.objects.get("Overview | authored pocket world")
if not player or not overview_camera:
    raise RuntimeError("The player and overview cameras are required in this scene.")

scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.camera = player
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.filepath = FIRST
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("FINISHED_BLEND", BLEND)
print("FIRST_PERSON", FIRST)
print("OVERVIEW", OVERVIEW)
print("FAR_FIELD_SIZE", tuple(round(v, 2) for v in far.dimensions) if far else None)
