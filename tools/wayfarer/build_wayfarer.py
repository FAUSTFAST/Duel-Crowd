"""Original clothed adult + four SEPARATE equipment assets, Blender 4.5 LTS.

Authored anatomical/tailoring profiles, coherent facial surface, explicit UVs,
new relaxed humanoid rig and in-place actions. An editable art candidate, NOT
a finished hand-sculpted production human. Never reads old knight geometry.
Default refuses regeneration; save hand edits before -- --replace-generated.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Quaternion, Euler, Matrix

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'assets/characters/wayfarer'
if (BASE/'wayfarer.glb').exists() and '--replace-generated' not in sys.argv:
    raise RuntimeError('Save manual edits/checkpoint before --replace-generated')
for sub in ['textures','equipment','source/blender']:
    (BASE/sub).mkdir(parents=True, exist_ok=True)
(BASE/'source/blender/.gdignore').touch()
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for action in list(bpy.data.actions): bpy.data.actions.remove(action)

# Small, deliberately quiet palette fields, not photographic random noise.
# Individual 128px PNGs are editable sources; surface seams/folds are geometry.
PALETTES = {
 'skin':['a67957','b68b65','c29872','cba580','d3ae88'],
 'hair':['282623','332c24','3c3328','483d2e','534633'],
 'linen':['666150','706c58','77745e','7e7b65','86836c'],
 'trousers':['353c40','3d4548','454d50','4d5557','545c5d'],
 'leather':['302820','3d3025','493b2d','574635','624f3c'],
 'steel':['59646b','6b7980','7b8990','8e9ba0','9eaaad'],
 'wood':['39352b','494334','554d39','62583f','706448'],
 'eye':['a4957c','c4b89e','ddd4ba','e2d9bf','b9af98'],
}
MATS={}
def hash2(x,y): return ((x*374761393+y*668265263+19349663)^((x+y*15731)<<3)) & 65535
for kind, palette in PALETTES.items():
    rgb=[tuple(int(c[i:i+2],16)/255 for i in (0,2,4)) for c in palette]
    image=bpy.data.images.new('Way_'+kind+'_albedo',128,128,alpha=False)
    pixels=[]
    for y in range(128):
        for x in range(128):
            if kind in ('linen','trousers'):
                k=2+(1 if (x%12==0 and y%6<2) else -1 if (y%12==0 and x%6<2) else 0)
                if hash2(x//7,y//9)%19==0:k-=1
            elif kind in ('wood','hair'):
                k=1+int((math.sin(x*.48+math.sin(y*.055)*.9)+1)*1.45)
            elif kind=='steel':
                k=2+int(hash2(x//11,y//8)%13==0)-int(hash2(x//9,y//12)%17==0)
            else:
                k=2+int(hash2(x//9,y//7)%17==0)-int(hash2(x//8,y//11)%19==0)
            c=rgb[max(0,min(4,k))]; pixels.extend((*c,1))
    image.pixels[:]=pixels; image.filepath_raw=str(BASE/'textures'/f'{kind}_albedo.png')
    image.file_format='PNG'; image.save(); image.pack()
    mat=bpy.data.materials.new('Way_'+kind);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.63 if kind=='steel' else .92
    bs.inputs['Metallic'].default_value=.38 if kind=='steel' else 0
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest'
    mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    MATS[kind]=mat
for name,color in [('dark',(0.055,.045,.034,1)),('lip',(.36,.20,.15,1)),('iris',(.12,.16,.12,1))]:
    mat=bpy.data.materials.new('Way_'+name);mat.diffuse_color=color;mat.use_nodes=True
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color
    mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85
    MATS[name]=mat

# Human proportions: 1.79m crown, ~7.5 heads, .44m shoulders. No armor rig reuse.
adata=bpy.data.armatures.new('WayfarerSkeleton');rig=bpy.data.objects.new('WayfarerRig',adata)
bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig
rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=adata.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=adata.edit_bones[parent]
bone('Root',(0,0,0),(0,0,.16))
bone('Pelvis',(0,0,.92),(0,0,1.045),'Root')
bone('Spine',(0,0,1.045),(0,0,1.24),'Pelvis')
bone('Chest',(0,0,1.24),(0,0,1.455),'Spine')
bone('Neck',(0,0,1.455),(0,0,1.555),'Chest')
bone('Head',(0,0,1.555),(0,0,1.78),'Neck')
for s,side in [(-1,'L'),(1,'R')]:
    bone('Thigh_'+side,(s*.105,0,.92),(s*.105,.015,.52),'Pelvis')
    bone('Shin_'+side,(s*.105,.015,.52),(s*.105,0,.10),'Thigh_'+side)
    bone('Foot_'+side,(s*.105,0,.10),(s*.105,.19,.055),'Shin_'+side)
    bone('Toe_'+side,(s*.105,.19,.055),(s*.105,.27,.055),'Foot_'+side)
    bone('Clavicle_'+side,(s*.065,0,1.425),(s*.215,0,1.425),'Chest')
    bone('UpperArm_'+side,(s*.215,0,1.425),(s*.285,.008,1.13),'Clavicle_'+side)
    bone('Forearm_'+side,(s*.285,.008,1.13),(s*.315,.025,.89),'UpperArm_'+side)
    bone('Hand_'+side,(s*.315,.025,.89),(s*.32,.045,.775),'Forearm_'+side)
    for i,fn in enumerate(['Index','Middle','Ring','Little']):
        bone(fn+'_'+side,(s*(.284+i*.022),.046,.792),(s*(.284+i*.022),.055,.727+(i%3)*.004),'Hand_'+side)
    bone('Thumb_'+side,(s*.28,.03,.845),(s*.263,.08,.80),'Hand_'+side)
bpy.ops.object.mode_set(mode='OBJECT')
objects=[]; entries=[]
def clamp(x):return max(0,min(1,x))
def interp(points,t):
    a=t*(len(points)-1);i=min(len(points)-2,int(a));f=a-i
    p0=Vector(points[max(0,i-1)]);p1=Vector(points[i]);p2=Vector(points[i+1]);p3=Vector(points[min(len(points)-1,i+2)])
    return .5*(2*p1+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f**3)
def mesh(name,vs,fs,uv,kind,weights,category='base',solid=0):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update()
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
    data.materials.append(MATS[kind]);layer=data.uv_layers.new(name='TailoredUV')
    for loop in data.loops:layer.data[loop.index].uv=(.02+.96*uv[loop.vertex_index][0],.02+.96*uv[loop.vertex_index][1])
    for p in data.polygons:p.use_smooth=True
    if weights:
        ob.parent=rig
        for i,p in enumerate(vs):
            ws=weights(p) if callable(weights) else {weights:1}
            for bn,w in ws.items():
                if w>1e-5:(ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)).add([i],w,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    if solid:
        mod=ob.modifiers.new('SeamThickness','SOLIDIFY');mod.thickness=solid;mod.offset=-1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
    if weights:mod=ob.modifiers.new('SharedHumanoidSkin','ARMATURE');mod.object=rig
    objects.append(ob);entries.append({'name':name,'category':category,'kind':kind,'source_vertices':len(vs)})
    ob['region']=category
    return ob
def patch(name,fn,nu,nv,kind,weights,category='base',solid=0):
    vs=[];fs=[];uv=[]
    for j in range(nv+1):
        for i in range(nu+1):
            u=i/nu;v=j/nv;vs.append(fn(u,v));uv.append((u,v))
            if i and j:
                n=j*(nu+1)+i;fs.append((n-nu-2,n-nu-1,n,n-1))
    return mesh(name,vs,fs,uv,kind,weights,category,solid)
def loft(name,profiles,kind,weights,category='base',fold=0,nu=24,nv=24,solid=.003):
    def fn(u,v):
        x,y,z,rx,ry=interp(profiles,v);a=(u-.5)*math.tau
        ripple=fold*(math.cos(a*7+v*4)+.4*math.cos(a*11-v*5))*math.sin(math.pi*v)
        return (x+(rx+ripple)*math.sin(a),y+(ry+ripple)*math.cos(a),z)
    return patch(name,fn,nu,nv,kind,weights,category,solid)
def torso(p):
    t=clamp((p[2]-1.08)/.25)
    return {'Spine':1-t,'Chest':t}
def arm_weights(side,p):
    t=clamp((p[2]-1.075)/.12)
    return {'UpperArm_'+side:t,'Forearm_'+side:1-t}
def leg_weights(side,p):
    t=clamp((p[2]-.46)/.14)
    pelvis=clamp((p[2]-.84)/.12)
    return {'Pelvis':pelvis,'Thigh_'+side:t*(1-pelvis),'Shin_'+side:(1-t)*(1-pelvis)}

# Continuous face: shaped jaw/cheek/forehead; bridge, nostrils, lips and sockets
# deform the actual head surface. No separate ball-head or glued-on box nose.
head_profile=[(1.548,.035,.042,.006),(1.572,.061,.063,.005),(1.617,.078,.076,0),(1.665,.081,.078,0),(1.712,.079,.075,-.003),(1.76,.053,.055,-.006),(1.782,.001,.002,-.008)]
def face(u,v):
    z,rx,ry,cy=interp(head_profile,v);a=(u-.5)*math.tau;x=rx*math.sin(a);y=cy+ry*math.cos(a)
    front=max(0,math.cos(a))**14
    bridge=.018*math.exp(-((z-1.659)/.030)**2)
    tip=.030*math.exp(-((z-1.632)/.012)**2)
    mouth=.008*math.exp(-((z-1.593)/.008)**2)
    sockets=-.010*(math.exp(-((x-.033)/.018)**2)+math.exp(-((x+.033)/.018)**2))*math.exp(-((z-1.671)/.011)**2)
    y+=(bridge+tip)*front+mouth*max(0,math.cos(a))**5+sockets*max(0,math.cos(a))**3
    return (x,y,z)
patch('Head',face,64,50,'skin','Head',category='head')
loft('NeckSkin',[(0,0,1.435,.065,.055),(0,0,1.50,.045,.044),(0,.003,1.58,.042,.045)],'skin','Neck','neck',nu=24,nv=12)
for s in [-1,1]:
    # Almond-shaped sclera, dark iris, fine upper lid and brow are surface inlays.
    def eye(u,v,s=s):
        x=s*.033+(u-.5)*.027;h=.006*math.sin(math.pi*u)
        return (x,.077+.004*math.sin(math.pi*u),1.671+(v-.5)*h*2)
    patch('EyeWhite'+str(s),eye,12,4,'eye','Head','head')
    patch('Iris'+str(s),lambda u,v,s=s:(s*.033+(u-.5)*.009,.082,1.671+(v-.5)*.008),4,4,'iris','Head','head')
    patch('UpperLid'+str(s),lambda u,v,s=s:(s*.033+(u-.5)*.030,.078+.004*math.sin(math.pi*u),1.672+.006*math.sin(math.pi*u)+v*.0016),14,2,'leather','Head','head')
    patch('Brow'+str(s),lambda u,v,s=s:(s*.034+(u-.5)*.034,.077+.004*math.sin(math.pi*u),1.690+.004*math.sin(math.pi*u)+v*.002),16,2,'hair','Head','head')
    def ear(u,v,s=s):
        a=u*math.tau;r=math.sin(v*math.pi/2)
        return (s*(.079+.016*r*math.cos(a)),.002+.010*r*math.sin(a),1.646+.030*r*math.sin(a))
    patch('Ear'+str(s),ear,20,8,'skin','Head','head',solid=.004)
    patch('Nostril'+str(s),lambda u,v,s=s:(s*.009+(u-.5)*.009,.101,1.624+(v-.5)*.003),6,2,'lip','Head','head')
patch('Mouth',lambda u,v:((u-.5)*.041,.077+.004*math.cos((u-.5)*math.pi),1.594+(v-.5)*.003-.001*math.cos(u*math.pi*2)),20,3,'lip','Head','head')

# Groomed short hair with an asymmetrical hairline, taper and directional ridges.
head_samples=[interp(head_profile,i/500) for i in range(501)]
def skull_radius(z):
    if z>=1.782:return (.001,.001,-.008)
    row=min(head_samples,key=lambda p:abs(p[0]-z))
    return (row[1],row[2],row[3])
def hair(u,v):
    a=(u-.5)*math.tau;front=max(0,math.cos(a));bottom=1.603+.113*front**2+.004*math.sin(a*3)
    z=bottom+(1.790-bottom)*v;rx,ry,cy=skull_radius(z-.006)
    ripple=.0011*math.sin(a*25+v*10)*math.sin(math.pi*v)
    return ((rx+.004+ripple)*math.sin(a),cy+(ry+.004+ripple)*math.cos(a),z)
patch('Hair',hair,64,28,'hair','Head','hair',solid=.002)

# Body includes a closed underlying torso/hips; clothing has its own hide groups.
loft('BodyUnderTunic',[(0,0,.86,.16,.095),(0,0,1.04,.14,.085),(0,0,1.25,.18,.107),(0,0,1.40,.202,.087),(0,0,1.46,.07,.053)],'skin',torso,'body_under_cloth',nu=24,nv=24)
loft('Tunic',[(0,0,1.035,.16,.113),(0,0,1.075,.155,.108),(0,0,1.25,.188,.12),(0,0,1.385,.202,.105),(0,0,1.435,.176,.076),(0,0,1.465,.061,.052)],'linen',torso,'torso_cloth',fold=.0035,nu=40,nv=32)
loft('TunicHem',[(0,0,.806,.233,.148),(0,0,.88,.224,.143),(0,0,.97,.195,.129),(0,0,1.085,.162,.115)],'linen',lambda p:{'Pelvis':1-clamp((p[2]-1.01)/.08),'Spine':clamp((p[2]-1.01)/.08)},'tunic_hem',fold=.004,nu=40,nv=20)
loft('LinenCollar',[(0,0,1.451,.065,.057),(0,0,1.482,.053,.05)],'linen','Neck','collar',nu=28,nv=5)
# The seam ribbon is intentionally restrained. Belt is cloth, not armor.
loft('ClothWaistTie',[(0,0,1.015,.163,.114),(0,0,1.047,.161,.111)],'leather','Spine','waist_tie',nu=36,nv=5)
patch('TunicPlacket',lambda u,v:((u-.5)*.018,.077+(.12-.077)*(1-v),1.31+v*.13),4,10,'leather','Chest','torso_cloth',solid=.002)
for s,side in [(-1,'L'),(1,'R')]:
    aw=lambda p,side=side:arm_weights(side,p)
    loft('Sleeve_'+side,[(s*.198,0,1.416,.063,.070),(s*.246,0,1.35,.064,.068),(s*.273,0,1.235,.057,.059),(s*.287,.008,1.13,.053,.055),(s*.30,.016,1.027,.049,.049)],'linen',aw,'sleeves',fold=.0035,nu=28,nv=28)
    loft('ForearmSkin_'+side,[(s*.295,.013,1.07,.042,.044),(s*.312,.022,.98,.039,.041),(s*.315,.025,.885,.029,.032)],'skin','Forearm_'+side,'forearms',nu=24,nv=18)
    # Oval knuckles/palm blend to four individually tapered fingers, with thumb.
    loft('Palm_'+side,[(s*.315,.025,.901,.03,.031),(s*.318,.036,.849,.04,.023),(s*.32,.046,.794,.038,.019),(s*.32,.047,.779,.030,.017)],'skin','Hand_'+side,'hands',nu=28,nv=14)
    for i,fn in enumerate(['Index','Middle','Ring','Little']):
        x=s*(.284+i*.022);low=.729+abs(i-1)*.007
        loft(fn+'_'+side,[(x,.046,.799,.0108,.016),(x,.06,.764,.010,.013),(x,.067,low+.006,.008,.011),(x,.065,low,.003,.005)],'skin',fn+'_'+side,'hands',nu=12,nv=10)
    loft('Thumb_'+side,[(s*.286,.035,.856,.018,.020),(s*.265,.066,.824,.014,.016),(s*.263,.082,.802,.008,.011)],'skin','Thumb_'+side,'hands',nu=14,nv=12)
    lw=lambda p,side=side:leg_weights(side,p)
    loft('Trousers_'+side,[(s*.075,0,1.035,.076,.094),(s*.089,0,.95,.084,.100),(s*.109,0,.83,.095,.104),(s*.109,.012,.68,.09,.089),(s*.105,.015,.53,.066,.071),(s*.105,.001,.40,.069,.069),(s*.105,-.003,.24,.053,.053),(s*.105,0,.17,.043,.048)],'trousers',lw,'legs_cloth',fold=.003,nu=28,nv=34)
    loft('Shoe_'+side,[(s*.105,.066,.024,.055,.119),(s*.105,.083,.052,.066,.148),(s*.105,.068,.094,.061,.129),(s*.105,.012,.142,.041,.055),(s*.105,0,.192,.041,.047)],'leather','Foot_'+side,'feet_shoes',nu=32,nv=16)
    loft('Sole_'+side,[(s*.105,.079,.015,.059,.126),(s*.105,.083,.035,.066,.144)],'leather','Foot_'+side,'feet_shoes',nu=32,nv=4)

# Armor is export-separated, same exact rig and rest transforms; body garment
# gets hidden on equip. No metal/weapon mesh exists in the base export.
def cuirass(u,v):
    a=(u-.5)*math.tau
    z,rx,ry=interp([(1.035,.17,.123),(1.12,.174,.136),(1.27,.214,.148),(1.38,.229,.128),(1.443,.177,.09)],v)
    z-=.023*max(0,(v-.8)/.2)*abs(math.sin(a))**4
    y=ry*math.cos(a)+.012*max(0,math.cos(a))**10*math.sin(math.pi*v)
    return (rx*math.sin(a),y,z)
patch('Chestplate',cuirass,48,30,'steel',torso,'chest',solid=.008)
loft('ChestplateRolledWaist',[(0,0,1.035,.172,.125),(0,0,1.053,.174,.127)],'steel','Spine','chest',nu=40,nv=4,solid=.005)
loft('ChestplateGorget',[(0,0,1.433,.077,.066),(0,0,1.481,.058,.054)],'steel','Neck','chest',nu=28,nv=8,solid=.004)
# Open-face helmet, preserving readable face. Hair is hidden when worn.
def helm(u,v):
    a=(u-.5)*math.tau;front=max(0,math.cos(a))**3
    bottom=1.604+.101*front;z=bottom+(1.803-bottom)*v
    rx,ry,cy=skull_radius(z-.014)
    return ((rx+.010)*math.sin(a),cy+(ry+.011)*math.cos(a),z)
patch('Helmet',helm,48,24,'steel','Head','helmet',solid=.006)
for s in [-1,1]:
    patch('HelmetCheek'+str(s),lambda u,v,s=s:(s*(.076+u*.020),.023+v*.025,1.608+v*.104+.009*math.sin(u*math.pi)),10,12,'steel','Head','helmet',solid=.005)

# Grip-origin rigid items. Bone local transforms are exported in a manifest,
# not baked into the character skin. Grip pose uses a modest finger curl later.
grip=Vector((.315,.055,.815))
def swordpoint(p):
    # Carry blade diagonally, away from thigh and clear of the floor.
    return grip+Euler((0,-.76,0),'XYZ').to_matrix()@Vector(p)
def itempatch(name,fn,nu,nv,kind,cat):
    return patch(name,lambda u,v:swordpoint(fn(u,v)) if cat=='sword' else fn(u,v),nu,nv,kind,None,cat,solid=.005)
itempatch('LongswordBlade',lambda u,v:((u-.5)*(.055*(.18+.82*math.sin(v*math.pi/2))),.006*math.cos((u-.5)*math.pi),-.70+v*.65),8,26,'steel','sword')
itempatch('LongswordGuard',lambda u,v:((u-.5)*.235,.006+v*.018,-.049+.019*math.cos(u*math.tau)),16,3,'steel','sword')
# Grip and pommel loft in model coordinates, transformed as a rigid piece.
for name,profile,kind in [('SwordGrip',[(0,0,-.038,.018,.021),(0,0,.09,.017,.020)],'leather'),('SwordPommel',[(0,0,.085,.023,.024),(0,0,.12,.027,.025),(0,0,.135,.008,.01)],'steel')]:
    ob=loft(name,profile,kind,None,'sword',nu=16,nv=10)
    for vertex in ob.data.vertices:vertex.co=swordpoint(vertex.co)
# Curved, smaller heater shield: a plank body, forged rim, original twin stripe.
shield_center=Vector((-.34,.095,.91))
def shield_shape(u,v):
    z=.20-v*.50;width=.195*(1 if v<.45 else 1-.92*(v-.45)/.55)
    return shield_center+Vector(((u-.5)*width*2,.018+.050*(1-(u*2-1)**2),z))
itempatch('ShieldBoard',shield_shape,24,24,'wood','shield')
for edge in [0,1]:
    itempatch('ShieldRim'+str(edge),lambda u,v,edge=edge:shield_shape(.025*u if edge==0 else 1-.025*u,v)+Vector((0,.005,0)),3,24,'steel','shield')
itempatch('ShieldUpperRim',lambda u,v:shield_shape(u,v*.027)+Vector((0,.005,0)),24,3,'steel','shield')
for x in [.35,.57]:
    itempatch('ShieldStripe'+str(x),lambda u,v,x=x:shield_shape(x+u*.065,v*.81)+Vector((0,.006,0)),3,20,'linen','shield')

# Five fresh in-place actions. Foot targets solve a two-bone chain, preventing
# bone scaling. These are authored procedural cycles, not mocap or slope IK.
def world_rotation(bn,direction):
    pb=rig.pose.bones[bn];rest=pb.bone.matrix_local
    q=(pb.bone.tail_local-pb.bone.head_local).rotation_difference(Vector(direction).normalized())@rest.to_quaternion()
    parent=pb.parent.matrix.to_quaternion() if pb.parent else Quaternion()
    local_rest=(pb.parent.bone.matrix_local.inverted()@rest).to_quaternion() if pb.parent else rest.to_quaternion()
    pb.rotation_quaternion=local_rest.inverted()@parent.inverted()@q
    bpy.context.view_layer.update()
def leg_pose(side,y,z,bob):
    s=-1 if side=='L' else 1;hip=Vector((s*.105,0,.92+bob));foot=Vector((s*.105,y,z))
    axis=(foot-hip).normalized();d=min(.819,max(.2,(foot-hip).length))
    along=(.40028**2-.42027**2+d*d)/(2*d)
    front=(Vector((0,1,0))-axis*axis.y).normalized()
    knee=hip+axis*along+front*math.sqrt(max(0,.40028**2-along*along))
    world_rotation('Thigh_'+side,knee-hip);world_rotation('Shin_'+side,foot-knee)
    world_rotation('Foot_'+side,(0,.19,-.045))
rig.animation_data_create();fps=30;metrics={}
for clip,duration,speed in [('idle',2.4,0),('walk',.60,3.2),('run',.60,5.8),('turn_left',.70,0),('turn_right',.70,0)]:
    action=bpy.data.actions.new(clip);action.use_fake_user=True;rig.animation_data.action=action
    end=round(duration*fps)
    for frame in range(end+1):
        t=frame/end;phase=t*math.tau;moving=clip in ('walk','run');running=clip=='run'
        for pb in rig.pose.bones:
            pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.location=(0,0,0);pb.scale=(1,1,1)
        bob=(-.105 if running else -.094)+(.025 if running else .008)*(1-math.cos(phase*2)) if moving else -.006+.002*math.sin(phase)
        rig.pose.bones['Pelvis'].location.y=bob
        lean=.13 if running else .025 if moving else .004*math.sin(phase)
        twist=(.055 if running else .035)*math.sin(phase) if moving else .008*math.sin(phase)
        if clip.startswith('turn'):twist=(.18 if clip=='turn_left' else -.18)*math.sin(math.pi*t)
        rig.pose.bones['Spine'].rotation_quaternion=Euler((lean,twist,0)).to_quaternion()
        rig.pose.bones['Chest'].rotation_quaternion=Euler((-.02,-twist*.5,0)).to_quaternion()
        rig.pose.bones['Head'].rotation_quaternion=Euler((0,-twist*.3,.008*math.sin(phase))).to_quaternion()
        bpy.context.view_layer.update()
        for side,offset in [('L',0),('R',.5)]:
            p=(t+offset)%1;stance=.25 if running else .48;travel=speed*duration*stance
            if moving:
                if p<stance:y=travel*(.5-p/stance);z=.10
                else:
                    u=(p-stance)/(1-stance);y=travel*(-.5+u);z=.10+(.20 if running else .09)*math.sin(math.pi*u)
            else:y=0;z=.10
            leg_pose(side,y,z,bob)
            swing=(-1 if side=='L' else 1)*math.sin(phase)*(.42 if running else .24 if moving else .012)
            rig.pose.bones['UpperArm_'+side].rotation_quaternion=Euler((swing,0,0)).to_quaternion()
            rig.pose.bones['Forearm_'+side].rotation_quaternion=Euler((-.75 if running else -.07,0,0)).to_quaternion()
        for pb in rig.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            if pb.name=='Pelvis':pb.keyframe_insert('location',frame=frame,group=pb.name)
    metrics[clip]={'duration':end/fps,'reference_speed':speed}

# One export surface per visibility region/material. Do not merge distinct hide
# regions, nor put armor in the base asset. Keep editable, unmerged source too.
source_collection=bpy.data.collections.new('EDITABLE_SURFACES');bpy.context.scene.collection.children.link(source_collection)
groups={}
for ob in objects:
    category=ob['region'];kind=ob.data.materials[0].name
    groups.setdefault((category,kind),[]).append(ob)
    backup=ob.copy();backup.data=ob.data.copy();source_collection.objects.link(backup)
    backup.hide_viewport=True;backup.hide_render=True
merged=[]
for (category,kind),group in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for ob in group:ob.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    if len(group)>1:bpy.ops.object.join()
    ob=group[0];ob.name=category+'__'+kind;merged.append(ob)
rig.animation_data.action=bpy.data.actions['idle'];bpy.context.scene.frame_set(0)
bpy.context.scene.render.fps=fps
source=BASE/'source/blender/wayfarer.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(source))

opts=dict(export_format='GLB',use_selection=True,export_yup=True,export_tangents=True,
          export_skins=True,export_materials='EXPORT',export_animation_mode='ACTIONS',
          export_frame_range=False,export_force_sampling=True,export_bake_animation=True,
          export_anim_single_armature=True,export_extras=True)
available=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def export(path,categories,animated,skinned=True):
    bpy.ops.object.select_all(action='DESELECT')
    if skinned:rig.select_set(True);bpy.context.view_layer.objects.active=rig
    for ob in merged:
        if ob['region'] in categories:ob.select_set(True)
    options=dict(opts,filepath=str(path),export_animations=animated)
    bpy.ops.export_scene.gltf(**{k:v for k,v in options.items() if k in available})
base_regions=set(ob['region'] for ob in merged)-{'chest','helmet','sword','shield'}
export(BASE/'wayfarer.glb',base_regions,True)
rig.animation_data.action=None
for pb in rig.pose.bones:pb.rotation_quaternion=Quaternion();pb.location=(0,0,0)
bpy.context.view_layer.update()
for cat in ['chest','helmet','sword','shield']:
    export(BASE/'equipment'/f'{cat}.glb',{cat},False,cat in ['chest','helmet'])
manifest={'asset_status':'editable art candidate / equipment visual prototype',
 'blender':bpy.app.version_string,'height_m':1.795,'shoulder_width_m':.44,
 'bones':len(adata.bones),'actions':metrics,'parts':entries,
 'regions':sorted(base_regions),'hidden_by_default':['body_under_cloth'],
 'bone_rest':{b.name:[list(row) for row in b.matrix_local] for b in adata.bones},
 'rigid_rest_alignment':{'sword':'Hand_R','shield':'Hand_L'},
 'materials':'original procedural 128px palette fields; no high-poly bake',
 'source':str(source.relative_to(ROOT))}
(BASE/'source/build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('WAYFARER_BUILD',json.dumps({k:v for k,v in manifest.items() if k not in ['parts','bone_rest']}))
