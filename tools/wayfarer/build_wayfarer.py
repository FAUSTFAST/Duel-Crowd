"""Original clothed adult + four SEPARATE equipment assets, Blender 4.5 LTS.

Authored anatomical/tailoring profiles, coherent facial surface, explicit UVs,
new relaxed humanoid rig and in-place actions. An editable art candidate, NOT
a finished hand-sculpted production human. Never reads old knight geometry.
Default refuses regeneration; save hand edits before -- --replace-generated.
"""
import bpy, math, json, sys
sys.dont_write_bytecode=True  # Local build helper import; no project cache files.
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
 'skin':['b38a67','b9906d','bf9672','c49b77','c9a07c'],
 'hair':['1d2224','222729','272c2d','2c3131','323734'],
 'linen':['5e4334','6c4e3b','795a42','87664b','947254'],
 'trousers':['323234','3d3b3a','484440','534d46','60584f'],
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
            elif kind=='hair':
                k=2-int(x%29<2)+int((x+3)%43==0)
            elif kind=='wood':
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

# Reference-guided silhouette, not a reproduction of the reference costume.
# These landmarks drive BOTH the rest rig and animation IK. Never scale bones
# to repair proportions after skinning. Clothing/gear are refitted below.
ANATOMY={'crown':1.80,'chin':1.545,'shoulder':1.435,'hip':.935,
         'knee':.515,'ankle':.105,'hip_half_width':.103,
         'elbow':1.155,'wrist':.910,'head_width':.181}
adata=bpy.data.armatures.new('WayfarerSkeleton');rig=bpy.data.objects.new('WayfarerRig',adata)
bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig
rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=adata.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=adata.edit_bones[parent]
bone('Root',(0,0,0),(0,0,.16))
bone('Pelvis',(0,0,ANATOMY['hip']),(0,0,1.075),'Root')
bone('Spine',(0,0,1.075),(0,0,1.275),'Pelvis')
bone('Chest',(0,0,1.275),(0,0,1.475),'Spine')
bone('Neck',(0,0,1.475),(0,0,1.56),'Chest')
bone('Head',(0,0,1.56),(0,0,1.795),'Neck')
for s,side in [(-1,'L'),(1,'R')]:
    bone('Thigh_'+side,(s*.103,0,ANATOMY['hip']),(s*.103,.018,ANATOMY['knee']),'Pelvis')
    bone('Shin_'+side,(s*.103,.018,ANATOMY['knee']),(s*.103,0,ANATOMY['ankle']),'Thigh_'+side)
    bone('Foot_'+side,(s*.103,0,ANATOMY['ankle']),(s*.103,.18,.055),'Shin_'+side)
    bone('Toe_'+side,(s*.103,.18,.055),(s*.103,.23,.055),'Foot_'+side)
    bone('Clavicle_'+side,(s*.06,0,1.465),(s*.188,0,ANATOMY['shoulder']),'Chest')
    bone('UpperArm_'+side,(s*.188,0,ANATOMY['shoulder']),(s*.218,.018,ANATOMY['elbow']),'Clavicle_'+side)
    bone('Forearm_'+side,(s*.218,.018,ANATOMY['elbow']),(s*.231,.025,ANATOMY['wrist']),'UpperArm_'+side)
    bone('Hand_'+side,(s*.231,.025,ANATOMY['wrist']),(s*.236,.045,.802),'Forearm_'+side)
    for i,fn in enumerate(['Index','Middle','Ring','Little']):
        bone(fn+'_'+side,(s*(.206+i*.020),.043,.807),(s*(.206+i*.020),.060,.807-[.055,.064,.059,.044][i]),'Hand_'+side)
    bone('Thumb_'+side,(s*.205,.03,.870),(s*.182,.07,.815),'Hand_'+side)
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
            ws=weights(p) if callable(weights) else weights[i] if isinstance(weights,list) else {weights:1}
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
    t=clamp((p[2]-1.10)/.25)
    return {'Spine':1-t,'Chest':t}
def arm_weights(side,p):
    t=clamp((p[2]-1.095)/.12)
    return {'UpperArm_'+side:t,'Forearm_'+side:1-t}
def leg_weights(side,p):
    t=clamp((p[2]-.46)/.12)
    pelvis=clamp((p[2]-.84)/.16)
    return {'Pelvis':pelvis,'Thigh_'+side:t*(1-pelvis),'Shin_'+side:(1-t)*(1-pelvis)}

# Anatomical surfaces are kept separate from rig/export code for hand editing.
sys.path.insert(0,str(Path(__file__).parent))
from human_surfaces import build as build_human_surfaces
skull_radius=build_human_surfaces(patch,loft,mesh,interp,clamp,torso,arm_weights,leg_weights)

# Armor is export-separated, same exact rig and rest transforms; body garment
# gets hidden on equip. No metal/weapon mesh exists in the base export.
def cuirass(u,v):
    a=(u-.5)*math.tau
    z,rx,ry=interp([(1.067,.161,.125),(1.15,.168,.138),(1.29,.193,.143),(1.39,.206,.124),(1.470,.092,.065)],v)
    z-=.023*max(0,(v-.8)/.2)*abs(math.sin(a))**4
    y=ry*math.cos(a)+.012*max(0,math.cos(a))**10*math.sin(math.pi*v)
    return (rx*math.sin(a),y,z)
