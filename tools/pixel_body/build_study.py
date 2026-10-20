"""Stage 2 ONLY: independent, palette-first pixel character silhouette study.

Hand-authored profile/edge-loop construction in Blender; no primitive kitbash,
no old geometry, no skeleton/animation, and no production Godot modifications.
Refuses to overwrite an existing version. Use a new --version for revisions.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--version', default='v3')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
assert args.version.replace('_', '').isalnum(), 'Invalid version'
BASE = ROOT / 'assets/characters' / ('pixel_adventurer_' + args.version)
OUT = ROOT / 'docs/pixel_body_study' / args.version
assert not BASE.exists(), 'Existing study preserved. Choose another --version.'
BASE.mkdir(parents=True)
(BASE / 'source/blender').mkdir(parents=True)
(BASE / '.gdignore').touch()  # Isolated until silhouette approval.
OUT.mkdir(parents=True, exist_ok=False)
(OUT / '.gdignore').touch()

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
model = bpy.data.collections.new('PIXEL_BODY_STAGE_2')
scene.collection.children.link(model)
studio = bpy.data.collections.new('REVIEW_STUDIO_EXCLUDED_FROM_GLB')
scene.collection.children.link(studio)

# Restrained large color regions; no baked shading or surface micro-noise.
COLORS = {
    'skin': '#c79a75', 'skin_shadow': '#a97654', 'hair': '#493023',
    'hair_light': '#60402b', 'hair_dark': '#32251e', 'linen': '#d6c4a1',
    'linen_shadow': '#b5a280', 'scarf': '#813e30', 'scarf_shadow': '#622c25',
    'trousers': '#343334', 'leather': '#53392c', 'leather_light': '#745038',
    'sole': '#2d2420', 'buckle': '#a87a3a', 'face_mark': '#44332b',
}
MATS = {}
def srgb(v):
    v = int(v, 16) / 255
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
for name, color in COLORS.items():
    rgb = tuple(srgb(color[i:i + 2]) for i in (1, 3, 5))
    mat = bpy.data.materials.new('Pixel_' + name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Roughness'].default_value = .88
    MATS[name] = mat

def mesh(name, vs, fs, material, smooth=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vs, [], fs)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    ob = bpy.data.objects.new(name, data)
    model.objects.link(ob)
    data.materials.append(MATS[material])
    for f in data.polygons:
        f.use_smooth = smooth
    ob['stage'] = '2: silhouette/color block study; not rigged or art-approved'
    return ob

def profile_mesh(name, rows, n, material, deform=None, cap=True, smooth=True):
    """Explicit authored rings; rows=(x,y,z,width,depth), no subdivisions."""
    vs, fs = [], []
    for j, (x, y, z, rx, ry) in enumerate(rows):
        for i in range(n):
            a = i / n * math.tau
            p = Vector((x + rx * math.sin(a), y + ry * math.cos(a), z))
            if deform:
                p = Vector(deform(p, a, j))
            vs.append(p)
            if j:
                q = j * n + i
                ni = j * n + (i + 1) % n
                fs.append((q - n, ni - n, ni, q))
    if cap:
        fs += [tuple(reversed(range(n))), tuple((len(rows) - 1) * n + i for i in range(n))]
    return mesh(name, vs, fs, material, smooth)

# One connected neck/head surface, restrained nose/jaw, complete cranium.
# Anatomical crown 1.775m; hair envelope 1.85m; chin 1.535m (~7.4 heads).
HEAD = [
    (0, -.013, 1.445, .064, .054), (0, -.010, 1.49, .053, .048),
    (0, .008, 1.535, .043, .052), (0, .006, 1.56, .067, .065),
    (0, -.003, 1.595, .083, .073), (0, -.008, 1.625, .094, .079),
    (0, -.009, 1.653, .096, .085), (0, -.010, 1.681, .096, .084),
    (0, -.012, 1.715, .091, .080), (0, -.016, 1.750, .070, .064),
    (0, -.019, 1.772, .035, .033), (0, -.019, 1.778, .008, .008),
]
def face_deform(p, a, j):
    front = max(0, math.cos(a))
    if j == 5: p.y += .016 * front ** 26  # restrained nose, not a pointed profile
    if j == 6: p.y -= .004 * front ** 6  # broad socket plane
    if j == 3: p.y += .005 * front ** 10
    return p
head = profile_mesh('HeadNeck_continuous', HEAD, 20, 'skin', face_deform)

# Ears are small faceted anatomical wedges, not spheres.
for s in (-1, 1):
    mesh('Ear_' + str(s), [(s*.091,-.009,1.65),(s*.108,-.005,1.655),
         (s*.111,.012,1.634),(s*.103,.012,1.608),(s*.091,-.004,1.615),
         (s*.098,.018,1.633)], [(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5),(4,3,2,1,0)], 'skin')

# Tiny flat marks only; no eyespheres/lashes/iris detail competing at sprite size.
for s in (-1, 1):
    x = s * .035
    mesh('EyeMark_' + str(s), [(x-.014,.076,1.659),(x+.014,.076,1.659),
         (x+.012,.077,1.652),(x-.012,.077,1.652)], [(0,1,2,3)], 'face_mark', False)
    mesh('Brow_' + str(s), [(s*.020,.077,1.675),(s*.052,.067,1.674),
         (s*.052,.067,1.670),(s*.020,.077,1.671)], [(0,1,2,3)], 'hair', False)
mesh('MouthMark', [(-.016,.074,1.575),(.016,.074,1.575),(.011,.075,1.572),(-.011,.075,1.572)], [(0,1,2,3)], 'skin_shadow', False)

# Continuous tailored shirt: neckline, shoulders and sleeves share vertices.
# Broad curves are authored, rather than adding many separate small folds.
shirt_rows = [(.84,.191,.112),(.93,.187,.117),(1.015,.171,.109),
              (1.078,.151,.096),(1.15,.164,.101),(1.245,.183,.107),
              (1.325,.202,.105),(1.405,.217,.093),(1.455,.181,.073),
              (1.485,.115,.059),(1.500,.063,.050)]
n = 24
vs, fs = [], []
for j, (z, rx, ry) in enumerate(shirt_rows):
    for i in range(n):
        a = i/n*math.tau
        x = rx*math.sin(a)
        y = ry*math.cos(a)
        # Slight front/back split in silhouette, not a dense pleat pattern.
        zz = z + (.035 * abs(math.cos(a)) ** 18 if j == 0 else 0)
        zz -= .010 * abs(math.sin(a)) if j >= 7 else 0
        vs.append((x,y,zz))
holes = [(4,8,6,9,1),(16,20,6,9,-1)]
def idx(i,j): return j*n + i % n
for j in range(len(shirt_rows)-1):
    for i in range(n):
        if any(a<=i<b and c<=j<d for a,b,c,d,s in holes): continue
        fs.append((idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)))
for a,b,c,d,s in holes:
    loop = ([idx(i,c) for i in range(a,b)]+[idx(b,j) for j in range(c,d)]
            +[idx(i,d) for i in range(b,a,-1)]+[idx(a,j) for j in range(d,c,-1)])
    center = sum((Vector(vs[i]) for i in loop),Vector())/len(loop)
    angles = [math.atan2(vs[i][1]/.10,(vs[i][2]-center.z)/.09) for i in loop]
    paths = [(s*.224,.002,1.403,.055,.067),(s*.244,.006,1.34,.059,.064),
             (s*.265,.016,1.263,.059,.062),(s*.274,.023,1.203,.055,.057),
             (s*.278,.027,1.174,.055,.056)]
    previous = loop
    for j,(x,y,z,rx,ry) in enumerate(paths):
        ring=[]
        for k,angle in enumerate(angles):
            p=Vector((x+s*rx*math.cos(angle),y+ry*math.sin(angle),z-.30*rx*math.cos(angle)))
            if j==0:p=Vector(vs[loop[k]]).lerp(p,.65)
            ring.append(len(vs));vs.append(p)
        fs += [(previous[k],previous[(k+1)%len(ring)],ring[(k+1)%len(ring)],ring[k]) for k in range(len(ring))]
        previous=ring
    # Rolled cuff is a broad integral change in sleeve contour.
    inner=[]
    for q in previous:
        p=Vector(vs[q]);p.x=x+(p.x-x)*.80;p.y=y+(p.y-y)*.80;p.z+=.012
        inner.append(len(vs));vs.append(p)
    fs += [(previous[k],previous[(k+1)%len(inner)],inner[(k+1)%len(inner)],inner[k]) for k in range(len(inner))]
used=sorted({i for f in fs for i in f});remap={i:j for j,i in enumerate(used)}
shirt=mesh('Tunic_shoulders_sleeves_CONTINUOUS',[vs[i] for i in used],
           [tuple(remap[i] for i in f) for f in fs],'linen')
shirt['topology_note']='Shared shoulder/armhole vertices. Neck, hem and cuffs are intentional garment boundaries.'

# Connected trouser seat/crotch and both legs. Knees carry 3 deformation loops.
vs,fs=[],[]
n=24
for j,(z,rx,ry) in enumerate([(1.085,.133,.082),(1.005,.160,.099),(.925,.175,.105),(.855,.175,.104)]):
    for i in range(n):
        a=i/n*math.tau;vs.append((rx*math.sin(a),ry*math.cos(a),z))
        if j:fs.append(((j-1)*n+i,(j-1)*n+(i+1)%n,j*n+(i+1)%n,j*n+i))
bridge=[]
for j in range(1,6):
    t=j/6;bridge.append(len(vs));vs.append((0,-.104+t*.208,.855+.012*math.sin(t*math.pi)))
end=3*n
for s in (1,-1):
    previous=([end+i for i in range(13)]+bridge if s==1 else [end+i for i in range(12,24)]+[end]+list(reversed(bridge)))
    angles=[math.atan2((vs[q][0]-s*.094)/.088,vs[q][1]/.104) for q in previous]
    for j,(x,y,z,rx,ry) in enumerate([(s*.098,0,.80,.083,.097),(s*.108,.010,.69,.083,.085),
            (s*.120,.024,.565,.070,.073),(s*.125,.028,.52,.063,.066),
            (s*.129,.022,.475,.068,.072),(s*.131,.012,.412,.076,.073),
            (s*.130,.004,.366,.059,.058),(s*.130,0,.30,.047,.052)]):
        ring=[]
        for k,a in enumerate(angles):
            p=Vector((x+rx*math.sin(a),y+ry*math.cos(a),z))
            if j==0:p=Vector(vs[previous[k]]).lerp(p,.83)
            ring.append(len(vs));vs.append(p)
        fs += [(previous[k],previous[(k+1)%len(ring)],ring[(k+1)%len(ring)],ring[k]) for k in range(len(ring))]
        previous=ring
pants=mesh('Trousers_seat_crotch_legs_CONTINUOUS',vs,fs,'trousers')

# Bare forearm into a simple relaxed hand with a sewn-in thumb root.
# Fingers remain a readable mitten block at this stage, not final hand topology.
for s in (-1,1):
    rows=[(s*.269,.023,1.225,.037,.037),(s*.282,.028,1.18,.039,.039),
          (s*.293,.031,1.14,.043,.041),
          (s*.309,.046,1.055,.039,.038),(s*.326,.057,.97,.029,.029),
          (s*.331,.063,.935,.028,.024),(s*.339,.073,.902,.040,.022),
          (s*.344,.083,.855,.037,.021),(s*.346,.091,.825,.030,.019),
          (s*.347,.092,.811,.022,.012)]
    arm=profile_mesh('Forearm_hand_'+str(s),rows,12,'skin')
    # Explicit lateral thumb-shaped extrusion, connected to palm face.
    bm=bmesh.new();bm.from_mesh(arm.data);bm.faces.ensure_lookup_table()
    face=min(bm.faces,key=lambda f:(f.calc_center_median()-Vector((s*.309,.073,.900))).length)
    result=bmesh.ops.extrude_face_region(bm,geom=[face])
    verts=[v for v in result['geom'] if isinstance(v,bmesh.types.BMVert)]
    center=sum((v.co for v in verts),Vector())/len(verts)
    for v in verts:v.co=center+(v.co-center)*.66+Vector((-s*.020,.013,-.021))
    bmesh.ops.delete(bm,geom=[face],context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(arm.data);bm.free()
    profile_mesh('Wrist_wrap_blockout_'+str(s),[(s*.326,.057,.966,.032,.032),
         (s*.332,.062,.929,.032,.029)],12,'leather',cap=False)

# Boots are sculpted profiles, integrated calf/instep/toe rather than cylinders.
for s in (-1,1):
    def boot_deform(p,a,j,s=s):
        # Natural slight toe-out without rotating legs or a skeleton.
        x,y=p.x-s*.13,p.y
        angle=-s*.065
        p.x=s*.13+x*math.cos(angle)-y*math.sin(angle)
        p.y=x*math.sin(angle)+y*math.cos(angle)
        return p
    boot=profile_mesh('Boot_main_'+str(s),[(s*.13,.042,.035,.060,.119),
        (s*.13,.047,.061,.064,.123),(s*.13,.050,.085,.062,.118),
        (s*.13,.025,.121,.053,.081),(s*.13,-.005,.17,.047,.052),
        (s*.13,-.011,.255,.048,.055),(s*.13,-.002,.326,.060,.061),
        (s*.13,-.002,.355,.062,.063),(s*.13,-.002,.365,.055,.055)],
        16,'leather',boot_deform)
    profile_mesh('Boot_sole_'+str(s),[(s*.13,.043,.014,.062,.121),(s*.13,.044,.034,.062,.121)],16,'sole',boot_deform)
    # Clear broad folded rim; no laces or micro-buckles until stage 3.
    profile_mesh('Boot_cuff_blockout_'+str(s),[(s*.13,-.002,.327,.062,.064),
        (s*.13,-.002,.368,.067,.066),(s*.13,-.002,.379,.063,.063)],16,'leather_light',boot_deform,cap=False)

# Main hair cap has an uneven 20-sided silhouette. Broad authored clumps only.
def hair_shape(p,a,j):
    p.x += .006*math.sin(5*a+.8*j)
    p.y += .005*math.sin(3*a+.6*j)
    if j==0:p.z += .066*max(0,math.cos(a))**2+.008*math.sin(5*a)
    return p
hair=profile_mesh('Hair_main_mass',[(0,-.018,1.625,.105,.091),
    (0,-.018,1.70,.132,.112),(0,-.014,1.762,.141,.115),
    (0,-.023,1.803,.121,.102),(0,-.027,1.826,.078,.069),
    (0,-.027,1.833,.009,.011)],20,'hair',hair_shape,smooth=True)

def clump(name,points,widths,depths,material):
    vs,fs=[],[]
    for j,point in enumerate(points):
        p=Vector(point)
        tangent=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])).normalized()
        side=tangent.cross(Vector((0,1,0))).normalized()
        if side.length<.1:side=Vector((1,0,0))
        normal=side.cross(tangent).normalized()
        for k in range(6):
            a=k/6*math.tau
            vs.append(p+side*(math.cos(a)*widths[j])+normal*(math.sin(a)*depths[j]))
            if j:
                q=j*6+k;ni=j*6+(k+1)%6;fs.append((q-6,ni-6,ni,q))
    fs += [tuple(reversed(range(6))),tuple((len(points)-1)*6+i for i in range(6))]
    return mesh(name,vs,fs,material,True)
# Five broad, bent fringe blocks: round volume, asymmetric descending tips.
for i,(points,widths) in enumerate([
    ([(-.089,.022,1.795),(-.096,.075,1.766),(-.111,.100,1.719),(-.100,.111,1.690)],[.031,.038,.025,.003]),
    ([(-.051,.035,1.810),(-.052,.089,1.780),(-.047,.118,1.733),(-.026,.116,1.705)],[.035,.039,.027,.003]),
    ([(.001,.044,1.814),(.012,.102,1.778),(.039,.119,1.723),(.046,.106,1.696)],[.037,.039,.026,.003]),
    ([(.057,.028,1.808),(.086,.082,1.773),(.101,.106,1.735),(.081,.114,1.711)],[.033,.037,.027,.003]),
    ([(.092,-.003,1.785),(.124,.046,1.753),(.128,.075,1.711),(.114,.076,1.681)],[.028,.033,.023,.003]),
]):clump('Hair_fringe_'+str(i),points,widths,[.023,.025,.016,.002],'hair_light' if i in (0,3) else 'hair')
for s in (-1,1):
    clump('Hair_temple_'+str(s),[(s*.104,.038,1.765),(s*.136,.04,1.704),(s*.112,.043,1.632)],
          [.035,.028,.002],[.027,.023,.002],'hair_dark')
    clump('Hair_side_sweep_'+str(s),[(s*.077,-.04,1.807),(s*.144,-.03,1.766),(s*.158,.005,1.724)],
          [.042,.031,.002],[.028,.023,.002],'hair')
    clump('Hair_back_flip_'+str(s),[(s*.065,-.077,1.793),(s*.119,-.11,1.746),(s*.142,-.114,1.702)],
          [.040,.028,.002],[.024,.022,.002],'hair_dark')
clump('Hair_crown_sweep',[(.046,-.056,1.801),(.014,-.038,1.835),(-.038,-.012,1.840),(-.085,.018,1.810)],
      [.038,.041,.026,.003],[.024,.025,.018,.002],'hair_light')

# Identification blockouts only: scarf main fold/tail, belt/pouch large forms.
def scarf_deform(p,a,j):
    p.z-=.019*max(0,math.cos(a))+.009*math.sin(a)
    return p
profile_mesh('Scarf_wrap_BLOCKOUT',[(0,-.004,1.463,.10,.085),
    (0,-.004,1.49,.108,.09),(0,-.004,1.522,.086,.074),
    (0,-.004,1.545,.066,.06)],18,'scarf',scarf_deform)
mesh('Scarf_tail_BLOCKOUT',[(-.080,.060,1.49),(-.039,.085,1.48),(-.091,.12,1.355),
    (-.127,.105,1.325),(-.110,.083,1.436),(-.080,.048,1.49),(-.039,.073,1.48),
    (-.091,.108,1.355),(-.127,.093,1.325),(-.110,.071,1.436)],
    [(0,1,2,3,4),(9,8,7,6,5),(0,5,6,1),(1,6,7,2),(2,7,8,3),(3,8,9,4),(4,9,5,0)],'scarf_shadow')
profile_mesh('Belt_BLOCKOUT',[(0,0,1.060,.155,.101),(0,0,1.105,.157,.102)],24,'leather',cap=False)
# Curved trapezoidal leather pouch at character's left hip, not a cube primitive.
profile_mesh('Pouch_BLOCKOUT',[(.178,.058,.910,.042,.029),(.183,.062,.923,.053,.035),
    (.180,.057,1.005,.057,.035),(.171,.049,1.037,.051,.031)],10,'leather_light')

# Purpose groups reserve future visibility/rig regions without adding a rig now.
for ob in model.objects:
    ob['future_role'] = ('head' if ob.name.startswith(('Head','Ear','Eye','Brow','Mouth','Hair')) else
        'torso_cloth' if ob==shirt else 'legs_cloth' if ob==pants else
        'feet' if ob.name.startswith('Boot') else 'arms_hands' if ob.name.startswith(('Forearm','Wrist')) else 'accessory')

def point(ob, target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,pos,energy,size,color in [
    ('Key',(-3,4,5),480,4,(1,.90,.79)),
    ('Fill',(3,2,2.7),220,3,(.76,.85,1)),
    ('Rim',(1,-3,4),380,3,(1,.82,.64)),
]:
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=pos;point(ob,(0,0,1))
world=bpy.data.worlds.new('NeutralReview');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.19,.21,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.40
scene.world=world
for name,pos in [('front',(0,5,.93)),('side',(-5,0,.93)),('threequarter',(2.5,4.33,1.03))]:
    data=bpy.data.cameras.new('Review_'+name);data.type='ORTHO';data.ortho_scale=2.03
    ob=bpy.data.objects.new('Review_'+name,data);studio.objects.link(ob);ob.location=pos
    point(ob,(0,0,.93))
    if name=='threequarter':scene.camera=ob
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [x.identifier for x in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items] else 'None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene['scope']='Stage 2 silhouette only. No rig, actions, equipment, textures or Godot integration.'
scene['reference']='User supplied adventurer_concept.png; not our concept art, not a game texture.'
scene['review_status']='Awaiting user silhouette review; later stages not started.'

# Reference is a viewport-only image empty, excluded from all renders and GLB.
reference=ROOT/'assets/characters/wayfarer/source/reference/adventurer_concept.png'
ref_collection=bpy.data.collections.new('USER_REFERENCE_NOT_EXPORTED');scene.collection.children.link(ref_collection)
ref_collection.hide_render=True
ref=bpy.data.objects.new('User_reference_only',None);ref_collection.objects.link(ref)
ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(reference));ref.data.pack()
ref.empty_display_size=3;ref.location=(-2,0,1);ref.rotation_euler=(math.pi/2,0,0)
ref.hide_set(True)

bpy.ops.object.select_all(action='DESELECT')
for ob in model.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=shirt
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.region_3d.view_location=(0,0,.95)
            area.spaces.active.region_3d.view_distance=3.2
            area.spaces.active.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
blend=BASE/'source/blender/adventurer_blockout.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(BASE/'adventurer_blockout.glb'),export_format='GLB',
    use_selection=True,export_animations=False,export_cameras=False,export_lights=False,
    export_yup=True,export_materials='EXPORT',export_apply=False)

report={'version':args.version,'stage':2,'status':'silhouette candidate, not approved',
    'blender':bpy.app.version_string,'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
    'armatures':0,'actions':0,'textures':0,'palette_srgb':COLORS,
    'mesh_objects':len(model.objects),'vertices':sum(len(o.data.vertices) for o in model.objects),
    'triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in model.objects),
    'landmarks_m':{'hair_top_approx':1.86,'chin':1.535,'shoulder':1.43,'belt':1.083,'hem':.84,'knee':.52,'boot_top':.379},
    'intentional_limits':['No final UVs/textures','Hands are silhouette blocks','Hair overlap at clump roots',
        'Accessories are blockout; stage 3 pending','No binding or motion deformation claims'],
    'objects':{o.name:{'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'future_role':o['future_role']} for o in model.objects}}
(BASE/'source/build_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('BUILT_PIXEL_BODY',json.dumps({k:report[k] for k in ['version','mesh_objects','vertices','triangles']}),flush=True)
for view in ['front','side','threequarter']:
    scene.camera=bpy.data.objects['Review_'+view]
    for label,w,h in [('native',640,800),('pixel128',104,128),('pixel96',78,96),('pixel64',52,64)]:
        scene.render.resolution_x=w;scene.render.resolution_y=h
        scene.render.filepath=str(OUT/f'{view}_{label}.png')
        bpy.ops.render.render(write_still=True)
        print('RENDER_PIXEL_BODY',view,label,flush=True)
print('PASS PIXEL BODY STAGE 2 BUILD AND 12 REAL RENDERS',flush=True)
