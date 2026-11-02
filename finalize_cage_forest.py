import bpy
import math
from mathutils import Vector

ROOT = r"D:\I'm (NOT) in a cage"
BLEND = ROOT + r"\cage_forest_prototype.blend"
FIRST = ROOT + r"\cage_forest_firstperson.png"
OVERVIEW = ROOT + r"\cage_forest_overview.png"

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

# Rebalance the third-person landmark positions without rebuilding the authored geometry.
for obj in bpy.data.collections["05 | Anomaly B - four-dimensional time block"].objects:
    obj.location.x += 2.0
for obj in bpy.data.collections["07 | The sheep"].objects:
    obj.location.x -= 0.8
    obj.location.y -= 1.0

fill = bpy.data.objects.get("Player-side soft fill for readable nearby grass")
if fill and fill.type == "LIGHT":
    fill.data.energy = 2400

cam = bpy.data.objects.get("Player eye | sharp near-field view")
overview_cam = bpy.data.objects.get("Overview | authored pocket world")
if cam:
    cam.rotation_euler = (Vector((.15, 5.6, .48)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 27
scene.camera = cam

scene.view_settings.exposure = 0.0
scene.eevee.taa_render_samples = 16
scene.eevee.volumetric_samples = 12

backdrop = bpy.data.objects.get("Far field | packed project photo behind the 3D play space")
if backdrop:
    backdrop.hide_render = False
    for mat in backdrop.data.materials:
        for node in mat.node_tree.nodes:
            if node.type == "EMISSION":
                node.inputs["Strength"].default_value = 0.27

scene.camera = cam
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x = 1400
scene.render.resolution_y = 700
scene.render.resolution_percentage = 72
scene.render.filepath = FIRST
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
bpy.ops.render.render(write_still=True)

if backdrop:
    backdrop.hide_render = True
scene.camera = overview_cam
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 72
scene.render.filepath = OVERVIEW
bpy.ops.render.render(write_still=True)

if backdrop:
    backdrop.hide_render = False
scene.camera = cam
scene.render.filepath = FIRST
bpy.ops.wm.save_as_mainfile(filepath=BLEND, compress=True)
print("Finalized:", BLEND)
print("First person:", FIRST)
print("Overview:", OVERVIEW)
