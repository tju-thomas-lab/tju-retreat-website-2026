"""Face-on Cycles render of the Varian TrueBeam, in layers (Blender 4.x).

Run from this folder, for example:
  LAYER=rot RES=1200 SM=64 OUT=rot.png VIEW=Standard KEY=0.06 ENV=0.55 blender -b -P render_layers.py

Env: LAYER = all | back | rot | front, ANGLE (gantry degrees), RES (pixels), SM (samples), SEED, OUT (required).
The camera looks straight down the gantry axis, so the rotating layer only ever needs to be rotated in 2D."""
import bpy, math, os, mathutils

LAYER = os.environ.get('LAYER', 'all'); ANGLE = float(os.environ.get('ANGLE', '0'))
RES = int(os.environ.get('RES', '640')); SM = int(os.environ.get('SM', '24')); OUT = os.environ['OUT']
FRAME = float(os.environ.get('FRAME', '3.9')); CAMY = float(os.environ.get('CAMY', '-14'))
ZISO = float(os.environ.get('ZISO', '0.995')); YREF = -0.37

bpy.ops.wm.read_factory_settings(use_empty=True)
_HERE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
bpy.ops.import_scene.fbx(filepath=os.path.join(_HERE, 'Varian_truebeam_fbx.FBX'))
N = lambda i: 'Varian_truebeam%02d' % i
BACK = [N(i) for i in (48, 50, 53, 55, 56, 59)]
ROT = [N(i) for i in (49, 51, 52, 54, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 73, 74, 75, 76)]
FRONT = [N(i) for i in range(2, 48)]
KEEP = set(BACK + ROT + FRONT)
for o in list(bpy.data.objects):
    if o.name not in KEEP: bpy.data.objects.remove(o, do_unlink=True)
show = {'all': KEEP, 'back': set(BACK), 'rot': set(ROT), 'front': set(FRONT)}[LAYER]
for o in bpy.data.objects: o.hide_render = o.name not in show

# ---------- materials: the model's own palette (white, taupe, black gloss, aluminium) ----------
def mat(name, color, rough, metal=0.0, coat=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal; p.inputs['Coat Weight'].default_value = coat; p.inputs['Coat Roughness'].default_value = 0.1
    p.inputs['Specular IOR Level'].default_value = spec
    return m
NEW = {
    'white': mat('white', (0.93, 0.93, 0.92), 0.34, 0, 0.35),
    'taupe': mat('taupe', (0.333, 0.325, 0.298), 0.42, 0, 0.2),
    'grey': mat('grey', (0.42, 0.43, 0.43), 0.45, 0, 0.1),
    'black': mat('black', (0.015, 0.016, 0.018), 0.16, 0, 0.5),
    'red': mat('red', (0.39, 0.02, 0.02), 0.35, 0, 0.3),
    'yellow': mat('yellow', (0.96, 0.97, 0.67), 0.4),
    'alu': mat('alu', (0.78, 0.79, 0.80), 0.24, 1.0),
}
MAP = {'varian  plastic white': 'white', 'varian  plastic white2': 'white', 'PVC white': 'white', 'varian  plastic silver': 'taupe',
       'varian  plastic grey': 'grey', 'varian  plastic black': 'black', 'varian  plastic black gloss': 'black',
       'varian  plastic red': 'red', 'varian  plastic yellow': 'yellow', 'Clean Aluminium Polished': 'alu'}
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    for i, slot in enumerate(o.material_slots):
        k = MAP.get(slot.material.name if slot.material else '')
        if k: slot.material = NEW[k]
        elif slot.material:                                   # buttons + lens keep their real textures; drop the dead normal maps
            nt = slot.material.node_tree
            for n in list(nt.nodes):
                if n.bl_idname == 'ShaderNodeNormalMap': nt.nodes.remove(n)

# ---------- rotate the gantry about the axis (x=0, z=ZISO, along y); camera looks along +y, +angle = clockwise ----------
piv = bpy.data.objects.new('pivot', None); bpy.context.scene.collection.objects.link(piv); piv.location = (0, YREF, ZISO)
bpy.context.view_layer.update()
for n in ROT:
    o = bpy.data.objects.get(n)
    if o: o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
piv.rotation_euler = (0, math.radians(ANGLE), 0); bpy.context.view_layer.update()

# ---------- scene ----------
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SM; sc.cycles.use_denoising = False
sc.cycles.seed = int(os.environ.get('SEED', '0')); sc.cycles.use_animated_seed = False; sc.cycles.max_bounces = 6
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = RES
sc.view_settings.view_transform = os.environ.get('VIEW', 'Filmic'); sc.view_settings.exposure = float(os.environ.get('EXPOSURE', '0'))
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.filepath = OUT

w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.86, 0.88, 0.92, 1); bg.inputs['Strength'].default_value = float(os.environ.get('ENV', '0.5'))
def area(name, loc, size, energy, color, target):
    l = bpy.data.lights.new(name, 'AREA'); l.shape = 'DISK'; l.size = size; l.energy = energy; l.color = color
    ob = bpy.data.objects.new(name, l); sc.collection.objects.link(ob); ob.location = loc
    t = bpy.data.objects.new(name + 't', None); sc.collection.objects.link(t); t.location = target
    c = ob.constraints.new('TRACK_TO'); c.target = t; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
K = float(os.environ.get('KEY', '1.0')); tgt = (0, YREF, ZISO)
area('front', (0, CAMY + 1.5, ZISO + 0.6), 8.0, 7000 * K, (1.0, 0.98, 0.95), tgt)      # frontal softbox: near rotation-symmetric shading
area('top', (-0.9, -1.0, 5.0), 3.5, 900 * K, (1.0, 0.94, 0.86), tgt)

cam = bpy.data.cameras.new('cam'); cam.sensor_width = 36
cam.lens = (YREF - CAMY) * 36 / FRAME
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
co.location = (0, CAMY, ZISO); co.rotation_euler = (math.radians(90), 0, 0); cam.clip_start = 0.1; cam.clip_end = 80
import time; t0 = time.time(); bpy.ops.render.render(write_still=True); print('RENDER SECONDS', round(time.time() - t0, 1))
