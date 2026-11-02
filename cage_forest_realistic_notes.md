# I'm (NOT) in a Cage. — realistic environment pass

## Deliverables

- `cage_forest_realistic.blend` — editable Blender scene. Opens with the first-person camera, 720×1280 framing, Cycles, denoising, and 32 samples. All used images are packed into the Blend file.
- `cage_forest_realistic_firstperson.png` — denoised 720×1280 player-eye render.
- `cage_forest_realistic_overview.png` — brighter 800×600 overview of the pocket world.
- `refine_cage_forest_realistic.py`, `polish_cage_forest_realistic.py`, `finish_cage_forest_realistic.py` — scene construction and refinement scripts.
- `assets/polyhaven_cc0/` — locally copied source files and asset metadata for the CC0 materials and model.

The earlier `cage_forest_prototype.blend` remains as the original blockout. The realistic pass is saved separately.

## What is 3D

The player-scale path, terrain, stepping stones, pit and broken rim, moss rocks, ferns, curved grass blades, tree trunks and branches, memory frame, time slices, and spatial-scan fragments are modeled geometry. The supplied `仮イメージ１.jpg` is packed into the scene as a distant forest background only. No new generated image was used.

Natural surface detail comes from PBR color, roughness and normal maps, photo-based bark and pine sprig textures, and a forest HDRI. The scene keeps the original uncanny locations and first-person route.

## Asset sources and licenses

All assets listed as used here are from Poly Haven and licensed CC0 1.0. The full downloaded file lists and source metadata are retained under `assets/polyhaven_cc0/`.

| Asset | Author / creator | Use in this scene | Source |
|---|---|---|---|
| Forest Floor | eye-candy.xyz | Textured soil and leaf litter | https://polyhaven.com/a/forest_floor |
| Forest Slope | Andreas Mischok | Environment lighting and reflections | https://polyhaven.com/a/forest_slope |
| Pine Tree 01 image maps | Rob Tuytel (photography), Rico Cilliers (original model) | Tree bark and photographed branch cards; the high-density source tree mesh is not used | https://polyhaven.com/a/pine_tree_01 |
| Rock Moss Set 01 | Kless Gyzen | Realistic mossy rock meshes around the pit and route | https://polyhaven.com/a/rock_moss_set_01 |
| Stone Tiles 02 | Charlotte Baglioni | Path, stepping stones and exposed pit rock | https://polyhaven.com/a/stone_tiles_02 |

The copied `wood_planks_dirt` set is not assigned to this scene. Poly Haven's license is at https://polyhaven.com/license; CC0 1.0 is at https://creativecommons.org/publicdomain/zero/1.0/.

## Render notes

The first-person PNG was rendered on the available CPU with 6 Cycles samples and denoising. The editable scene is set to 32 samples for future renders. The overview uses a separate exposure adjustment so the full layout reads in one image. Neither preview claims to be a final game capture; player controls and world simulation are not part of this Blender file.
