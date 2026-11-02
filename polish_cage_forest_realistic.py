import bpy
import math
import os
import random


ROOT = r"D:\I'm (NOT) in a cage"
REAL_BLEND = os.path.join(ROOT, "cage_forest_realistic.blend")
PREVIEW = os.path.join(ROOT, "cage_forest_realistic_firstperson.png")

scene = bpy.context.scene
if not bpy.data.filepath.lower().endswith("cage_forest_realistic.blend"):
    raise RuntimeError("Open the realistic scene before running this refinement.")

# Clear the player's line down the path. Keep the uncanny reeds on both sides of the well.
targets = {
    0: -4.4,
    1: 4.0,
    2: 3.5,
    3: -4.5,
    11: -4.8,
    12: -4.6,
    13: 4.6,
    14: -4.3,
}
for index, target_x in targets.items():
    prefix = f"Sky reed {index:02d} |"
    group = [o for o in bpy.data.objects if o.name.startswith(prefix)]
    if not group:
        continue
    # Compute the original complete plant centre, then move every stem and leaflet together.
    boxes = [[o.matrix_world @ __import__("mathutils").Vector(c) for c in o.bound_box] for o in group]
    min_x = min(min(p.x for p in box) for box in boxes)
    max_x = max(max(p.x for p in box) for box in boxes)
    centre_x = (min_x + max_x) * 0.5
    delta = target_x - centre_x
    for obj in group:
        obj.location.x += delta

# Dark, textured green keeps the remaining grass in the same light as the forest.
reed = bpy.data.materials.get("Realistic reeds | deep wet green")
if reed:
    bpy.data.materials.remove(reed, do_unlink=True)
reed = bpy.data.materials.new("Realistic reeds | deep wet green")
reed.use_nodes = True
nt = reed.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.9
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
coords = nt.nodes.new("ShaderNodeTexCoord")
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 18.0
noise.inputs["Detail"].default_value = 3.0
nt.links.new(coords.outputs["Generated"], noise.inputs["Vector"])
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.018, 0.042, 0.014, 1.0)
ramp.color_ramp.elements[1].color = (0.12, 0.19, 0.055, 1.0)
nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.16
bump.inputs["Distance"].default_value = 0.018
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
for obj in bpy.data.objects:
    if obj.name.startswith("Sky reed ") and obj.type in {"MESH", "CURVE"}:
        obj.data.materials.clear()
        obj.data.materials.append(reed)

# Reduce the pale, simplified grass colour; the photo based leaf litter remains visible.
for name, color in (
    ("Grass | dark wet green", (0.045, 0.085, 0.028, 1.0)),
    ("Grass | silver tips", (0.13, 0.19, 0.065, 1.0)),
):
    mat = bpy.data.materials.get(name)
    if mat and mat.use_nodes:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = color
        mat.diffuse_color = color

# Replace single-triangle grass with thinner, bent, individually modeled blades.
detail = bpy.data.collections.get("10 | CC0 realistic close detail")
if not detail:
    detail = bpy.data.collections.new("10 | CC0 realistic close detail")
    scene.collection.children.link(detail)
for old in list(bpy.data.objects):
    if old.name == "Grass | curved individual 3D blades":
        bpy.data.objects.remove(old, do_unlink=True)
old_grass = bpy.data.objects.get("Dense low forest grass | 3D blades")
if old_grass:
    old_grass.hide_render = True
    old_grass.hide_set(True)

def ground_z(x, y):
    z = 0.1 * math.sin(x * 0.54 + y * 0.19) + 0.055 * math.sin(y * 0.7 - x * 0.27)
    dx, dy = (x + 3.4) / 1.55, (y + 8.6) / 1.55
    radius = math.sqrt(dx * dx + dy * dy)
    if radius < 1.55:
        z = -3.65 * max(0.0, 1.0 - radius / 1.55) ** 1.28
    elif radius < 2.25:
        t = (radius - 1.55) / 0.7
        fade = 1.0 - t*t*(3.0 - 2.0*t)
        z = z * (1.0-fade) - 0.11*fade
    return z

def path_x(y):
    return 0.45 * math.sin(y * 0.17) + 0.22 * math.sin(y * 0.48)

