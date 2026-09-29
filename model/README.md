# TrueBeam model

Source for the machine shown on the site. **The website does not load anything from this folder.** `index.html` already
contains the finished renders, so this folder is only here so the renders can be redone or changed later.

| File | What it is |
| --- | --- |
| `Varian_truebeam_fbx.FBX` | The model (FBX). Its two textures, `buttons.jpg` and `lens.jpg`, must stay beside it. |
| `Varian_truebeam_2013.max` | The same model as a 3ds Max scene. |
| `preview.jpg` | The model's preview image. |
| `render_layers.py` | The Blender scene used for the site (Blender 4.x, Cycles). |

## How the three layers on the site were made

The camera looks straight down the gantry's rotation axis, so turning the gantry is a pure 2D rotation of its image.
That is why the site can spin one picture instead of rendering every angle. The model is split into three layers:

- **back**: the fixed stand behind the machine
- **rot**: everything that turns with the gantry (the arm, the head and both imaging arms)
- **front**: the couch and its base

Render one layer (run from this folder):

```
LAYER=rot RES=1200 SM=64 OUT=rot.png VIEW=Standard KEY=0.06 ENV=0.55 blender -b -P render_layers.py
```

The site's layers were rendered at 1200 px with two 64-sample passes per layer, averaged, lightly denoised, given a soft
baked ambient shadow, and saved as WebP with transparency into `src/`. Those last steps (averaging, denoising, shadow,
export) were done separately and are not scripted here. The rotation axis is x = 0, z = 0.995 m.
