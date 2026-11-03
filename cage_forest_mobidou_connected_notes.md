# Connected Mobidou forest prototype

## Deliverables

- `cage_forest_mobidou_connected.blend` — editable Blender scene with the Mobidou shrine area joined to the original forest route.
- `game/assets/forest.glb` — browser runtime environment exported from the connected scene.
- `game/assets/forest-panorama.png` — distant forest background used by the browser build.
- `game/` — Three.js first-person prototype, its local server, and the vendored runtime modules with their license.

## World layout and runtime

The Mobidou area continues from the far edge of the original forest. The continuous path crosses the boundary; terrain, vegetation, and buildings remain in their separate areas. The browser route extends through the connector and into the Mobidou path.

At load time, `game/main.js` removes runtime objects whose names begin with `Memory frame`, `Memory boundary`, `Memory interior`, `Memory volume`, `Time block`, `Spatial scan`, `Light bleeding from the memory frame`, or `Far field`. Those Blender objects can remain in the editable scene while hidden in the browser build.

## Source and verification

The imported shrine-world model came from [`haru516-web/mobidou-ios-app`, commit `5beeda0`](https://github.com/haru516-web/mobidou-ios-app/commit/5beeda0), file `assets/prayer-first-person/shrine-world-realistic.glb`.

The browser prototype is served with `node game/serve.mjs` at `http://127.0.0.1:8765/`. The GLB loaded in the browser without reported errors. Visual verification was limited to Blender previews and browser loading.
