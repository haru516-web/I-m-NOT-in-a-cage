import bpy
import math
import os
import random
from mathutils import Vector


ROOT = r"D:\I'm (NOT) in a cage"
ASSETS = os.path.join(ROOT, "assets", "polyhaven_cc0")
DETAIL_COLLECTION = "10 | CC0 realistic close detail"
REAL_BLEND = os.path.join(ROOT, "cage_forest_realistic.blend")
FIRST_RENDER = os.path.join(ROOT, "cage_forest_realistic_firstperson.png")
OVERVIEW_RENDER = os.path.join(ROOT, "cage_forest_realistic_overview.png")

random.seed(271828)
scene = bpy.context.scene


def asset(*parts):
    return os.path.join(ASSETS, *parts)


def get_image(path, non_color=False):
    image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def get_node(nodes, node_type):
    return next(n for n in nodes if n.type == node_type)


def make_pbr(name, diffuse_path, rough_path, normal_path, uv_scale=1.0, bump_strength=0.12, bump_distance=0.025, normal_strength=0.62):
    old = bpy.data.materials.get(name)
    if old:
        bpy.data.materials.remove(old, do_unlink=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (760, 40)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (500, 40)
    bsdf.inputs["Roughness"].default_value = 0.78
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    coords = nt.nodes.new("ShaderNodeTexCoord")
    coords.location = (-780, 40)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-580, 40)
    mapping.inputs["Scale"].default_value = (uv_scale, uv_scale, 1.0)
    nt.links.new(coords.outputs["UV"], mapping.inputs["Vector"])

    color = nt.nodes.new("ShaderNodeTexImage")
    color.name = "CC0 Base Color"
    color.image = get_image(diffuse_path)
    color.extension = "REPEAT"
    color.location = (-330, 260)
    nt.links.new(mapping.outputs["Vector"], color.inputs["Vector"])
    nt.links.new(color.outputs["Color"], bsdf.inputs["Base Color"])

    rough = nt.nodes.new("ShaderNodeTexImage")
    rough.name = "CC0 Roughness"
    rough.image = get_image(rough_path, True)
    rough.extension = "REPEAT"
    rough.location = (-330, 40)
    nt.links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    nt.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    normal_image = nt.nodes.new("ShaderNodeTexImage")
    normal_image.name = "CC0 Tangent Normal"
    normal_image.image = get_image(normal_path, True)
    normal_image.extension = "REPEAT"
    normal_image.location = (-330, -180)
    nt.links.new(mapping.outputs["Vector"], normal_image.inputs["Vector"])
    normal = nt.nodes.new("ShaderNodeNormalMap")
    normal.location = (-70, -160)
    normal.inputs["Strength"].default_value = normal_strength
    nt.links.new(normal_image.outputs["Color"], normal.inputs["Color"])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-330, -430)
    noise.inputs["Scale"].default_value = 52.0
    noise.inputs["Detail"].default_value = 3.0
    nt.links.new(coords.outputs["Generated"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (240, -140)
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(normal.outputs["Normal"], bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_bark_material():
    name = "CC0 | Pine bark photo with fine ridges"
    old = bpy.data.materials.get(name)
    if old:
        bpy.data.materials.remove(old, do_unlink=True)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.88
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    coords = nt.nodes.new("ShaderNodeTexCoord")
    separate = nt.nodes.new("ShaderNodeSeparateXYZ")
    combine = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(coords.outputs["Generated"], separate.inputs["Vector"])
    nt.links.new(separate.outputs["X"], combine.inputs["X"])
    nt.links.new(separate.outputs["Z"], combine.inputs["Y"])
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (4.0, 12.0, 1.0)
    nt.links.new(combine.outputs["Vector"], mapping.inputs["Vector"])

    color = nt.nodes.new("ShaderNodeTexImage")
    color.image = get_image(asset("pine_tree_01", "bark_diff.png"))
    color.extension = "REPEAT"
    nt.links.new(mapping.outputs["Vector"], color.inputs["Vector"])
    nt.links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    normal_image = nt.nodes.new("ShaderNodeTexImage")
    normal_image.image = get_image(asset("pine_tree_01", "bark_nor_gl.png"), True)
    normal_image.extension = "REPEAT"
    nt.links.new(mapping.outputs["Vector"], normal_image.inputs["Vector"])
    normal = nt.nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.56
    nt.links.new(normal_image.outputs["Color"], normal.inputs["Color"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 74.0
    noise.inputs["Detail"].default_value = 2.5
    nt.links.new(coords.outputs["Generated"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.17
    bump.inputs["Distance"].default_value = 0.018
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(normal.outputs["Normal"], bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_ground_variant(name, value):
    mat = make_pbr(
        name,
        asset("forest_floor", "Diffuse.jpg"),
        asset("forest_floor", "Rough.jpg"),
        asset("forest_floor", "nor_gl.jpg"),
        uv_scale=1.0,
        bump_strength=0.10,
        bump_distance=0.028,
        normal_strength=0.54,
    )
    nt = mat.node_tree
    color = next(n for n in nt.nodes if n.name == "CC0 Base Color")
    hue = nt.nodes.new("ShaderNodeHueSaturation")
    hue.inputs["Value"].default_value = value
    hue.inputs["Saturation"].default_value = 0.74
    hue.location = (20, 250)
    bsdf = get_node(nt.nodes, "BSDF_PRINCIPLED")
    for link in list(nt.links):
        if link.to_node == bsdf and link.to_socket == bsdf.inputs["Base Color"]:
            nt.links.remove(link)
    nt.links.new(color.outputs["Color"], hue.inputs["Color"])
    nt.links.new(hue.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def assign(obj, slot, material):
    if slot < len(obj.data.materials):
        obj.data.materials[slot] = material
    else:
        obj.data.materials.append(material)


def add_world_uv(obj, tile_size, center=(0.0, 0.0)):
    if not obj or obj.type != "MESH":
        return
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="WorldScaleUV")
    for loop in obj.data.loops:
        co = obj.data.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((co.x - center[0]) / tile_size, (co.y - center[1]) / tile_size)


def smooth_mesh(obj):
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True


def ground_z(x, y):
    z = 0.1 * math.sin(x * 0.54 + y * 0.19) + 0.055 * math.sin(y * 0.7 - x * 0.27)
    dx, dy = (x + 3.4) / 1.55, (y + 8.6) / 1.55
    r = math.sqrt(dx * dx + dy * dy)
    if r < 1.55:
        z = -3.65 * max(0.0, 1.0 - r / 1.55) ** 1.28
    elif r < 2.25:
        t = max(0.0, min(1.0, (r - 1.55) / 0.7))
        fade = 1.0 - t * t * (3.0 - 2.0 * t)
        z = z * (1.0 - fade) - 0.11 * fade
    return z


def make_twig_material(name, crop, image):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.88
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    u0, v0, u1, v1 = crop
    mapping.inputs["Location"].default_value = (u0, v0, 0.0)
    mapping.inputs["Scale"].default_value = (u1 - u0, v1 - v0, 1.0)
    nt.links.new(tc.outputs["UV"], mapping.inputs["Vector"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "EXTEND"
    nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    try:
        choices = [e.identifier for e in mat.bl_rna.properties["surface_render_method"].enum_items]
        if "BLENDED" in choices:
            mat.surface_render_method = "BLENDED"
        elif "DITHERED" in choices:
            mat.surface_render_method = "DITHERED"
    except Exception:
        pass
    return mat


def add_tube(verts, faces, start, end, radius_start, radius_end, sides=6):
    a, b = Vector(start), Vector(end)
    axis = b - a
    if axis.length < 0.0001:
        return
    axis.normalize()
    ref = Vector((0.0, 0.0, 1.0))
    if abs(axis.dot(ref)) > 0.91:
        ref = Vector((0.0, 1.0, 0.0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u).normalized()
    start_index = len(verts)
    for t, radius in ((0.0, radius_start), (0.56, radius_start * 0.58), (1.0, radius_end)):
        c = a.lerp(b, t)
        for i in range(sides):
            ang = math.tau * i / sides
            p = c + radius * (math.cos(ang) * u + math.sin(ang) * v)
            verts.append(tuple(p))
    for ring in range(2):
        base = start_index + ring * sides
        nxt = base + sides
        for i in range(sides):
            j = (i + 1) % sides
            faces.append((base + i, base + j, nxt + j, nxt + i))


def add_card(verts, faces, uvs, matids, center, width, height, yaw, matid):
    cx, cy, cz = center
    co, si = math.cos(yaw), math.sin(yaw)
    base = len(verts)
    for x, z in ((-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)):
        verts.append((cx + x*co, cy + x*si, cz + z))
    faces.append((base, base + 1, base + 2, base + 3))
    uvs.extend(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)))
    matids.append(matid)


def link_mesh(name, verts, faces, collection, materials, uvs=None, matids=None):
    mesh = bpy.data.meshes.new(name + " Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for mat in materials:
        mesh.materials.append(mat)
    if uvs is not None:
        layer = mesh.uv_layers.new(name="UVMap")
        for i, co in enumerate(uvs):
            layer.data[i].uv = co
    if matids is not None:
        for p, idx in zip(mesh.polygons, matids):
            p.material_index = idx
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def make_fern_mesh(collection, green, pale):
    verts, faces, matids = [], [], []
    stem_v, stem_f = [], []
    for plant_id, (cx, cy, scale, rotation) in enumerate([
        (-1.85, -13.4, 0.86, 0.1), (2.05, -12.0, 0.94, 2.2),
        (-2.3, -5.1, 0.78, 1.3), (2.65, -3.6, 0.92, 0.5),
        (-2.1, 1.5, 0.82, 2.5), (2.5, 3.0, 0.78, 0.8),
        (-4.6, -11.4, 0.7, 1.5), (4.4, -6.5, 0.74, 0.2),
    ]):
        base_z = ground_z(cx, cy) + 0.035
        for frond in range(7):
            phi = rotation + math.tau * frond / 7.0 + random.uniform(-0.14, 0.14)
            length = scale * random.uniform(0.64, 1.08)
            rise = scale * random.uniform(0.38, 0.64)
            endpoint = (cx + math.cos(phi)*length, cy + math.sin(phi)*length, base_z + rise)
            add_tube(stem_v, stem_f, (cx, cy, base_z), endpoint, scale*0.014, scale*0.006, 5)
            for pair in range(1, 8):
                t = pair / 8.5
                px = cx + math.cos(phi)*length*t
                py = cy + math.sin(phi)*length*t
                pz = base_z + rise*t + scale*0.025*math.sin(t*math.pi)
                taper = math.sin(t*math.pi) ** 0.72
                leaflet_len = scale * (0.16 + 0.10*(1-t)) * taper
                for side in (-1, 1):
                    la = phi + side*0.98
                    tip = (px + math.cos(la)*leaflet_len, py + math.sin(la)*leaflet_len, pz + leaflet_len*0.32)
                    mid = (px + math.cos(la)*leaflet_len*0.48, py + math.sin(la)*leaflet_len*0.48, pz + leaflet_len*0.23)
                    width = leaflet_len * 0.19
                    perp = (-math.sin(la)*width, math.cos(la)*width, width*0.16)
                    base = len(verts)
                    verts.extend([
                        (px, py, pz),
                        (mid[0]+perp[0], mid[1]+perp[1], mid[2]+perp[2]),
                        tip,
                        (mid[0]-perp[0], mid[1]-perp[1], mid[2]-perp[2]),
                    ])
                    faces.append((base, base+1, base+2, base+3))
                    matids.append(1 if random.random() < 0.18 else 0)
    stem_obj = link_mesh("Fern rachises | 3D stems", stem_v, stem_f, collection, [pale])
    smooth_mesh(stem_obj)
    leaf_obj = link_mesh("Fern fronds | layered individual leaflets", verts, faces, collection, [green, pale], matids=matids)
    for p in leaf_obj.data.polygons:
        p.use_smooth = True
    return stem_obj, leaf_obj


# Rebuild only the collection owned by this realism pass; the original blockout stays intact.
old_collection = bpy.data.collections.get(DETAIL_COLLECTION)
if old_collection:
    for obj in list(old_collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old_collection)
detail = bpy.data.collections.new(DETAIL_COLLECTION)
scene.collection.children.link(detail)

# CC0 PBR materials, with true metre-scale UVs on the walkable ground.
floor = make_ground_variant("CC0 | Forest floor | shaded leaf litter", 0.62)
floor_moss = make_ground_variant("CC0 | Forest floor | deep moss variation", 0.46)
stone = make_pbr(
    "CC0 | Weathered stone tiles 02",
    asset("stone_tiles_02", "Diffuse.jpg"),
    asset("stone_tiles_02", "Rough.jpg"),
    asset("stone_tiles_02", "nor_gl.jpg"),
    uv_scale=0.23,
    bump_strength=0.13,
    bump_distance=0.018,
    normal_strength=0.72,
)
bark = make_bark_material()

terrain = bpy.data.objects.get("Uneven forest floor with real pit depression")
path = bpy.data.objects.get("Worn footpath | continuous 3D surface")
pit = bpy.data.objects.get("Deep hidden well | exposed inner rock")
if terrain:
    add_world_uv(terrain, 3.4)
    assign(terrain, 0, floor)
    assign(terrain, 1, floor_moss)
if path:
    add_world_uv(path, 2.6)
    assign(path, 0, stone)
for obj in bpy.data.objects:
    if obj.name.startswith("Path stone "):
        assign(obj, 0, stone)
    if obj.name.startswith("Well lip | broken stone"):
        assign(obj, 0, stone)
    if obj.name.startswith("Spatial scan | road fragment"):
        assign(obj, 0, stone)
    if obj.name.startswith("Time block | slice") and "base" in obj.name:
        assign(obj, 0, stone)
if pit:
    # Cylindrical UVs keep the texture aligned down the exposed inner rock wall.
    uv = pit.data.uv_layers.active or pit.data.uv_layers.new(name="UVMap")
    for poly in pit.data.polygons:
        loops = list(poly.loop_indices)
        us = []
        coords = []
        for loop_index in loops:
            co = pit.data.vertices[pit.data.loops[loop_index].vertex_index].co
            u = (math.atan2(co.y + 8.6, co.x + 3.4) / math.tau) % 1.0
            v = (co.z + 3.65) / 3.65
            us.append(u)
            coords.append((loop_index, u, v))
        if max(us) - min(us) > 0.5:
            coords = [(idx, u + (1.0 if u < 0.5 else 0.0), v) for idx, u, v in coords]
        for idx, u, v in coords:
            uv.data[idx].uv = (u * 1.1, v)
    assign(pit, 0, stone)
    if len(pit.data.materials) > 1:
        assign(pit, 1, stone)

# Add natural bark maps to every authored trunk, limb, root and hanging branch.
for obj in bpy.data.objects:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    for i, material in enumerate(list(obj.data.materials)):
        if material and material.name.startswith("Bark |"):
            obj.data.materials[i] = bark
    if obj.name.startswith("Forest trunk") or "grows down from the sky" in obj.name:
        if obj.type == "MESH":
            smooth_mesh(obj)
            bevel = obj.modifiers.new("Rounded bark ridges", "BEVEL")
            bevel.width = 0.025
            bevel.segments = 2
            bevel.limit_method = "ANGLE"

# Procedural surface breakup for the oxidized memory frame and the uncanny scan pieces.
for name in ("Memory frame | oxidized bronze", "Time slices | pale stone", "Spatial scan | slate", "Spatial scan | broken pale facets"):
    mat = bpy.data.materials.get(name)
    if not mat or not mat.use_nodes:
        continue
    nt = mat.node_tree
    bsdf = get_node(nt.nodes, "BSDF_PRINCIPLED")
    coords = next((n for n in nt.nodes if n.type == "TEX_COORD"), None)
    if not coords:
        coords = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0 if "bronze" in name else 18.0
    noise.inputs["Detail"].default_value = 4.0
    nt.links.new(coords.outputs["Generated"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.018
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    # Keep the original shading and add fine surface relief.
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# Move the six photo-scanned CC0 moss rocks around the real pit; preserve the asset UVs.
rock_gltf = asset("rock_moss_set_01", "model.gltf")
rock_names = [f"rock_moss_set_01_rock{i:02d}" for i in range(1, 7)]
if not all(bpy.data.objects.get(name) for name in rock_names):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=rock_gltf)
    imported = [o for o in bpy.data.objects if o not in before]
    for obj in imported:
        for previous in list(obj.users_collection):
            previous.objects.unlink(obj)
        detail.objects.link(obj)
rock_positions = [
    (-5.05, -8.62, 0.47, -0.25), (-2.05, -10.12, 0.38, 0.70),
    (-3.66, -6.40, 0.39, 1.30), (-5.15, -7.15, 0.35, 2.00),
    (-1.77, -7.55, 0.36, -0.85), (-4.25, -10.45, 0.33, 0.32),
]
for name, (x, y, scale, yaw) in zip(rock_names, rock_positions):
    obj = bpy.data.objects.get(name)
    if not obj:
        continue
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    detail.objects.link(obj)
    obj.scale = (scale, scale, scale)
    obj.rotation_euler[2] = yaw
    local_min_z = min(corner[2] for corner in obj.bound_box)
    obj.location = (x, y, ground_z(x, y) - local_min_z * scale + 0.015)
    smooth_mesh(obj)

# Reuse the moss-rock models as linked instances farther along the walkable world.
extra_rocks = [
    (0, (-5.1, -2.8, 0.36, 0.4)), (2, (4.5, -1.5, 0.43, 1.2)),
    (4, (-5.4, 3.3, 0.37, -0.7)), (1, (5.7, 7.0, 0.39, 0.5)),
    (3, (-7.0, 6.4, 0.42, 2.0)),
]
for j, (source_index, (x, y, scale, yaw)) in enumerate(extra_rocks):
    source = bpy.data.objects.get(rock_names[source_index])
    if not source:
        continue
    obj = source.copy()
    obj.data = source.data
    obj.name = f"CC0 moss rock | linked instance {j+1:02d}"
    detail.objects.link(obj)
    obj.scale = (scale, scale, scale)
    obj.rotation_euler[2] = yaw
    local_min_z = min(corner[2] for corner in obj.bound_box)
    obj.location = (x, y, ground_z(x, y) - local_min_z * scale + 0.012)

# Real photographed pine sprigs on crossed planes, supported by modeled 3D branches.
twig_image = get_image(asset("pine_tree_01", "twig_diff.png"))
twig_a = make_twig_material("CC0 | photographed pine sprig | upright", (0.005, 0.55, 0.245, 0.995), twig_image)
twig_b = make_twig_material("CC0 | photographed pine sprig | lateral", (0.65, 0.40, 0.995, 0.67), twig_image)
branch_v, branch_f = [], []
fol_v, fol_f, fol_uv, fol_mi = [], [], [], []
trunks = sorted([o for o in bpy.data.objects if o.name.startswith("Forest trunk ")], key=lambda o: o.name)
for tree_index, trunk in enumerate(trunks):
    dims = trunk.dimensions
    h = max(float(dims.z), 5.0)
    x, y = float(trunk.location.x), float(trunk.location.y)
    base_z = float(trunk.location.z - h*0.5)
    phase = random.uniform(-0.4, 0.4)
    for old in bpy.data.objects:
        if old.name.startswith(f"Forest canopy {tree_index:02d}.") or old.name.startswith("Misty broadleaf cluster"):
            old.hide_render = True
            old.hide_set(True)
    for layer in range(5):
        frac = 0.40 + layer*0.12 + random.uniform(-0.018, 0.018)
        z = base_z + h*frac
        radius = h*(0.28 - layer*0.043) * random.uniform(0.88, 1.10)
        branch_count = 6
        for arm in range(branch_count):
            ang = phase + math.tau*arm/branch_count + layer*0.31 + random.uniform(-0.12, 0.12)
            r = radius*random.uniform(0.78, 1.08)
            start = (x + math.cos(ang)*0.06, y + math.sin(ang)*0.06, z)
            end = (x + math.cos(ang)*r, y + math.sin(ang)*r, z - h*random.uniform(0.035, 0.095))
            add_tube(branch_v, branch_f, start, end, h*0.011*(1.0-layer*0.08), h*0.0038, 5)
            a_width, a_height = h*0.085, h*0.17
            b_width, b_height = h*0.16, h*0.095
            add_card(fol_v, fol_f, fol_uv, fol_mi, end, a_width, a_height, ang, 0)
            add_card(fol_v, fol_f, fol_uv, fol_mi, (end[0], end[1], end[2]-h*0.015), b_width, b_height, ang+math.pi*0.5, 1)
    # A small tuft completes the irregular, open crown.
    crown_z = base_z + h*0.93
    for arm in range(4):
        ang = phase + math.tau*arm/4.0
        add_card(fol_v, fol_f, fol_uv, fol_mi, (x+math.cos(ang)*h*.07,y+math.sin(ang)*h*.07,crown_z), h*.075, h*.15, ang, 0)

branch_obj = link_mesh("Pine scaffold | tapered modeled limbs", branch_v, branch_f, detail, [bark])
foliage_obj = link_mesh("Pine crowns | CC0 photographed 3D cards", fol_v, fol_f, detail, [twig_a, twig_b], fol_uv, fol_mi)
for p in branch_obj.data.polygons:
    p.use_smooth = True

# Close-range ferns are made of individual bent 3D leaflets, not background cards.
fern_green = bpy.data.materials.new("Living fern | layered green")
fern_green.use_nodes = True
fn = fern_green.node_tree
fbs = get_node(fn.nodes, "BSDF_PRINCIPLED")
fbs.inputs["Roughness"].default_value = 0.7
ftex = fn.nodes.new("ShaderNodeTexNoise")
ftex.inputs["Scale"].default_value = 5.0
ftex.inputs["Detail"].default_value = 4.0
ftex.inputs["Roughness"].default_value = 0.72
fcoord = fn.nodes.new("ShaderNodeTexCoord")
framp = fn.nodes.new("ShaderNodeValToRGB")
framp.color_ramp.elements[0].position = 0.22
framp.color_ramp.elements[0].color = (0.018, 0.065, 0.032, 1.0)
framp.color_ramp.elements[1].position = 0.78
framp.color_ramp.elements[1].color = (0.12, 0.26, 0.085, 1.0)
fn.links.new(fcoord.outputs["Generated"], ftex.inputs["Vector"])
fn.links.new(ftex.outputs["Fac"], framp.inputs["Fac"])
fn.links.new(framp.outputs["Color"], fbs.inputs["Base Color"])
fern_bump = fn.nodes.new("ShaderNodeBump")
fern_bump.inputs["Strength"].default_value = 0.18
fern_bump.inputs["Distance"].default_value = 0.018
fn.links.new(ftex.outputs["Fac"], fern_bump.inputs["Height"])
fn.links.new(fern_bump.outputs["Normal"], fbs.inputs["Normal"])
fern_pale = bpy.data.materials.new("Living fern | stem and new tips")
fern_pale.diffuse_color = (0.22, 0.34, 0.10, 1.0)
fern_pale.use_nodes = True
get_node(fern_pale.node_tree.nodes, "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.12, 0.23, 0.065, 1.0)
get_node(fern_pale.node_tree.nodes, "BSDF_PRINCIPLED").inputs["Roughness"].default_value = 0.72
make_fern_mesh(detail, fern_green, fern_pale)

# A CC0 forest HDRI supplies realistic reflections and soft open-sky light; the supplied photo stays as the far-field image.
world = scene.world or bpy.data.worlds.new("Forest world")
scene.world = world
world.use_nodes = True
wn = world.node_tree
background = get_node(wn.nodes, "BACKGROUND")
env = next((n for n in wn.nodes if n.type == "TEX_ENVIRONMENT"), None)
if not env:
    env = wn.nodes.new("ShaderNodeTexEnvironment")
env.image = get_image(asset("forest_slope", "lighting.hdr"))
env.location = (-430, 180)
background.inputs["Strength"].default_value = 0.32
wn.links.new(env.outputs["Color"], background.inputs["Color"])
volume = next((n for n in wn.nodes if n.type == "PRINCIPLED_VOLUME"), None)
if volume:
    volume.inputs["Density"].default_value = 0.0045
    volume.inputs["Color"].default_value = (0.48, 0.56, 0.51, 1.0)
    volume.inputs["Anisotropy"].default_value = 0.25

# Use a path-traced still preview with denoising; the playable world remains fully 3D in the near field.
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.preview_samples = 12
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.2
scene.view_settings.gamma = 1.0
scene.camera.data.dof.use_dof = False
for obj in bpy.data.objects:
    if obj.type == "LIGHT":
        obj.data.use_shadow = True

# Portrait first-person preview to inspect the actual walking range at the same framing used for the shrine review.
player = bpy.data.objects.get("Player eye | sharp near-field view")
overview = bpy.data.objects.get("Overview | authored pocket world")
if not player or not overview:
    raise RuntimeError("Expected first-person and overview cameras were not found.")
player.data.lens = 29.0
scene.camera = player
scene.render.resolution_x, scene.render.resolution_y = 720, 1280
scene.render.filepath = FIRST_RENDER
scene.render.resolution_percentage = 100

# Keep the editable source portable while retaining the local CC0 source files and attribution records.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=REAL_BLEND)
print("REALISTIC_BLEND", REAL_BLEND)
print("FIRST_RENDER", FIRST_RENDER)
print("OVERVIEW_RENDER", OVERVIEW_RENDER)
print("TEXTURED_TREES", len(trunks), "FOLIAGE_QUADS", len(fol_f), "BRANCH_FACES", len(branch_f))
print("PBR_MATERIALS", floor.name, stone.name, bark.name)