patch('Chestplate',cuirass,48,30,'steel',torso,'chest',solid=.008)
loft('ChestplateRolledWaist',[(0,0,1.066,.164,.127),(0,0,1.083,.165,.130)],'steel','Spine','chest',nu=40,nv=4,solid=.005)
loft('ChestplateGorget',[(0,0,1.467,.081,.069),(0,0,1.517,.060,.060)],'steel','Neck','chest',nu=28,nv=8,solid=.004)
# Open-face helmet, preserving readable face. Hair is hidden when worn.
def helm(u,v):
    a=(u-.5)*math.tau;front=max(0,math.cos(a))**3
    bottom=1.610+.110*front;z=bottom+(1.825-bottom)*v
    rx,ry,cy=skull_radius(z-.022)
    return ((rx+.010)*math.sin(a),cy+(ry+.011)*math.cos(a),z)
patch('Helmet',helm,48,24,'steel','Head','helmet',solid=.006)
for s in [-1,1]:
    patch('HelmetCheek'+str(s),lambda u,v,s=s:(s*(.087+u*.017),.023+v*.025,1.611+v*.105+.009*math.sin(u*math.pi)),10,12,'steel','Head','helmet',solid=.005)

# Grip-origin rigid items. Bone local transforms are exported in a manifest,
# not baked into the character skin. Grip pose uses a modest finger curl later.
grip=Vector((.232,.055,.830))
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
shield_center=Vector((-.252,.095,.925))
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
    s=-1 if side=='L' else 1
    hip=Vector((s*ANATOMY['hip_half_width'],0,ANATOMY['hip']+bob))
    foot=Vector((s*ANATOMY['hip_half_width'],y,z))
    upper=adata.bones['Thigh_'+side].length;lower=adata.bones['Shin_'+side].length
    axis=(foot-hip).normalized();d=min(upper+lower-.001,max(.2,(foot-hip).length))
    along=(upper**2-lower**2+d*d)/(2*d)
    front=(Vector((0,1,0))-axis*axis.y).normalized()
    knee=hip+axis*along+front*math.sqrt(max(0,upper**2-along*along))
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
                if p<stance:y=travel*(.5-p/stance);z=ANATOMY['ankle']
                else:
                    u=(p-stance)/(1-stance);y=travel*(-.5+u);z=ANATOMY['ankle']+(.20 if running else .09)*math.sin(math.pi*u)
            else:y=0;z=ANATOMY['ankle']
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
for ob in list(objects):
    backup=ob.copy();backup.data=ob.data.copy();source_collection.objects.link(backup)
    backup.hide_viewport=True;backup.hide_render=True
    if ob.get('split_sleeves'):
        # Keep the connected authored mesh in the editable collection. Only
        # split the export at the armhole for runtime chest visibility masks.
        import bmesh
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
        bpy.context.view_layer.objects.active=ob
        group_index=ob.vertex_groups['VIS_SLEEVES'].index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='DESELECT')
        bm=bmesh.from_edit_mesh(ob.data);deform=bm.verts.layers.deform.active
        for f in bm.faces:
            f.select_set(all(v[deform].get(group_index,0)>.5 for v in f.verts))
        bmesh.update_edit_mesh(ob.data)
        before=set(bpy.data.objects)
        bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
        sleeves=(set(bpy.data.objects)-before).pop();sleeves.name='ContinuousSleeves'
        sleeves['region']='sleeves';objects.append(sleeves)
groups={}
for ob in objects:
    category=ob['region'];kind=ob.data.materials[0].name
    groups.setdefault((category,kind),[]).append(ob)
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
base_points=[v.co for ob in merged if ob['region'] in base_regions for v in ob.data.vertices]
rest_bounds=[[min(p[i] for p in base_points),max(p[i] for p in base_points)] for i in range(3)]
shoulders=[p for ob in merged if ob['region'] in ['torso_cloth','sleeves'] for p in (v.co for v in ob.data.vertices) if 1.38<p.z<1.48]
manifest={'asset_status':'editable art candidate / equipment visual prototype',
 'blender':bpy.app.version_string,'height_m':rest_bounds[2][1]-rest_bounds[2][0],
 'shoulder_width_m':max(p.x for p in shoulders)-min(p.x for p in shoulders),'rest_bounds_m':rest_bounds,
 'anatomical_landmarks_m':ANATOMY,'head_units_to_anatomical_crown':round(ANATOMY['crown']/(ANATOMY['crown']-ANATOMY['chin']),3),
 'revision':'reference-guided natural proportions; short cloth shirt; connected shoulders and trouser seat',
 'bones':len(adata.bones),'actions':metrics,'parts':entries,
 'regions':sorted(base_regions),'hidden_by_default':['body_under_cloth'],
 'bone_rest':{b.name:[list(row) for row in b.matrix_local] for b in adata.bones},
 'rigid_rest_alignment':{'sword':'Hand_R','shield':'Hand_L'},
 'materials':'original procedural 128px palette fields; no high-poly bake',
 'source':str(source.relative_to(ROOT))}
(BASE/'source/build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('WAYFARER_BUILD',json.dumps({k:v for k,v in manifest.items() if k not in ['parts','bone_rest']}))
