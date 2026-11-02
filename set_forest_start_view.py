import bpy

path = r"D:\I'm (NOT) in a cage\cage_forest_prototype.blend"
bpy.ops.wm.open_mainfile(filepath=path)
scene = bpy.context.scene
scene.camera = bpy.data.objects.get("Player eye | sharp near-field view")
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_perspective = "CAMERA"
            space.shading.type = "SOLID"
            space.shading.color_type = "MATERIAL"
            space.overlay.show_floor = False
            space.overlay.show_axis_x = False
            space.overlay.show_axis_y = False
bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
print("Saved Blender start view: first-person camera")
