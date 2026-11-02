import bpy
import math
import random
from mathutils import Vector


ROOT = r"D:\I'm (NOT) in a cage"
BLEND_PATH = ROOT + r"\cage_forest_prototype.blend"
FIRST_RENDER = ROOT + r"\cage_forest_firstperson.png"
OVERVIEW_RENDER = ROOT + r"\cage_forest_overview.png"
REFERENCE_IMAGE = ROOT + r"\仮イメージ１.jpg"

random.seed(18)

# This is a fresh background Blender process with its startup scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

scene = bpy.context.scene
for col in list(bpy.data.collections):
    if col.name != "Collection":
        bpy.data.collections.remove(col)
base = bpy.data.collections.get("Collection")
if base:
    base.name = "00 | Scene"
    if base.name not in scene.collection.children:
        pass

COL = None


def collection(name):
    global COL
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    COL = col
    return col


def place(obj):
    if COL:
        for old in list(obj.users_collection):
            old.objects.unlink(obj)
        COL.objects.link(obj)
    return obj


def material(name, color, roughness=0.82, emission=None, emission_strength=0.0, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = (*emission, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


M = {
    "earth": material("Earth | wet charcoal loam", (0.12, 0.16, 0.15)),
    "earth2": material("Earth | moss shadow", (0.16, 0.22, 0.18)),
    "path": material("Path | old slate", (0.19, 0.225, 0.22)),
    "stone": material("Stone | cold basalt", (0.105, 0.135, 0.14)),
    "stone2": material("Stone | pale lichen", (0.23, 0.28, 0.26)),
    "bark": material("Bark | black wet wood", (0.16, 0.12, 0.09)),
    "bark2": material("Bark | silvered ridges", (0.30, 0.29, 0.23)),
    "leaf": material("Leaves | deep forest", (0.13, 0.24, 0.18)),
    "leaf2": material("Leaves | mist green", (0.25, 0.36, 0.28)),
    "grass": material("Grass | dark wet green", (0.24, 0.34, 0.20)),
    "grass2": material("Grass | silver tips", (0.42, 0.49, 0.31)),
    "portal": material("Memory frame | oxidized bronze", (0.15, 0.24, 0.22), metallic=0.55),
    "glow": material("Memory frame | cold phosphor", (0.13, 0.42, 0.46), emission=(0.15, 0.72, 0.78), emission_strength=1.5),
    "snow": material("Inside memory | old snow", (0.47, 0.56, 0.59)),
    "ice": material("Inside memory | blue shadow", (0.17, 0.30, 0.36), metallic=0.15),
    "time": material("Time slices | pale stone", (0.32, 0.38, 0.38), metallic=0.25),
    "timeglow": material("Time slices | thin light", (0.39, 0.61, 0.61), emission=(0.24, 0.6, 0.62), emission_strength=1.1),
    "scan": material("Spatial scan | slate", (0.26, 0.32, 0.34), metallic=0.2),
    "scan2": material("Spatial scan | broken pale facets", (0.44, 0.49, 0.47), metallic=0.12),
    "sheep": material("Sheep | muted wool", (0.57, 0.57, 0.49)),
    "wool": material("Sheep | wool highlights", (0.73, 0.72, 0.62)),
    "face": material("Sheep | face", (0.23, 0.20, 0.17)),
    "eye": material("Sheep | eyes", (0.025, 0.03, 0.03), roughness=0.3),
    "water": material("Well | unseen water", (0.018, 0.035, 0.045), roughness=0.18, metallic=0.32),
}


def mesh_obj(name, verts, faces, mat, col=None, material_indices=None):
    me = bpy.data.meshes.new(name + " Mesh")
    me.from_pydata(verts, [], faces)
    me.materials.append(mat)
    if material_indices:
        for poly, idx in zip(me.polygons, material_indices):
            poly.material_index = idx
    me.update()
    ob = bpy.data.objects.new(name, me)
    (col or COL).objects.link(ob)
    return ob


def cube(name, loc, dims, mat, bevel=0.0, col=None, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = dims
    if rot:
        ob.rotation_euler = rot
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Soft worn edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return place(ob) if col is None else _move_to(ob, col)


def _move_to(ob, col):
    for old in list(ob.users_collection):
        old.objects.unlink(ob)
    col.objects.link(ob)
    return ob


def ico(name, loc, scale, mat, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    return place(ob)


def uv(name, loc, scale, mat, segments=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return place(ob)


def cylinder(name, loc, radius, depth, mat, vertices=12, rot=None, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    if rot:
        ob.rotation_euler = rot
    if mat:
        ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Rounded rim", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return place(ob)


def cone(name, loc, radius1, radius2, depth, mat, vertices=9):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return place(ob)


def curve_tube(name, points, radii, mat, bevel_depth=0.2, resolution=8, col=None):
    cu = bpy.data.curves.new(name + " Curve", "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = resolution
    cu.bevel_depth = bevel_depth
    cu.bevel_resolution = 3
    spl = cu.splines.new("POLY")
    spl.points.add(len(points) - 1)
    for p, xyz, radius in zip(spl.points, points, radii):
        p.co = (xyz[0], xyz[1], xyz[2], 1.0)
        p.radius = radius
    ob = bpy.data.objects.new(name, cu)
    (col or COL).objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def ground_z(x, y):
    z = 0.1 * math.sin(x * 0.54 + y * 0.19) + 0.055 * math.sin(y * 0.7 - x * 0.27)
    dx = (x + 3.4) / 1.55
    dy = (y + 8.6) / 1.55
    r = math.sqrt(dx * dx + dy * dy)
    if r < 1.55:
        z = -3.65 * max(0.0, 1.0 - r / 1.55) ** 1.28
    elif r < 2.25:
        fade = 1.0 - smoothstep((r - 1.55) / 0.7)
        z = z * (1.0 - fade) - 0.11 * fade
    return z


def path_x(y):
    return 0.45 * math.sin(y * 0.17) + 0.22 * math.sin(y * 0.48)


def build_terrain():
    collection("01 | Hand-built terrain and path")
    nx, ny = 61, 91
    xmin, xmax, ymin, ymax = -14.0, 14.0, -20.0, 23.0
    verts = []
    faces = []
    for j in range(ny):
        y = ymin + (ymax - ymin) * j / (ny - 1)
        for i in range(nx):
            x = xmin + (xmax - xmin) * i / (nx - 1)
            verts.append((x, y, ground_z(x, y)))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            b = a + 1
            c = a + nx
            d = c + 1
            faces.append((a, b, d, c))
    terrain = mesh_obj("Uneven forest floor with real pit depression", verts, faces, M["earth"])
    terrain.data.materials.append(M["earth2"])
    for poly in terrain.data.polygons:
        if random.random() < 0.24:
            poly.material_index = 1

    # A continuous ground path, modeled as a raised, hand-authored ribbon.
    path_verts, path_faces = [], []
    n = 120
    for i in range(n):
        y = ymin + 1.0 + (ymax - ymin - 2.0) * i / (n - 1)
        cx = path_x(y)
        width = 1.72 + 0.17 * math.sin(y * 0.31)
        for x in (cx - width / 2, cx + width / 2):
            path_verts.append((x, y, ground_z(x, y) + 0.065))
        if i < n - 1:
            a = 2 * i
            path_faces.append((a, a + 1, a + 3, a + 2))
    mesh_obj("Worn footpath | continuous 3D surface", path_verts, path_faces, M["path"])

    # Pavers follow the path and make the close walking range readable.
    for i in range(76):
        y = -18.2 + i * 0.48
        x = path_x(y) + random.uniform(-0.46, 0.46)
        z = ground_z(x, y) + 0.12
        size = random.uniform(0.38, 0.78)
        ob = cube("Path stone %02d" % i, (x, y, z), (size, random.uniform(0.30, 0.65), random.uniform(0.08, 0.17)), random.choice([M["path"], M["stone"], M["stone2"]]), bevel=0.035)
        ob.rotation_euler[2] = random.uniform(-0.35, 0.35)

    # The pit is an actual descending mesh, not a dark decal.
    px, py = -3.4, -8.6
    seg = 40
    rings = [(1.52, -0.14), (1.32, -0.58), (1.02, -1.65), (0.69, -2.85), (0.36, -3.58)]
    v, f = [], []
    for rr, zbase in rings:
        for k in range(seg):
            a = 2 * math.pi * k / seg
            jitter = 1.0 + 0.04 * math.sin(a * 7.0) + random.uniform(-0.025, 0.025)
            z = zbase + random.uniform(-0.07, 0.07)
            v.append((px + rr * jitter * math.cos(a), py + rr * jitter * math.sin(a), z))
    for ri in range(len(rings) - 1):
        for k in range(seg):
            a = ri * seg + k
            b = ri * seg + (k + 1) % seg
            c = (ri + 1) * seg + (k + 1) % seg
            d = (ri + 1) * seg + k
            f.append((a, b, c, d))
    pit = mesh_obj("Deep hidden well | exposed inner rock", v, f, M["stone"])
    pit.data.materials.append(M["stone2"])
    for p in pit.data.polygons:
        if random.random() < 0.2:
            p.material_index = 1
    cylinder("Well bottom | lightless water", (px, py, -3.69), 0.47, 0.10, M["water"], vertices=32)
    # Broken stones around the lip.
    for i in range(26):
        a = 2 * math.pi * i / 26 + random.uniform(-0.08, 0.08)
        rr = random.uniform(1.45, 1.88)
        x, y = px + rr * math.cos(a), py + rr * math.sin(a)
        z = ground_z(x, y) + random.uniform(0.05, 0.16)
        ob = ico("Well lip | broken stone %02d" % i, (x, y, z), (random.uniform(0.22, 0.46), random.uniform(0.20, 0.39), random.uniform(0.13, 0.30)), random.choice([M["stone"], M["stone2"]]), subdivisions=1)
        ob.rotation_euler[2] = a


def build_grass():
    collection("02 | Grass, reeds and close detail")
    verts, faces, mi = [], [], []
    # Grass is one combined mesh so the sharply visible play area remains light enough to edit.
    attempts = 1300
    for _ in range(attempts):
        x = random.uniform(-13.3, 13.3)
        y = random.uniform(-19.0, 21.0)
        cx = path_x(y)
        if abs(x - cx) < random.uniform(1.2, 2.25):
            continue
        if math.hypot((x + 3.4) / 1.7, (y + 8.6) / 1.7) < 1.15:
            continue
        z0 = ground_z(x, y) + 0.02
        for _blade in range(random.randint(2, 4)):
            ang = random.random() * math.tau
            h = random.uniform(0.20, 0.72)
            w = random.uniform(0.065, 0.15)
            lean = random.uniform(0.08, 0.42)
            bx = x + random.uniform(-0.11, 0.11)
            by = y + random.uniform(-0.11, 0.11)
            dx, dy = math.cos(ang) * w, math.sin(ang) * w
            tipx = bx + math.cos(ang + 0.7) * lean
            tipy = by + math.sin(ang + 0.7) * lean
            i = len(verts)
            verts.extend([(bx - dx, by - dy, z0), (bx + dx, by + dy, z0), (tipx, tipy, z0 + h)])
            faces.append((i, i + 1, i + 2))
            mi.append(1 if random.random() < 0.13 else 0)
    grass = mesh_obj("Dense low forest grass | 3D blades", verts, faces, M["grass"])
    grass.data.materials.append(M["grass2"])
    for p, idx in zip(grass.data.polygons, mi):
        p.material_index = idx

    # Taller, uncanny reeds rise above the ordinary vegetation and frame the well.
    for i in range(15):
        a = 2 * math.pi * i / 15
        rr = random.uniform(1.6, 4.6)
        x, y = -3.4 + rr * math.cos(a), -8.6 + rr * math.sin(a)
        z = ground_z(x, y)
        height = random.uniform(5.0, 10.0)
        leanx, leany = random.uniform(-1.0, 1.0), random.uniform(-0.8, 0.8)
        pts = [(x, y, z), (x + leanx * 0.25, y + leany * 0.25, z + height * 0.34), (x + leanx * 0.7, y + leany * 0.6, z + height * 0.73), (x + leanx, y + leany, z + height)]
        curve_tube("Sky reed %02d | tall blade" % i, pts, [1.0, 0.76, 0.48, 0.08], M["grass2"] if i % 4 == 0 else M["grass"], 0.055)
        for j in range(3):
            t = 0.38 + j * 0.16
            bx = x + leanx * t
            by = y + leany * t
            bz = z + height * t
            side = -1 if (i + j) % 2 else 1
            curve_tube("Sky reed %02d | leaf" % i, [(bx, by, bz), (bx + side * 0.55, by - 0.2, bz + 0.18), (bx + side * 1.05, by - 0.25, bz + 0.42)], [0.8, 0.45, 0.02], M["grass2"], 0.035)


def build_forest():
    collection("03 | Forest and descending tree")
    # Side forest: small authored silhouettes, kept outside the trail's central view.
    for i in range(30):
        side = -1 if i % 2 == 0 else 1
        y = -17 + (i // 2) * 2.65 + random.uniform(-0.5, 0.5)
        x = side * random.uniform(7.5, 13.5)
        z = ground_z(x, y)
        h = random.uniform(7.0, 12.5)
        trunk_r = random.uniform(0.28, 0.58)
        cylinder("Forest trunk %02d" % i, (x, y, z + h * 0.43), trunk_r, h * 0.86, M["bark"], vertices=8)
        if i % 3:
            for layer in range(3):
                hh = h * (0.38 + layer * 0.18)
                cone("Forest canopy %02d.%d" % (i, layer), (x + random.uniform(-0.25, 0.25), y, z + hh), h * (0.28 - layer * 0.045), 0.06, h * 0.48, M["leaf"] if layer % 2 else M["leaf2"], vertices=7)
        else:
            for _ in range(7):
                ico("Misty broadleaf cluster", (x + random.uniform(-1.8, 1.8), y + random.uniform(-1, 1), z + h * random.uniform(0.55, 0.95)), (random.uniform(1.2, 2.1), random.uniform(1.0, 1.8), random.uniform(0.8, 1.5)), M["leaf"] if random.random() < 0.7 else M["leaf2"], subdivisions=1)

    # Giant tree enters from above; its roots grow downward through the fog.
    main = [(-11.3, 4.5, 20.0), (-9.1, 4.3, 16.0), (-7.2, 4.7, 12.7), (-5.5, 5.4, 9.0), (-4.2, 5.7, 4.9), (-4.0, 5.0, 0.1)]
    curve_tube("The tree that grows down from the sky", main, [1.85, 1.55, 1.27, 0.96, 0.63, 0.34], M["bark"], 0.62, resolution=12)
    # Sky crown branches and downward root-fingers.
    branches = [
        ([(-7.8, 4.5, 19), (-9.2, 4.1, 17), (-10.8, 3.6, 15.3), (-11.8, 3.4, 12.9)], [1.0, .78, .44, .04], .36),
        ([(-6.2, 4.5, 16), (-4.9, 3.0, 17.7), (-3.1, 2.1, 18.3), (-1.8, 1.9, 18.8)], [1.0, .68, .34, .02], .35),
        ([(-4.2, 4.7, 12.7), (-2.5, 3.5, 14.1), (-0.5, 2.7, 14.5), (1.2, 2.4, 14.3)], [1.0, .62, .31, .02], .27),
        ([(-2.5, 5.4, 9.0), (-4.0, 7.0, 7.3), (-5.2, 8.2, 4.6), (-6.1, 8.7, 1.7)], [1.0, .65, .4, .03], .30),
        ([(-1.4, 5.2, 4.0), (0.5, 6.1, 3.1), (2.6, 6.5, 1.6), (4.8, 7.1, .1)], [1.0, .7, .4, .03], .25),
        ([(-1.1, 5.1, 1.2), (-2.3, 4.0, .8), (-3.1, 2.5, .2)], [1.0, .6, .04], .28),
    ]
    for i, (pts, radii, depth) in enumerate(branches):
        pts = [(px - 3.0, py, pz) for px, py, pz in pts]
        curve_tube("Sky-root branch %02d" % i, pts, radii, M["bark2"] if i in (0, 2) else M["bark"], depth)
    # Hanging moss / root threads beneath the canopy.
    for i in range(19):
        x = random.uniform(-12.0, -4.6)
        y = random.uniform(2.0, 6.4)
        top = random.uniform(12.5, 18.0)
        length = random.uniform(2.0, 6.0)
        curve_tube("Hanging root %02d" % i, [(x, y, top), (x + random.uniform(-.5, .5), y, top - length * .5), (x + random.uniform(-.8, .8), y + .2, top - length)], [1.0, .38, .01], M["bark"], random.uniform(.045, .09))


def add_frame_bar(name, loc, dims, mat, bevel=0.08):
    return cube(name, loc, dims, mat, bevel=bevel)


def build_memory_frame():
    collection("04 | Anomaly A - walk-in memory frame")
    x, y, z = 0.3, 6.9, 2.7
    w, h, d = 4.9, 5.4, 0.34
    # A freestanding opening, not a billboard. Its interior contains actual 3D geometry.
    add_frame_bar("Memory frame | left jamb", (x - w/2, y, z), (0.26, d, h), M["portal"])
    add_frame_bar("Memory frame | right jamb", (x + w/2, y, z), (0.26, d, h), M["portal"])
    add_frame_bar("Memory frame | lintel", (x, y, z + h/2), (w, d, 0.25), M["portal"])
    add_frame_bar("Memory frame | threshold", (x, y, z - h/2), (w, d, 0.25), M["portal"])
    # Light traces mark the border where the captured winter scene begins.
    for sx in (-1, 1):
        cube("Memory boundary | light line", (x + sx * (w/2 - .19), y - .205, z), (.045, .035, h - .55), M["glow"])
    cube("Memory boundary | upper light", (x, y - .205, z + h/2 - .18), (w - .45, .035, .045), M["glow"])
    cube("Memory boundary | lower light", (x, y - .205, z - h/2 + .18), (w - .45, .035, .045), M["glow"])

    # An inner miniature forest: snow lives only inside this spatial memory.
    inner_y = y + 0.42
    cube("Memory interior | snowfield", (x, inner_y, 0.25), (w - .44, 1.7, .32), M["snow"], bevel=.08)
    for i in range(8):
        px = x + random.uniform(-1.95, 1.95)
        py = inner_y + random.uniform(-0.5, .5)
        ph = random.uniform(1.4, 2.7)
        cylinder("Memory interior | tree trunk %02d" % i, (px, py, .36 + ph*.30), .10, ph*.60, M["bark"], vertices=7)
        cone("Memory interior | snow pine lower %02d" % i, (px, py, .36 + ph*.56), ph*.31, .05, ph*.58, M["ice"], vertices=7)
        cone("Memory interior | snow pine crown %02d" % i, (px, py, .36 + ph*.78), ph*.23, .02, ph*.42, M["snow"], vertices=7)
    # A snowy branch floating through the interior, echoing the seasonal scene in ref 1.
    curve_tube("Memory interior | frozen branch", [(x-1.8, inner_y-.1, 2.8), (x-.8, inner_y-.18, 3.3), (x+.2, inner_y-.2, 3.1), (x+1.2, inner_y-.1, 3.65)], [1,.72,.42,.02], M["snow"], .085)
    # A thin spatial volume frame makes the interior read as a place with depth.
    for yy in (y + .2, y + 1.32):
        for xx in (x - w/2 + .21, x + w/2 - .21):
            cylinder("Memory volume | depth post", (xx, yy, z), .045, h-.47, M["timeglow"], vertices=8)


def build_time_block():
    collection("05 | Anomaly B - four-dimensional time block")
    cx, cy = -4.4, 9.1
    # Three rectangular slices hold the same patch of world in different moments.
    for i in range(4):
        zz = 1.55 + i * 1.62
        width = 3.5 - 0.18 * i
        depth = 2.15 - 0.12 * i
        cube("Time block | slice %d base" % i, (cx, cy, zz), (width, depth, .16), M["time"], bevel=.05)
        for sx in (-1, 1):
            cube("Time block | slice %d frame post" % i, (cx + sx*width/2, cy, zz + .67), (.08, .08, 1.35), M["timeglow"], bevel=.02)
        for sz in (zz + .05, zz + 1.34):
            cube("Time block | slice %d frame rail" % i, (cx, cy, sz), (width, .075, .075), M["timeglow"], bevel=.02)
        # A repeated miniature tree changes state from layer to layer.
        tree_x = cx + [-.34, .04, .31, -.12][i]
        tree_h = [1.18, .93, .62, .33][i]
        cylinder("Time block | tree trunk slice %d" % i, (tree_x, cy, zz + .16 + tree_h*.36), .075, tree_h*.72, M["bark"], vertices=7)
        if i < 3:
            cone("Time block | tree crown slice %d" % i, (tree_x, cy, zz + .16 + tree_h*.74), .45 - .08*i, .025, tree_h*.52, M["leaf"] if i < 2 else M["bark2"], vertices=7)
        # A small path-line runs through each frozen time-slice.
        cube("Time block | path trace slice %d" % i, (cx+.63, cy-.18, zz+.12), (1.25, .11, .035), M["scan2"], bevel=.018, rot=(0, 0, .12*i))
    # Vertical edge line connects all slices, like one solid object viewed through time.
    curve_tube("Time block | continuous axis", [(cx+1.95, cy, 1.5), (cx+1.95, cy, 4.2), (cx+1.95, cy, 7.0)], [1,1,1], M["timeglow"], .035)


def build_spatial_scan():
    collection("06 | Anomaly C - spatial scan road")
    # A recognizable road becomes a preserved 3D volume, then fractures into cubes.
    # Its origin is a narrow ground-level ribbon.
    start = (7.0, 11.8)
    for i in range(12):
        t = i / 11
        x = 7.0 + 3.1 * t
        y = 11.8 + 3.2 * t
        z = ground_z(x, y) + .17 + 2.0 * t*t
        size = 1.05 - .28*t
        ob = cube("Spatial scan | road fragment %02d" % i, (x, y, z), (size, .72 - .16*t, .20 + .08*(i%3)), M["scan"] if i%3 else M["scan2"], bevel=.025, rot=(0, .05*i, .08*i))
    # Fragmented scan voxels detach from the continuous street.
    for i in range(72):
        t = random.random()
        x = 7.0 + 3.1*t + random.uniform(-1.0, 1.0)
        y = 11.8 + 3.3*t + random.uniform(-.8, .8)
        z = ground_z(x, y) + .45 + 3.4*t + random.uniform(-.6, .7)
        s = random.uniform(.12, .42)
        ob = cube("Spatial scan | displaced voxel %02d" % i, (x, y, z), (s, s*random.uniform(.7,1.5), s*random.uniform(.7,1.4)), M["scan2"] if i%4==0 else M["scan"], bevel=.015, rot=(random.uniform(-.2,.2), random.uniform(-.2,.2), random.uniform(-.4,.4)))
    # Survey-frame edges suggest a captured spatial volume that has not fully resolved.
    for x in (6.8, 10.2):
        curve_tube("Spatial scan | volume edge", [(x, 11.5, .1), (x, 12.9, .8), (x, 14.5, 2.2), (x, 15.3, 3.4)], [1,1,1,1], M["timeglow"], .026)


def build_sheep():
    collection("07 | The sheep")
    x, y, z = 3.7, 14.8, ground_z(3.7, 14.8)
    # Body silhouette and irregular wool are all modeled in 3D.
    uv("Sheep | body", (x, y, z + 1.05), (1.05, .56, .72), M["sheep"], 16, 10)
    for i in range(11):
        a = 2*math.pi*i/11
        uv("Sheep | wool curl %02d" % i, (x + .72*math.cos(a), y + .40*math.sin(a), z + 1.1 + .39*math.sin(a*2)), (.37,.35,.39), M["wool" if i%3 else "sheep"], 10, 7)
    # Four small legs.
    for lx in (-.62, .58):
        for ly in (-.32, .32):
            cylinder("Sheep | leg", (x+lx, y+ly, z+.40), .09, .78, M["face"], vertices=7)
    # Neck and head face back toward the player's position.
    uv("Sheep | neck", (x-.05, y-.43, z+1.35), (.34,.47,.43), M["sheep"], 12, 8)
    uv("Sheep | head turned toward player", (x-.10, y-.78, z+1.56), (.34,.39,.32), M["face"], 12, 8)
    uv("Sheep | muzzle", (x-.10, y-1.08, z+1.48), (.22,.19,.17), M["wool"], 10, 7)
    for side in (-1, 1):
        uv("Sheep | ear", (x-.10+side*.36, y-.64, z+1.64), (.11,.35,.10), M["face"], 8, 6)
        uv("Sheep | eye", (x-.10+side*.22, y-.91, z+1.65), (.045,.045,.045), M["eye"], 8, 6)


def build_mist_and_lights():
    collection("08 | Fog, lighting and sky")
    world = bpy.data.worlds.new("Fog forest | grey green dawn") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    bg.inputs["Color"].default_value = (0.30, 0.36, 0.34, 1)
    bg.inputs["Strength"].default_value = 0.60
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (.55, .61, .57, 1)
    vol.inputs["Density"].default_value = .007
    vol.inputs["Anisotropy"].default_value = .24
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])

    bpy.ops.object.light_add(type="SUN", location=(0, -2, 16))
    sun = bpy.context.object
    sun.name = "Overcast sun through dense fog"
    sun.data.energy = 1.2
    sun.data.angle = math.radians(24)
    sun.rotation_euler = (math.radians(23), math.radians(-28), math.radians(-24))
    place(sun)
    bpy.ops.object.light_add(type="AREA", location=(1.0, 9.0, 13.0))
    light = bpy.context.object
    light.name = "Pale sky opening behind the tree"
    light.data.energy = 2100
    light.data.shape = "DISK"
    light.data.size = 13
    light.data.color = (.73, .82, .79)
    light.rotation_euler = (math.radians(18), 0, math.radians(160))
    place(light)
    bpy.ops.object.light_add(type="AREA", location=(0.3, 6.3, 3.1))
    portal_light = bpy.context.object
    portal_light.name = "Light bleeding from the memory frame"
    portal_light.data.energy = 340
    portal_light.data.size = 3.5
    portal_light.data.color = (.38, .72, .74)
    portal_light.rotation_euler = (math.radians(72), 0, 0)
    place(portal_light)
    bpy.ops.object.light_add(type="AREA", location=(0.0, -9.0, 10.0))
    fill = bpy.context.object
    fill.name = "Player-side soft fill for readable nearby grass"
    fill.data.energy = 2400
    fill.data.shape = "DISK"
    fill.data.size = 19
    fill.data.color = (.82, .88, .78)
    fill.rotation_euler = (Vector((0.0, 5.0, 1.0)) - fill.location).to_track_quat("-Z", "Y").to_euler()
    place(fill)


def camera(name, loc, target, lens=30):
    data = bpy.data.cameras.new(name + " Lens")
    ob = bpy.data.objects.new(name, data)
    COL.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    data.clip_end = 100
    return ob


def build_reference_and_cameras():
    collection("09 | Cameras and source reference")
    first = camera("Player eye | sharp near-field view", (0.0, -14.6, 1.68), (.15, 5.6, 0.48), lens=27)
    overview = camera("Overview | authored pocket world", (26.0, -27.0, 23.5), (0.0, 3.0, 2.3), lens=37)
    # Keep the exact project image inside the blend file as a non-rendering reference board.
    backdrop = None
    try:
        img = bpy.data.images.load(REFERENCE_IMAGE, check_existing=True)
        img.pack()
        # The project photo can support the far field. Close vegetation, the path, well,
        # memory frame and all three anomalies remain modeled as 3D geometry in front of it.
        bgmat = bpy.data.materials.new("Far field | source forest photo, no generated image")
        bgmat.use_nodes = True
        nodes = bgmat.node_tree.nodes
        links = bgmat.node_tree.links
        nodes.clear()
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Linear"
        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Strength"].default_value = 0.27
        output = nodes.new("ShaderNodeOutputMaterial")
        links.new(tex.outputs["Color"], emission.inputs["Color"])
        links.new(emission.outputs["Emission"], output.inputs["Surface"])
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0.0, 28.0, 5.0), rotation=(math.radians(90), 0, 0))
        backdrop = place(bpy.context.object)
        backdrop.name = "Far field | packed project photo behind the 3D play space"
        backdrop.scale = (32.0, 16.0, 1.0)
        backdrop.data.materials.append(bgmat)
        backdrop["Usage"] = "Far background only; the nearby visible walking region is 3D."
        bpy.ops.object.empty_add(type="IMAGE", location=(28.0, 0.0, 3.0))
        ref = bpy.context.object
        ref.name = "Source image | 仮イメージ１.jpg (packed, non-rendering)"
        ref.data = img
        ref.empty_display_size = 12.0
        ref.hide_render = True
        ref.rotation_euler = (math.radians(90), 0, 0)
        place(ref)
    except Exception as exc:
        print("Could not pack reference photo:", exc)
    return first, overview, backdrop


def look_at_camera(cam, target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()


def render(cam, path, width, height, percent=100):
    scene.camera = cam
    scene.render.filepath = path
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = percent
    bpy.ops.render.render(write_still=True)


build_terrain()
build_grass()
build_forest()
build_memory_frame()
build_time_block()
build_spatial_scan()
build_sheep()
build_mist_and_lights()
player_cam, overview_cam, photo_backdrop = build_reference_and_cameras()

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 24
scene.eevee.use_volumetric_shadows = False
scene.eevee.volumetric_samples = 16
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
scene.render.resolution_percentage = 100
scene.render.resolution_x = 1400
scene.render.resolution_y = 700
scene.render.image_settings.color_depth = "8"
scene.render.filepath = FIRST_RENDER
scene.camera = player_cam
scene.camera.data.lens = 27
scene.camera.data.dof.use_dof = False
scene.render.film_transparent = False

# Metadata in the project file to keep the design intent visible to the next artist.
scene["Project"] = "I'm (NOT) in a Cage."
scene["Prototype scope"] = "Small, entirely 3D fog-forest pocket; the path and immediate player surroundings are fully modeled."
scene["Reference A"] = "A recorded winter moment occupies a walk-in 3D spatial frame inside the fog forest."
scene["Reference B"] = "Past/present/future appear together as four visible spatial slices."
scene["Reference C"] = "A spatially captured road resolves into floating cubes while retaining its route."

# Save the complete authored scene before rendering, so the project remains available even if
# the user's GPU/driver cannot complete a render in background mode.
scene.camera = player_cam
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH, compress=True)

# Render the first-person view, then an overview card; save with the player view active.
if photo_backdrop:
    photo_backdrop.hide_render = False
render(player_cam, FIRST_RENDER, 1400, 700, 72)
if photo_backdrop:
    photo_backdrop.hide_render = True
render(overview_cam, OVERVIEW_RENDER, 1200, 900, 80)
if photo_backdrop:
    photo_backdrop.hide_render = False
scene.camera = player_cam
scene.render.filepath = FIRST_RENDER
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH, compress=True)
print("Saved scene:", BLEND_PATH)
print("Rendered first-person:", FIRST_RENDER)
print("Rendered overview:", OVERVIEW_RENDER)
print("Object count:", len(bpy.data.objects))
