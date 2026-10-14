"""Original fitted armor / humanoid rig. Blender 4.5.9, metres, Y-forward/Z-up.
Run Blender --background --factory-startup --python tools/characters/build_knight.py
Overwrites only the new ashen_knight assets. Save manual edits in Git first.
Meshes are authored cross-sections and swept surfaces, not primitive assembly.
Locomotion is in-place: world displacement is owned by the existing controller.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Quaternion, Euler

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'assets/characters/ashen_knight'
BASE.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
materials = {}
for name, metallic, roughness in [('steel', .68, .62), ('bronze', .6, .68), ('cloth', 0, .9), ('leather', 0, .94), ('mail', .45, .83)]:
    mat = bpy.data.materials.new('Oath_'+name); mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value = metallic; bs.inputs['Roughness'].default_value = roughness
    for channel in ('albedo', 'normal', 'roughness'):
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(BASE/'textures'/f'{name}_{channel}.png'))
        tex.interpolation = 'Closest'
        if channel != 'albedo': tex.image.colorspace_settings.name = 'Non-Color'
        if channel == 'normal':
            normal = mat.node_tree.nodes.new('ShaderNodeNormalMap'); normal.inputs['Strength'].default_value = .3
            mat.node_tree.links.new(tex.outputs['Color'], normal.inputs['Color'])
            mat.node_tree.links.new(normal.outputs['Normal'], bs.inputs['Normal'])
        else: mat.node_tree.links.new(tex.outputs['Color'], bs.inputs['Base Color' if channel=='albedo' else 'Roughness'])
    if name == 'cloth': mat.use_backface_culling = False
    materials[name] = mat

# A real hierarchy; the pelvis has no exported horizontal root motion.
adata = bpy.data.armatures.new('OathHumanoid'); rig = bpy.data.objects.new('OathRig', adata)
bpy.context.collection.objects.link(rig); bpy.context.view_layer.objects.active = rig
rig.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
def bone(name, head, tail, parent=None):
    b = adata.edit_bones.new(name); b.head = head; b.tail = tail
    if parent: b.parent = adata.edit_bones[parent]
    return b
bone('Root', (0,0,0), (0,0,.2))
bone('Pelvis', (0,0,.98), (0,0,1.12), 'Root')
bone('Spine', (0,0,1.12), (0,0,1.32), 'Pelvis')
bone('Chest', (0,0,1.32), (0,0,1.5), 'Spine')
bone('Neck', (0,0,1.5), (0,0,1.64), 'Chest')
bone('Head', (0,0,1.64), (0,0,1.93), 'Neck')
for side, s in [('L',-1), ('R',1)]:
    bone('Thigh_'+side, (s*.14,0,.98), (s*.14,0,.56), 'Pelvis')
    bone('Shin_'+side, (s*.14,0,.56), (s*.14,0,.13), 'Thigh_'+side)
    bone('Foot_'+side, (s*.14,0,.13), (s*.14,.19,.075), 'Shin_'+side)
    bone('Toe_'+side, (s*.14,.19,.075), (s*.14,.30,.075), 'Foot_'+side)
    bone('Clavicle_'+side, (s*.08,0,1.46), (s*.31,0,1.46), 'Chest')
    bone('UpperArm_'+side, (s*.31,0,1.46), (s*.42,.015,1.14), 'Clavicle_'+side)
    bone('Forearm_'+side, (s*.42,.015,1.14), (s*.43,.06,.89), 'UpperArm_'+side)
    bone('Hand_'+side, (s*.43,.06,.89), (s*.43,.07,.76), 'Forearm_'+side)
    for finger in ('Index','Middle','Ring','Little'):
        k = ('Index','Middle','Ring','Little').index(finger)
        bone(f'{finger}_{side}', (s*(.385+k*.027),.07,.8), (s*(.385+k*.027),.095,.73), 'Hand_'+side)
    bone('Thumb_'+side, (s*.375,.055,.86), (s*.355,.13,.8), 'Hand_'+side)
for i,x in enumerate((-.22,0,.22)):
    bone(f'Cape_{i}_A', (x,-.13,1.48), (x,-.24,1.02), 'Chest')
    bone(f'Cape_{i}_B', (x,-.24,1.02), (x,-.29,.51), f'Cape_{i}_A')
bpy.ops.object.mode_set(mode='OBJECT')
objects = []

def mesh(name, verts, faces, kind, weights, uvs=None, solid=0, bevel=0, smooth=True):
    data = bpy.data.meshes.new(name); data.from_pydata(verts, [], faces); data.update()
    ob = bpy.data.objects.new(name, data); bpy.context.collection.objects.link(ob)
    data.materials.append(materials[kind]); ob.parent = rig
    uv = data.uv_layers.new(name='UVMap')
    for loop in data.loops:
        uv.data[loop.index].uv = uvs[loop.vertex_index] if uvs else (verts[loop.vertex_index][0], verts[loop.vertex_index][2])
    for p in data.polygons: p.use_smooth = smooth
    for vi, w in enumerate(weights):
        for bn, value in w.items():
            group = ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
            group.add([vi], value, 'REPLACE')
    bpy.context.view_layer.objects.active = ob
    for other in bpy.context.selected_objects: other.select_set(False)
    ob.select_set(True)
    if solid:
        mod=ob.modifiers.new('ArmorThickness', 'SOLIDIFY'); mod.thickness=solid
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if bevel:
        mod=ob.modifiers.new('ForgedRolledEdges', 'BEVEL'); mod.width=bevel; mod.segments=2
        mod.limit_method='ANGLE'; mod.angle_limit=.5
        bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('Triangles', 'TRIANGULATE'); bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=ob.modifiers.new('SkinDeform', 'ARMATURE'); mod.object=rig
    objects.append(ob); return ob

def loft(name, rows, kind, bn, sides=24, open_eye=False, bulge=0):
    # rows: (x,y,z, half width, half depth). Seam duplicated for proper UVs.
    vs=[]; fs=[]; uv=[]; ws=[]
    for j,(x,y,z,rx,ry) in enumerate(rows):
        for i in range(sides+1):
            a=math.tau*i/sides
            ridge=bulge*max(0, math.sin(a))**8
            vs.append((x+rx*math.cos(a), y+ry*math.sin(a)+ridge,z))
            uv.append((i/sides, j/(len(rows)-1)))
            ws.append(bn(z) if callable(bn) else {bn:1})
        if j:
            for i in range(sides):
                a=math.tau*(i+.5)/sides
                if open_eye and j==3 and abs(a-math.pi/2)<.95: continue
                n=j*(sides+1)+i; p=n-(sides+1)
                fs.append((p,p+1,n+1,n))
    fs.extend([tuple(reversed(range(sides))), tuple((len(rows)-1)*(sides+1)+i for i in range(sides))])
    return mesh(name,vs,fs,kind,ws,uv,bevel=.003)

def ribbon(name, points, width, kind, bn):
    vs=[]; fs=[];uv=[]
    for i,p in enumerate(points):
        p=Vector(p); tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        cross=tangent.cross(Vector((0,1,0))).normalized()*width/2
        vs.extend([tuple(p-cross),tuple(p+cross)]); uv.extend([(0,i/max(1,len(points)-1)),(1,i/max(1,len(points)-1))])
        if i:fs.append((2*i-2,2*i-1,2*i+1,2*i))
    return mesh(name,vs,fs,kind,[{bn:1} for p in vs],uv,solid=.005,bevel=.002)

def panel(name, outline, kind, bn, convex=.02):
    center=sum((Vector(p) for p in outline), Vector())/len(outline);center.y+=convex
    vs=[tuple(center)]+list(outline);fs=[]
    for i in range(len(outline)):
        f=(0,1+i,1+(i+1)%len(outline))
        normal=(Vector(vs[f[1]])-Vector(vs[0])).cross(Vector(vs[f[2]])-Vector(vs[0]))
        fs.append(f if normal.y>0 else tuple(reversed(f)))
    xs=[p[0] for p in vs];zs=[p[2] for p in vs]
    uv=[((p[0]-min(xs))/max(.001,max(xs)-min(xs)),(p[2]-min(zs))/max(.001,max(zs)-min(zs))) for p in vs]
    return mesh(name,vs,fs,kind,[{bn:1} for p in vs],uv,solid=.009,bevel=.005)

def shoulder_shell(name, side, index):
    s=-1 if side=='L' else 1
    x=s*(.315+index*.027);z=1.435-index*.060
    rx=.188-index*.020;ry=.150-index*.015;rz=.164-index*.020
    angles=[.08,.4,.75,1.1,1.4,1.7,1.93] if index==0 else [1.0,1.25,1.55,1.95]
    vs=[];uv=[];fs=[];sides=24
    for j,theta in enumerate(angles):
        for i in range(sides+1):
            a=math.tau*i/sides
            flute=1+.035*math.cos(a*6)*math.sin(theta)
            vs.append((x+rx*math.sin(theta)*math.cos(a)*flute,ry*math.sin(theta)*math.sin(a)*flute,z+rz*math.cos(theta)))
            uv.append((i/sides,j/(len(angles)-1)))
        if j:
            for i in range(sides):
                n=j*(sides+1)+i;p=n-sides-1;fs.append((p,n,n+1,p+1))
    ob=mesh(name,vs,fs,'steel',[{'UpperArm_'+side:1} for p in vs],uv,solid=.006)
    edge=vs[-(sides+1):]
    ribbon(name+'_RolledEdge',edge,.012,'bronze','UpperArm_'+side)
    return ob

# Padded, skinned understructure plus fitted articulated outer plate.
def torso_weight(z):
    if z<1.08:return {'Pelvis':1}
    if z<1.3:return {'Spine':.8,'Pelvis':.2}
    return {'Chest':1}
loft('QuiltedArmingCoat',[(0,0,.87,.19,.105),(0,0,1.04,.17,.12),(0,0,1.17,.195,.13),(0,0,1.38,.25,.13),(0,0,1.48,.21,.10)],'cloth',torso_weight)
loft('Breastplate',[(0,.015,1.1,.17,.13),(0,.012,1.18,.2,.145),(0,.012,1.33,.25,.15),(0,0,1.43,.27,.13),(0,0,1.49,.21,.095)],'steel','Chest',bulge=.025)
loft('Gorget',[(0,0,1.46,.15,.1),(0,0,1.51,.12,.105),(0,0,1.57,.105,.09)],'bronze','Neck')
loft('MailCoif',[(0,0,1.53,.105,.1),(0,0,1.64,.12,.105),(0,0,1.78,.115,.12),(0,0,1.87,.075,.08)],'mail','Head')
loft('HelmetShell',[(0,0,1.63,.105,.105),(0,0,1.70,.135,.15),(0,0,1.755,.145,.155),(0,0,1.79,.145,.151),(0,-.005,1.87,.125,.126),(0,-.005,1.95,.073,.075),(0,-.005,1.99,.014,.015)],'steel','Head',open_eye=True)
ribbon('HelmetBrow', [(-.13,.085,1.797),(-.08,.14,1.805),(0,.159,1.81),(.08,.14,1.805),(.13,.085,1.797)], .021,'bronze','Head')
panel('VisorNasal', [(-.014,.159,1.81),(.014,.159,1.81),(.022,.175,1.68),(0,.18,1.65),(-.022,.175,1.68)],'steel','Head')
ribbon('HelmetCrest',[(0,.13,1.82),(0,.103,1.925),(0,0,2.015),(0,-.1,1.935),(0,-.14,1.79)],.026,'bronze','Head')
for level in range(3):
    z=1.11-level*.072
    loft(f'Fauld_{level}',[(0,0,z-.075,.215+level*.012,.135),(0,0,z-.015,.18+level*.012,.125),(0,0,z,.177+level*.012,.124)],'steel','Pelvis',sides=24)
loft('WaistBelt',[(0,0,1.095,.179,.145),(0,0,1.125,.18,.145)],'leather','Pelvis')
panel('BeltClasp',[(-.045,.151,1.09),(.045,.151,1.09),(.045,.151,1.135),(-.045,.151,1.135)],'bronze','Pelvis',.008)
ribbon('SwordHarness',[(-.21,-.15,1.43),(-.11,-.176,1.34),(.03,-.176,1.20),(.17,-.15,1.10)],.048,'leather','Chest')
ribbon('CuirassCentralRidge',[(0,.136,1.48),(0,.187,1.36),(0,.191,1.28),(0,.17,1.17)],.012,'bronze','Chest')
for s in [-1,1]:
    ribbon('CuirassChasedEdge',[(s*.20,.082,1.47),(s*.23,.11,1.4),(s*.22,.13,1.26),(s*.17,.11,1.14)],.012,'bronze','Chest')
    ribbon('OathCuirassInlay',[(0,.201,1.31),(s*.052,.186,1.34),(s*.072,.175,1.395),(s*.032,.181,1.41)],.012,'bronze','Chest')
for side,s in [('L',-1),('R',1)]:
    thigh='Thigh_'+side;shin='Shin_'+side;ua='UpperArm_'+side;fa='Forearm_'+side
    loft('MailSleeve_'+side,[(s*.31,0,1.43,.085,.085),(s*.365,0,1.30,.078,.078),(s*.415,.01,1.14,.065,.07)],'mail',ua,sides=16)
    for j in range(3):
        shoulder_shell(f'Pauldron_{side}_{j}',side,j)
    loft('Rerebrace_'+side,[(s*.365,0,1.32,.08,.084),(s*.398,.008,1.21,.071,.078),(s*.42,.015,1.16,.067,.077)],'steel',ua)
    loft('ElbowWing_'+side,[(s*.42,.015,1.10,.084,.09),(s*.43,.02,1.14,.105,.105),(s*.42,.012,1.19,.08,.08)],'steel',fa)
    loft('Vambrace_'+side,[(s*.42,.027,1.105,.072,.08),(s*.43,.039,.99,.068,.076),(s*.43,.06,.895,.052,.068)],'steel',fa)
    loft('Glove_'+side,[(s*.43,.06,.89,.055,.063),(s*.43,.07,.8,.065,.045),(s*.43,.08,.76,.051,.038)],'leather','Hand_'+side,sides=16)
    panel('GauntletPlate_'+side,[(s*.49,.118,.88),(s*.37,.118,.88),(s*.37,.13,.795),(s*.49,.13,.795)],'steel','Hand_'+side,.006)
    for k,finger in enumerate(('Index','Middle','Ring','Little')):
        x=s*(.385+k*.027)
        loft(f'{finger}Glove_{side}',[(x,.085,.8,.012,.02),(x,.095,.755,.012,.016),(x,.106,.735,.008,.01)],'leather',finger+'_'+side,sides=8)
    loft('Hose_'+side,[(s*.14,0,.92,.104,.10),(s*.14,0,.78,.11,.11),(s*.14,0,.6,.081,.087)],'mail',thigh,sides=20)
    loft('Cuisse_'+side,[(s*.14,.007,.88,.116,.114),(s*.14,.014,.78,.11,.109),(s*.14,.02,.62,.091,.102)],'steel',thigh)
    # Curved segmented front tassets, separate from articulated thighs.
    for j in range(3):
        z=1.01-j*.067
        panel(f'Tasset_{side}_{j}',[(s*.055,.151,z),(s*.255,.137,z+.01),(s*.28,.155,z-.066),(s*.055,.18,z-.081)],'steel',thigh,.012)
    loft('Poleyn_'+side,[(s*.14,.01,.515,.093,.11),(s*.14,.025,.56,.112,.14),(s*.14,.01,.61,.09,.11)],'steel',shin)
    loft('Greave_'+side,[(s*.14,0,.16,.065,.075),(s*.14,.005,.29,.085,.09),(s*.14,0,.43,.086,.09),(s*.14,0,.52,.074,.085)],'steel',shin,bulge=.02)
    loft('Boot_'+side,[(s*.14,.11,.035,.095,.195),(s*.14,.10,.08,.096,.198),(s*.14,.065,.14,.09,.15),(s*.14,.012,.18,.065,.075)],'leather','Foot_'+side,sides=24)
    for j in range(4):
        y=.025+j*.061
        panel(f'Sabaton_{side}_{j}',[(s*.14-.075,y,.144-j*.023),(s*.14+.075,y,.144-j*.023),(s*.14+.083,y+.071,.12-j*.022),(s*.14-.083,y+.071,.12-j*.022)],'steel','Foot_'+side,.003)

# Cloth has actual folds and a two-joint three-column deforming cape.
vs=[];fs=[];uv=[];ws=[];rows,cols=17,17
for j in range(rows):
    t=j/(rows-1); z=1.46-t*.95
    for i in range(cols):
        u=i/(cols-1);x=(u-.5)*(.42+t*.20)
        y=-.145-t*.15-.025*math.cos(u*math.tau*4)*(t*.65+.35)
        hem=.025*math.sin(u*math.pi*7)*max(0,(t-.85)/.15)
        vs.append((x,y,z+hem));uv.append((u,1-t))
        band=u*2;a=min(1,int(band));b=a+1;f=band-a
        vertical=max(0,min(1,(t-.18)/.62))
        w={f'Cape_{a}_A':(1-f)*(1-vertical),f'Cape_{a}_B':(1-f)*vertical,
           f'Cape_{b}_A':f*(1-vertical),f'Cape_{b}_B':f*vertical}
        ws.append({k:v for k,v in w.items() if v>.00001})
        if i and j:
            n=j*cols+i;fs.append((n-cols-1,n-cols,n,n-1))
mesh('OxbloodCape',vs,fs,'cloth',ws,uv,solid=.004)

# Original curved kite shield; the broken sun / vertical oath blade is our emblem.
outline=[(-.43,.205,1.13),(-.63,.18,1.06),(-.66,.19,.86),(-.60,.2,.65),(-.43,.24,.43),(-.26,.2,.65),(-.20,.19,.86),(-.23,.18,1.06)]
panel('KiteShield',outline,'cloth','Forearm_L',.105)
for i in range(len(outline)):
    ribbon('ShieldRolledRim_'+str(i),[outline[i],outline[(i+1)%len(outline)]],.028,'bronze','Forearm_L')
ribbon('OathBladeEmblem',[(-.43,.335,1.06),(-.43,.34,.79),(-.43,.3,.60)],.027,'bronze','Forearm_L')
ribbon('OathSunEmblem',[(-.54,.293,.86),(-.51,.324,.94),(-.43,.342,.98),(-.35,.324,.94),(-.32,.293,.86)],.021,'bronze','Forearm_L')
# Sword rests downward outside the calf; equipment is visual, no combat colliders.
panel('SwordBlade',[(.43,.10,.72),(.476,.10,.63),(.47,.10,.15),(.43,.11,.04),(.39,.10,.15),(.384,.10,.63)],'steel','Hand_R',.016)
ribbon('SwordFuller',[(.43,.132,.60),(.43,.13,.17)],.012,'bronze','Hand_R')
ribbon('SwordQuillons',[(.32,.1,.72),(.35,.12,.75),(.51,.12,.75),(.54,.10,.72)],.035,'bronze','Hand_R')
loft('SwordGrip',[(.43,.1,.74,.021,.024),(.43,.1,.86,.019,.022),(.43,.1,.88,.032,.03)],'leather','Hand_R',sides=12)
loft('SwordPommel',[(.43,.1,.87,.025,.025),(.43,.1,.91,.034,.028),(.43,.1,.93,.013,.018)],'bronze','Hand_R',sides=12)
# Carry the blade diagonally outside the leg. A downward vertical blade would
# penetrate the floor when the animated pelvis lowers during running.
pivot=Vector((.43,.1,.8));carry=Euler((0,math.radians(-50),0),'XYZ').to_matrix()
for ob in objects:
    if ob.name in ('SwordBlade','SwordFuller','SwordQuillons','SwordGrip','SwordPommel'):
        for vertex in ob.data.vertices:vertex.co=pivot+carry@(vertex.co-pivot)

# Bind pose uses relaxed arms. Generate world-aligned two-bone foot targets
# for stance, then solve local rotations. Feet travel backward at authored speed
# while grounded; the controller scales the clip to actual horizontal velocity.
def world_rotation(bn, direction):
    pb=rig.pose.bones[bn]; rest=pb.bone.matrix_local
    q=(pb.bone.tail_local-pb.bone.head_local).rotation_difference(Vector(direction).normalized()) @ rest.to_quaternion()
    parent=pb.parent.matrix.to_quaternion() if pb.parent else Quaternion()
    local_rest=(pb.parent.bone.matrix_local.inverted()@rest).to_quaternion() if pb.parent else rest.to_quaternion()
    pb.rotation_quaternion=local_rest.inverted() @ parent.inverted() @ q
    bpy.context.view_layer.update()

def leg_pose(side, target, bob):
    s=-1 if side=='L' else 1
    hip=Vector((s*.14,0,.98+bob));foot=Vector((s*.14,target[0],target[1]))
    line=foot-hip;distance=min(.846,max(.2,line.length));axis=line.normalized()
    along=(.42**2-.43**2+distance**2)/(2*distance)
    front=(Vector((0,1,0))-axis*axis.dot(Vector((0,1,0)))).normalized()
    knee=hip+axis*along+front*math.sqrt(max(0,.42**2-along**2))
    world_rotation('Thigh_'+side,knee-hip);world_rotation('Shin_'+side,foot-knee)
    world_rotation('Foot_'+side,(0,.19,-.055))

rig.animation_data_create();fps=30
clip_metrics={}
for clip,duration,speed in [('idle',2.4,0),('walk',.5666667,3.2),('run',.60,5.8),('turn_left',.64,0),('turn_right',.64,0)]:
    action=bpy.data.actions.new(clip);action.use_fake_user=True;rig.animation_data.action=action
    end=round(duration*fps);duration=end/fps
    for frame in range(end+1):
        t=frame/end;phase=t*math.tau
        for pb in rig.pose.bones:
            pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.location=(0,0,0);pb.scale=(1,1,1)
        locomotion=clip in ('walk','run');running=clip=='run'
        # Flex the pelvis so planted feet can reach their stride targets without
        # stretching the thigh/shin. Lengths remain .42/.43m, never scale bones.
        bob=(-.19 if running else -.145)+(.018 if running else .006)*(1-math.cos(phase*2)) if locomotion else -.025+.003*math.sin(phase)
        # Pose locations/rotations use bone-local axes: local Y is vertical.
        rig.pose.bones['Pelvis'].location.y=bob
        lean=.14 if running else .035 if locomotion else 0
        twist=(.05 if running else .025)*math.sin(phase) if locomotion else .012*math.sin(phase)
        if clip.startswith('turn'):
            twist=(.19 if clip=='turn_left' else -.19)*math.sin(math.pi*t)
        rig.pose.bones['Spine'].rotation_quaternion=Euler((lean,twist,0),'XYZ').to_quaternion()
        rig.pose.bones['Chest'].rotation_quaternion=Euler((-.02,-twist*.45,0),'XYZ').to_quaternion()
        rig.pose.bones['Head'].rotation_quaternion=Euler((0,-twist*.35,.016*math.sin(phase)),'XYZ').to_quaternion()
        bpy.context.view_layer.update()
        for side,offset in [('L',0),('R',.5)]:
            p=(t+offset)%1
            stance=.28 if running else .52
            travel=speed*duration*stance
            if locomotion:
                if p<stance:
                    y=travel*(.5-p/stance);z=.13
                else:
                    u=(p-stance)/(1-stance)
                    y=travel*(-.5+u);z=.13+(.22 if running else .11)*math.sin(math.pi*u)
            else:y=0;z=.13
            leg_pose(side,(y,z),bob)
            swing=(-1 if side=='L' else 1)*math.sin(phase)*(.27 if running else .13 if locomotion else .008)
            rig.pose.bones['UpperArm_'+side].rotation_quaternion=Euler((swing,0,0),'XYZ').to_quaternion()
            rig.pose.bones['Forearm_'+side].rotation_quaternion=Euler((-.20 if running else -.05,0,0),'XYZ').to_quaternion()
        for i in range(3):
            rig.pose.bones[f'Cape_{i}_A'].rotation_quaternion=Euler((-.05-lean*.8+.025*math.sin(phase+i*.7),.014*math.sin(phase+i),0),'XYZ').to_quaternion()
            rig.pose.bones[f'Cape_{i}_B'].rotation_quaternion=Euler((.03+.06*math.sin(phase-.6+i*.5),.018*math.cos(phase+i),0),'XYZ').to_quaternion()
        for pb in rig.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            if pb.name=='Pelvis':pb.keyframe_insert('location',frame=frame,group=pb.name)
    clip_metrics[clip]={'duration':duration,'authored_speed_m_s':speed}
# Merge by material while preserving weights, UVs and the Armature modifier.
# Five skinned draw surfaces rather than 87 separately submitted armor pieces.
part_names=[o.name for o in objects]; merged=[]
groups={kind:[o for o in objects if o.data.materials[0]==mat] for kind,mat in materials.items()}
for kind,mat in materials.items():
    group=groups[kind]
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join()
    group[0].name='Oath_'+kind.title();merged.append(group[0])
objects=merged
rig.animation_data.action=bpy.data.actions['idle'];bpy.context.scene.frame_set(0)
bpy.context.scene.render.fps=fps
for image in bpy.data.images:
    if image.filepath: image.pack()
source=BASE/'source/blender/ashen_knight.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
opts=dict(filepath=str(BASE/'ashen_knight.glb'),export_format='GLB',use_selection=True,
          export_yup=True,export_tangents=True,export_animations=True,export_skins=True,
          export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,
          export_bake_animation=True,export_anim_single_armature=True,export_materials='EXPORT')
props=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
opts={k:v for k,v in opts.items() if k in props}
bpy.ops.export_scene.gltf(**opts)
metrics={'bones':len(adata.bones),'mesh_parts':len(objects),'triangles':sum(len(o.data.polygons) for o in objects),
         'authored_parts':part_names,'clips':clip_metrics,'height_m':2.015,'material_tiles_px':128,'blender':bpy.app.version_string}
(BASE/'source/build_manifest.json').write_text(json.dumps(metrics,indent=2)+'\n')
print('KNIGHT_BUILD',json.dumps(metrics))
