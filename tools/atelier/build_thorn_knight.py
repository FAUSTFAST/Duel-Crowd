"""Thorn Warden art candidate, Blender 4.5 LTS. New assets only.

Authored surface patches / explicit UV seams, not a primitive assembly.
Retains the project's original humanoid rig and five in-place clips as a
reusable animation library; NO old mesh is loaded. Source remains editable.
Run: Blender -b --factory-startup --python tools/atelier/build_thorn_knight.py
Use -- --replace-generated only after saving any manual edits in Git.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'assets/characters/thorn_knight'
DEST = BASE / 'thorn_knight.glb'
if DEST.exists() and '--replace-generated' not in sys.argv:
    raise RuntimeError('Generated model exists. Save manual edits before --replace-generated.')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(ROOT/'assets/characters/ashen_knight/source/blender/ashen_knight.blend')) as (src, dst):
    dst.objects = [n for n in src.objects if n == 'OathRig']
    dst.actions = [n for n in src.actions if n in ['idle','walk','run','turn_left','turn_right']]
rig = dst.objects[0]
assert rig and rig.type == 'ARMATURE'
rig.name = 'ThornHumanoid'
bpy.context.collection.objects.link(rig)
for act in dst.actions: act.use_fake_user = True
rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.rotation_quaternion = (1,0,0,0); pb.location = (0,0,0); pb.scale = (1,1,1)
bpy.context.view_layer.update()

image = bpy.data.images.load(str(BASE/'textures/equipment_albedo.png'))
MATS = {}
for kind, metal, rough in [('steel',.48,.72),('brass',.48,.75),('cloth',0,.95),('leather',0,.91),('mail',.32,.86)]:
    mat = bpy.data.materials.new('Thorn_'+kind); mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value = metal; bs.inputs['Roughness'].default_value = rough
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image = image; tex.interpolation = 'Closest'
    mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    if kind == 'cloth': mat.use_backface_culling = False
    MATS[kind] = mat

# Atlas row/column correspond to equipment surfaces; shared trim / mirrored
# limbs intentionally reuse UVs. Dedicated chest, back, helm, shield and cape.
TILES = {'chest':(0,0),'back':(0,1),'helm':(0,2),'shoulder':(0,3),
         'leg':(1,0),'arm':(1,1),'shield':(1,2),'brass':(1,3),
         'cape':(2,0),'tunic':(2,1),'leather':(2,2),'mail':(2,3),
         'boot':(3,0),'blade':(3,1),'plain':(3,2),'bluecloth':(3,3)}
objects = []; parts = []
def atlas(tile,u,v):
    row,col = TILES[tile]
    # Inset 6/1024 across each tile prevents touching adjacent regions.
    return ((col+.025+.95*u)/4,(3-row+.025+.95*v)/4)

def mesh(name,vs,fs,uv,tile,kind,binding,solid=0,bevel=0,smooth=True):
    data = bpy.data.meshes.new(name); data.from_pydata(vs,[],fs); data.update()
    ob = bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob)
    data.materials.append(MATS[kind]); ob.parent = rig
    layer = data.uv_layers.new(name='EquipmentUV')
    for loop in data.loops: layer.data[loop.index].uv = atlas(tile,*uv[loop.vertex_index])
    for p in data.polygons: p.use_smooth = smooth
    for i,p in enumerate(vs):
        weights = binding(p) if callable(binding) else {binding:1}
        for bn,w in weights.items():
            if w > .00001:
                group = ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
                group.add([i],w,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    if solid:
        mod=ob.modifiers.new('ForgedThickness','SOLIDIFY');mod.thickness=solid
        mod.offset=-1; bpy.ops.object.modifier_apply(modifier=mod.name)
    if bevel:
        mod=ob.modifiers.new('RolledCutEdges','BEVEL');mod.width=bevel;mod.segments=3
        mod.limit_method='ANGLE';mod.angle_limit=.6;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Fix normals before skinning, including back-facing patches and thickness.
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
    mod=ob.modifiers.new('Skin','ARMATURE');mod.object=rig
    objects.append(ob)
    parts.append({'name':name,'uv_region':tile,'material':kind,'source_vertices':len(vs)})
    return ob

def patch(name,fn,nu,nv,tile,kind,binding,solid=0,bevel=0):
    vs=[];uv=[];fs=[]
    for j in range(nv+1):
        for i in range(nu+1):
            u=i/nu;v=j/nv;vs.append(fn(u,v));uv.append((u,v))
            if i and j:
                n=j*(nu+1)+i;fs.append((n-nu-2,n-nu-1,n,n-1))
    return mesh(name,vs,fs,uv,tile,kind,binding,solid,bevel)

def interpolate(points,t):
    # Smooth Catmull-Rom sculpting profile. Each silhouette is authored below.
    x=t*(len(points)-1);i=min(len(points)-2,int(x));f=x-i
    p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[i+1]);p3=Vector(points[min(len(points)-1,i+2)])
    return .5*((2*p1)+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f*f*f)

def sleeve(name,profile,tile,kind,bn,segments=20,rings=12):
    # Seam on inward/back-facing side; elliptical but hand-shaped profiles.
    def fn(u,v):
        x,y,z,rx,ry=interpolate(profile,v);a=u*math.tau
        return (x+rx*math.sin(a),y+ry*math.cos(a),z)
    return patch(name,fn,segments,rings,tile,kind,bn,solid=.004)

def trim(name,points,width,bn,kind='brass',tile='brass'):
    vs=[];uv=[];fs=[]
    for i,p in enumerate(points):
        p=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        n=t.cross(Vector((0,1,0))).normalized()*width/2
        vs.extend([p-n,p+n]);uv.extend([(.4,i/max(1,len(points)-1)),(.6,i/max(1,len(points)-1))])
        if i:fs.append((2*i-2,2*i-1,2*i+1,2*i))
    return mesh(name,vs,fs,uv,tile,kind,bn,solid=.003,bevel=.001)

def torso_weights(p):
    z=p[2];a=max(0,min(1,(z-1.1)/.23))
    return {'Chest':a,'Spine':1-a}

# Continuous tailored doublet: shoulders narrow into an actual waist.
sleeve('TailoredGambeson',[(0,0,.86,.19,.108),(0,0,1.04,.155,.104),(0,0,1.23,.19,.122),(0,0,1.4,.235,.12),(0,0,1.49,.195,.085)],'bluecloth','cloth',torso_weights)

# Front and back are separate UV islands with purposeful neckline/arm cuts.
def cuirass(u,v,back=False):
    a=(u-.5)*math.pi
    w,d,z=interpolate([(.165,.11,1.08),(.162,.13,1.19),(.217,.17,1.35),(.237,.14,1.43),(.18,.082,1.515)],v)
    x=w*math.sin(a);y=d*math.cos(a)*( -1 if back else 1)
    if not back:
        y += .020*math.cos(a)**12*math.sin(math.pi*v)
        y += .004*math.cos(a*10)*math.sin(math.pi*v)**2*math.cos(a)
    # Neckline dips at center; armhole cuts away near lateral upper edges.
    z -= .052*max(0,(v-.75)/.25)*math.cos(a)**4
    z -= .024*max(0,(v-.78)/.22)*abs(math.sin(a))**6
    return (x,y,z)
patch('SculptedCuirass_Front',lambda u,v:cuirass(u,v),32,20,'chest','steel',torso_weights,solid=.009)
patch('SculptedCuirass_Back',lambda u,v:cuirass(u,v,True),28,18,'back','steel',torso_weights,solid=.009)
for s in [-1,1]:
    trim('CuirassRaisedBorder',[(s*.17,.02,1.1),(s*.18,.08,1.18),(s*.23,.04,1.38),(s*.20,.05,1.47),(s*.10,.1,1.485)],.009,'Chest')
sleeve('ArticulatedGorget',[(0,0,1.49,.125,.105),(0,0,1.53,.1,.09),(0,0,1.59,.085,.077)],'plain','steel','Neck',rings=7)
sleeve('VisibleMailNeck',[(0,0,1.54,.083,.073),(0,0,1.67,.092,.08),(0,0,1.72,.093,.084)],'mail','mail','Head',rings=8)

# Sallet: compact skull, swept nape, eye slit and projecting bevor.
def skull(u,v):
    a=(u-.5)*math.tau
    z,rx,ry=interpolate([(1.755,.114,.116),(1.81,.122,.124),(1.9,.107,.104),(1.965,.063,.065),(1.986,.003,.003)],v)
    rear=max(0,-math.cos(a));tail=(1-v)**5
    return (rx*math.sin(a),ry*math.cos(a)-.065*rear*tail,z-.045*rear*tail+.007*math.cos(a*2)*math.sin(math.pi*v))
patch('SalletCrown_Nape',skull,36,18,'helm','steel','Head',solid=.007)
def visor(u,v):
    a=(u-.5)*2.7
    return (.12*math.sin(a),.138*math.cos(a)+.018*(1-v),1.785+v*.048-.012*abs(math.sin(a)))
patch('VisorUpperLip',visor,28,5,'helm','steel','Head',solid=.007)
def bevor(u,v):
    a=(u-.5)*2.8;w=.091+v*.028
    return (w*math.sin(a),(.108+v*.035)*math.cos(a)+.014*math.cos(a)**10,1.70+v*.074+.013*abs(math.sin(a)))
patch('BevorCheekJaw',bevor,28,12,'plain','steel','Head',solid=.008)
trim('SalletBrowRim',[(-.113,.05,1.837),(-.08,.11,1.838),(0,.141,1.838),(.08,.11,1.838),(.113,.05,1.837)],.008,'Head')
trim('SalletMedianKeel',[(0,.10,1.90),(0,.06,1.967),(0,0,1.993),(0,-.07,1.957),(0,-.117,1.88)],.009,'Head',kind='steel',tile='plain')
# Dark recess is behind the physical gap, never a black face painted on mail.
patch('EyeRecess',lambda u,v:((u-.5)*.19,.10,1.77+v*.07),2,2,'boot','leather','Head')

# Waist is separated from thigh plates; fabric panels remain visible between.
sleeve('WaistHarness',[(0,0,1.075,.169,.135),(0,0,1.105,.17,.137)],'leather','leather','Pelvis',rings=3)
for level in range(2):
    z=1.10-level*.067
    patch('FauldFront_'+str(level),lambda u,v,z=z:((u-.5)*(.36+(1-v)*.055),.115+.036*math.cos((u-.5)*math.pi),z-.062+v*.068),20,5,'back','steel','Pelvis',solid=.007)
for s,side in [(-1,'L'),(1,'R')]:
    upper='UpperArm_'+side;fore='Forearm_'+side;thigh='Thigh_'+side;shin='Shin_'+side
    sleeve('MailUnderarm_'+side,[(s*.29,0,1.46,.06,.067),(s*.37,0,1.28,.062,.061),(s*.42,.014,1.13,.045,.052)],'mail','mail',upper)
    # Contoured asymmetric shoulder cap. Deliberate low apex, cut front/back,
    # extended lateral edge, not a spherical pauldron.
    for layer in range(2):
        def shoulder(u,v,s=s,layer=layer):
            a=(u-.5)*math.pi
            theta=v*1.5 if layer==0 else .95+v*.72
            x=s*(.215+.213*math.sin(theta))
            y=.12*math.sin(a)*(.72+.28*math.sin(theta))
            z=1.45+.078*math.cos(theta)-.062*math.sin(theta)-layer*.014-.022*abs(math.sin(a))**3
            x+=s*.013*math.cos(a)*math.sin(theta)**4
            return (x,y,z)
        patch('SweptPauldron_'+side+str(layer),shoulder,24,10,'shoulder','steel',upper,solid=.008)
    sleeve('TaperedRerebrace_'+side,[(s*.36,0,1.32,.066,.065),(s*.39,0,1.23,.058,.062),(s*.419,.01,1.17,.047,.051)],'arm','steel',upper)
    # Couter and knee wings authored as shaped patches with central arris.
    def wing(u,v,s=s,knee=False):
        width=.10 if knee else .075;cx=s*(.14 if knee else .424)
        return (cx+(u-.5)*width*2*(.55+.45*math.sin(math.pi*v)),
                (.11 if knee else .09)+.02*math.cos((u-.5)*math.pi),
                (.52 if knee else 1.1)+v*.095+.025*math.cos((u-.5)*math.pi)*math.sin(math.pi*v))
    patch('PointedCouter_'+side,wing,16,8,'arm','steel',fore,solid=.006)
    sleeve('Vambrace_'+side,[(s*.425,.025,1.10,.055,.064),(s*.43,.035,1.0,.06,.067),(s*.43,.06,.9,.044,.05)],'arm','steel',fore)
    sleeve('FittedGlove_'+side,[(s*.43,.06,.91,.044,.048),(s*.43,.065,.83,.054,.043),(s*.43,.08,.78,.046,.035)],'leather','leather','Hand_'+side,rings=8)
    patch('GauntletBack_'+side,lambda u,v,s=s:(s*.43+(u-.5)*.10,.116+.012*math.sin(math.pi*u),.79+v*.105),12,8,'arm','steel','Hand_'+side,solid=.004)
    for k,finger in enumerate(['Index','Middle','Ring','Little']):
        x=s*(.385+k*.027)
        sleeve(finger+'Grip_'+side,[(x,.085,.80,.011,.021),(x,.108,.76,.012,.020),(x,.12,.755,.009,.012)],'leather','leather',finger+'_'+side,segments=8,rings=6)
    sleeve('Thumb_'+side,[(s*.375,.055,.86,.02,.025),(s*.36,.10,.81,.014,.02)],'leather','leather','Thumb_'+side,segments=10,rings=5)
    sleeve('TailoredHose_'+side,[(s*.14,0,.96,.089,.087),(s*.14,0,.77,.095,.089),(s*.14,0,.56,.068,.071)],'bluecloth','cloth',thigh)
    sleeve('Cuisse_'+side,[(s*.14,0,.88,.093,.092),(s*.14,.003,.77,.092,.094),(s*.14,0,.61,.068,.075)],'leg','steel',thigh)
    patch('Tasset_'+side,lambda u,v,s=s:(s*(.055+u*.17),.145+.019*math.sin(math.pi*u),.845+v*.20+.02*math.sin(math.pi*u)),16,12,'leg','steel',thigh,solid=.007)
    patch('WingedPoleyn_'+side,lambda u,v:wing(u,v,knee=True),16,8,'leg','steel',shin,solid=.007)
    def greave(u,v,s=s):
        a=(u-.5)*math.tau
        rx,ry,z=interpolate([(.054,.063,.15),(.063,.07,.24),(.08,.079,.39),(.064,.068,.51)],v)
        flute=.006*max(0,math.cos(a))**12*math.sin(math.pi*v)
        return (s*.14+rx*math.sin(a),ry*math.cos(a)+flute,z)
    patch('RibbedGreave_'+side,greave,28,16,'leg','steel',shin,solid=.005)
    # Shaped footwear with pointed toe and higher instep, not flat bricks.
    def boot(u,v,s=s):
        a=(u-.5)*math.tau
        z,rx,depth,cy=interpolate([(.028,.073,.14,.08),(.07,.082,.17,.10),(.12,.075,.13,.07),(.19,.051,.064,.005)],v)
        return (s*.14+rx*math.sin(a),cy+depth*math.cos(a),z)
    patch('ShapedBoot_'+side,boot,28,12,'boot','leather','Foot_'+side,solid=.005)
    for j in range(3):
        patch('Sabaton_'+side+str(j),lambda u,v,s=s,j=j:(s*.14+(u-.5)*(.142-j*.006),.025+j*.061+v*.069,.132-j*.024+.015*math.cos((u-.5)*math.pi)-v*.024),12,5,'arm','steel','Foot_'+side,solid=.004)
    # Split ivory surcoat side panels swing with legs, a deliberate color mass.
    patch('SurcoatTail_'+side,lambda u,v,s=s:(s*(.035+u*.145),.105+.017*math.sin(u*math.pi*3),.66+v*.40),12,16,'tunic','cloth',thigh,solid=.003)

# A narrower, calf-length tailored cape with skinned folds and scalloped hem.
def cape_shape(u,v):
    t=1-v
    return ((u-.5)*(.35+t*.22),-.13-t*.18-.022*math.cos(u*math.pi*8)*(t*.7+.3),1.49-t*.89+.012*math.cos(u*math.pi*8)*t**7)
def cape_weights(p):
    t=max(0,min(1,(1.49-p[2])/.89));u=p[0]/(.35+t*.22)+.5
    band=max(0,min(1.999,u*2));a=int(band);b=a+1;f=band-a
    w=max(0,min(1,(t-.15)/.7))
    return {f'Cape_{a}_A':(1-f)*(1-w),f'Cape_{b}_A':f*(1-w),f'Cape_{a}_B':(1-f)*w,f'Cape_{b}_B':f*w}
patch('IvoryHeraldicCape',cape_shape,28,28,'cape','cloth',cape_weights,solid=.003)

# Curved heater shield; every vertex has dedicated front UV coordinates.
def shield(u,v):
    width=.205*(.22+.78*math.sin(v*math.pi/2)**.65)
    return (-.45+(u-.5)*width*2,.205+.045*math.cos((u-.5)*math.pi),.53+v*.61)
patch('ThornHeaterShield',shield,24,24,'shield','cloth','Forearm_L',solid=.032)
edge=[shield(0,i/12) for i in range(13)]+[shield(i/12,1) for i in range(1,13)]+[shield(1,1-i/12) for i in range(1,13)]
trim('ShieldRim',edge,.017,'Forearm_L')
trim('ShieldGrip',[(-.48,.18,.84),(-.43,.16,.84),(-.39,.18,.84)],.032,'Hand_L','leather','leather')
# Original cruciform arming sword: diamond section and taper, held in right fist.
vs=[];uv=[];fs=[]
for z,w in [(.87,.029),(.65,.027),(.23,.02),(.095,.001)]:
    for x,y in [(-w,0),(0,.007),(w,0),(0,-.007)]:
        vs.append((.43+x,.122+y,z));uv.append(((x/max(w,.001)+1)/2,(z-.095)/.775))
for j in range(3):
    for i in range(4):fs.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
mesh('DiamondSectionBlade',vs,fs,uv,'blade','steel','Hand_R',smooth=False)
trim('SwordGuard',[(.32,.12,.88),(.37,.12,.895),(.43,.12,.90),(.49,.12,.895),(.54,.12,.88)],.019,'Hand_R','steel','plain')
sleeve('SwordGrip',[(.43,.122,.90,.018,.018),(.43,.122,.99,.016,.016)],'leather','leather','Hand_R',segments=12,rings=6)
sleeve('SwordPommel',[(.43,.122,.99,.023,.023),(.43,.122,1.014,.018,.018),(.43,.122,1.025,.004,.004)],'brass','brass','Hand_R',segments=12,rings=5)

# The fist grips the hilt, not the blade. Outward carry provides ground
# clearance throughout the existing crouched locomotion cycle.
pivot=Vector((.43,.122,.825));carry=Matrix.Rotation(-.9,3,'Y')
for ob in objects:
    if ob.name in ['DiamondSectionBlade','SwordGuard','SwordGrip','SwordPommel']:
        for vertex in ob.data.vertices:
            p=vertex.co.copy();p.z-=.105
            vertex.co=pivot+carry@(p-pivot)

# Place the jaw immediately above the gorget. Reused head joint remains fixed;
# visual rest offset shortens the exposed neck without changing the rig.
for ob in objects:
    if ob.vertex_groups.get('Head') and len(ob.vertex_groups)==1:
        for vertex in ob.data.vertices:vertex.co.z-=.055

# Keep logical source components for editing, but export five skinned surfaces.
source_collection=bpy.data.collections.new('EDITABLE_SURFACES');bpy.context.scene.collection.children.link(source_collection)
for ob in objects:
    source_collection.objects.link(ob)
    for col in list(ob.users_collection):
        if col!=source_collection:col.objects.unlink(ob)
source_collection.hide_render=True
source_collection.hide_viewport=True
export_objects=[]
for kind,mat in MATS.items():
    clones=[]
    for ob in objects:
        if ob.data.materials[0]!=mat:continue
        copy=ob.copy();copy.data=ob.data.copy();bpy.context.collection.objects.link(copy);clones.append(copy)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in clones:ob.select_set(True)
    bpy.context.view_layer.objects.active=clones[0];bpy.ops.object.join()
    merged=clones[0];merged.name='Thorn_'+kind
    mod=merged.modifiers.new('ExportTriangles','TRIANGULATE')
    bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    export_objects.append(merged)

# Actual editable UV layout, exported by Blender, with region names in manifest.
bpy.ops.object.select_all(action='DESELECT')
for ob in export_objects:ob.select_set(True)
bpy.context.view_layer.objects.active=export_objects[0]
bpy.ops.uv.export_layout(filepath=str(BASE/'source/equipment_uv.svg'),export_all=True,mode='SVG',size=(1024,1024),opacity=.15)
uv_path=BASE/'source/equipment_uv.svg'
uv_path.write_text('\n'.join(line.rstrip() for line in uv_path.read_text().splitlines())+'\n')

# Explicit data maps: material-class roughness, not a fake high-poly normal bake.
# No normal image is invented. Form comes from mesh normals and rolled edges.
rough=bpy.data.images.new('EquipmentRoughness',width=256,height=256,alpha=False)
rough.colorspace_settings.name='Non-Color'
rough_by_region=[.72,.76,.72,.72,.74,.73,.92,.75,.96,.96,.91,.86,.94,.64,.74,.96]
pixels=[]
for y in range(256):
    row=3-y//64
    for x in range(256):
        value=rough_by_region[row*4+x//64];pixels.extend([value,value,value,1])
rough.pixels[:]=pixels;rough.filepath_raw=str(BASE/'textures/equipment_roughness.png');rough.file_format='PNG';rough.save()
for mat in MATS.values():
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=rough;tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'])
rig.animation_data.action=bpy.data.actions['idle'];bpy.context.scene.frame_set(0)
bpy.context.scene.render.fps=30
for im in [image,rough]:im.pack()
source=BASE/'source/blender/thorn_knight.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in export_objects:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(DEST),export_format='GLB',use_selection=True,export_yup=True,
    export_tangents=True,export_animations=True,export_skins=True,export_animation_mode='ACTIONS',
    export_frame_range=False,export_force_sampling=True,export_anim_single_armature=True)
metrics={'status':'art candidate; requires human art approval','blender':bpy.app.version_string,
    'bones':len(rig.data.bones),'triangles':sum(len(o.data.polygons) for o in export_objects),
    'draw_surfaces':len(export_objects),'parts':parts,'uv_regions':TILES,
    'atlas_size':list(image.size),'roughness_size':list(rough.size),'normal_map':'none; authored geometry normals',
    'uv_reuse':'mirrored limbs and shared small trim intentionally share designated atlas regions',
    'animation_source':'original project ashen_knight armature and five in-place clips reused, not a new mocap performance',
    'clips':{act.name:float((act.frame_range[1]-act.frame_range[0])/30) for act in dst.actions},
    'top_z_m':max(v.co.z for ob in objects for v in ob.data.vertices),
    'sword_carry_outward_radians':.9,
    'source':'separate editable surface patches and merged export meshes in .blend'}
(BASE/'source/build_manifest.json').write_text(json.dumps(metrics,indent=2)+'\n')
print('THORN_BUILD',json.dumps({k:v for k,v in metrics.items() if k not in ['parts','uv_regions']}))