def grass_material(name, dark, light):
    old = bpy.data.materials.get(name)
    if old:
        bpy.data.materials.remove(old, do_unlink=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.76
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    coords = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 45.0
    noise.inputs["Detail"].default_value = 3.0
    nt.links.new(coords.outputs["Generated"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*dark, 1.0)
    ramp.color_ramp.elements[1].color = (*light, 1.0)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.012
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat

blade_mats = [
    grass_material("Grass | wet narrow blades", (0.022, 0.055, 0.018), (0.075, 0.15, 0.035)),
    grass_material("Grass | pale blade tips", (0.045, 0.085, 0.024), (0.14, 0.22, 0.055)),
]
rng = random.Random(1709)
verts, faces, face_materials = [], [], []
for _ in range(720):
    x = rng.uniform(-13.3, 13.3)
    y = rng.uniform(-19.0, 21.0)
    if abs(x - path_x(y)) < rng.uniform(1.2, 2.15):
        continue
    if math.hypot((x+3.4)/1.7, (y+8.6)/1.7) < 1.15:
        continue
    z0 = ground_z(x, y) + 0.025
    for _ in range(rng.randint(3, 5)):
        angle = rng.random() * math.tau
        height = rng.uniform(0.18, 0.5)
        width = rng.uniform(0.018, 0.042)
        lean = rng.uniform(0.05, 0.28)
        bx = x + rng.uniform(-0.10, 0.10)
        by = y + rng.uniform(-0.10, 0.10)
        side_x, side_y = -math.sin(angle), math.cos(angle)
        base = len(verts)
        for t in (0.0, 0.24, 0.50, 0.76, 1.0):
            cx = bx + math.cos(angle) * lean * t*t + side_x*lean*0.12*math.sin(t*math.pi)
            cy = by + math.sin(angle) * lean * t*t + side_y*lean*0.12*math.sin(t*math.pi)
            cz = z0 + height * (t - 0.10*t*t)
            w = width * (1.0-t)**0.82 + 0.001
            verts.extend(((cx-side_x*w, cy-side_y*w, cz), (cx+side_x*w, cy+side_y*w, cz+0.006)))
        for row in range(4):
            a = base + row*2
            faces.append((a, a+1, a+3, a+2))
            face_materials.append(1 if rng.random() < 0.18 else 0)
mesh = bpy.data.meshes.new("Grass | curved segmented blade mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
for mat in blade_mats:
    mesh.materials.append(mat)
for poly, material_index in zip(mesh.polygons, face_materials):
    poly.material_index = material_index
    poly.use_smooth = True
grass = bpy.data.objects.new("Grass | curved individual 3D blades", mesh)
detail.objects.link(grass)

# Round the stepping stones so their weathered surfaces read as worn slabs rather than sharp cubes.
for obj in bpy.data.objects:
    if not obj.name.startswith("Path stone ") or obj.type != "MESH":
        continue
    bevel = next((m for m in obj.modifiers if m.type == "BEVEL"), None)
    if bevel:
        bevel.width = 0.052
        bevel.segments = 3
    weighted = next((m for m in obj.modifiers if m.type == "WEIGHTED_NORMAL"), None)
    if not weighted:
        weighted = obj.modifiers.new("Stone face normals", "WEIGHTED_NORMAL")
    weighted.keep_sharp = True

# Tone the forest-floor photograph toward damp green-brown soil while retaining the leaf detail.
for name in ("CC0 | Forest floor | shaded leaf litter", "CC0 | Forest floor | deep moss variation"):
    mat = bpy.data.materials.get(name)
    if not mat:
        continue
    hue = next((n for n in mat.node_tree.nodes if n.type == "HUE_SAT"), None)
    if hue:
        hue.inputs["Hue"].default_value = 0.485
        hue.inputs["Saturation"].default_value = 0.60
        hue.inputs["Value"].default_value = 0.54 if "shaded" in name else 0.43

# Preserve soft atmospheric depth without forcing the preview through dense infinite volume.
if scene.world and scene.world.use_nodes:
    for node in scene.world.node_tree.nodes:
        if node.type == "PRINCIPLED_VOLUME":
            node.inputs["Density"].default_value = 0.0032
scene.view_settings.exposure = 0.0
scene.cycles.samples = 10
scene.cycles.use_denoising = True
scene.camera = bpy.data.objects.get("Player eye | sharp near-field view")
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.filepath = PREVIEW
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=REAL_BLEND)
print("REFINED_BLEND", REAL_BLEND)
print("PREVIEW", PREVIEW)
print("REPOSITIONED_REED_GROUPS", len(targets))
print("CURVED_GRASS_BLADES", len(faces)//4)
