"""Author original contact-based locomotion for the isolated Mutsumi preview.

Blender --background --disable-autoexec --python-exit-code 1 --python THIS
Only reads the already collected local GLB. Never saves the downloaded source or
runs embedded scripts. New native/GLB/previews stay inside the ignored library.
These are an animation study, not motion capture, cloth physics or art approval.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import sys
import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / 'local_assets/bang_dream'
SOURCE = LIBRARY / 'models/mutsumi/map_preview_v2/mutsumi_map.glb'
p = argparse.ArgumentParser()
p.add_argument('--output', default='models/mutsumi/motion_preview_v5')
args = p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = (LIBRARY / args.output).resolve()
assert OUT.is_relative_to(LIBRARY.resolve())
if OUT.exists():
    raise RuntimeError('Refusing to overwrite existing study: choose a new --output')
OUT.mkdir(parents=True)
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
scene = bpy.context.scene
rig = next(o for o in scene.objects if o.type == 'ARMATURE')
meshes = [o for o in scene.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers)]
for obj in list(scene.objects):
    if obj != rig and obj not in meshes:
        bpy.data.objects.remove(obj, do_unlink=True)

def digest_meshes(include_weights=True):
    h = hashlib.sha256()
    for obj in sorted(meshes, key=lambda o:o.name):
        h.update(obj.name.encode())
        for v in obj.data.vertices:
            h.update(struct.pack('<3f', *v.co))
            if include_weights:
                for g in v.groups:
                    h.update(struct.pack('<If', g.group, g.weight))
        for layer in obj.data.uv_layers:
            for uv in layer.data:
                h.update(struct.pack('<2f', *uv.uv))
    return h.hexdigest()
source_skin_sha = digest_meshes()
geometry_sha = digest_meshes(False)
rests = {b.name: [list(r) for r in b.matrix_local] for b in rig.data.bones}
rig.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
for pb in rig.pose.bones:
    assert not pb.constraints
    pb.rotation_mode = 'QUATERNION'
FPS = 60
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 0, 60
HEIGHT = 5.797128543257713
SCALE = 1.58 / HEIGHT
GAITS = {
    'walk':dict(distance=1.25, duty=.62, lift=.070, arm=.25, elbow=.22, lean=.025),
    'run':dict(distance=1.80, duty=.40, lift=.145, arm=.47, elbow=.68, lean=.085),
}

def smooth(x):
    x = max(0, min(1, x))
    return x*x*(3-2*x)

# The source skirt has 3,105 vertices attached to the exporter neutral bone,
# so it remains in world rest while the pelvis/legs move. Rebind only this new
# study's skirt, without new bones, topology edits or changes to the source.
skirt = next(o for o in meshes if any(s.material and 'DRESS' in s.material.name for s in o.material_slots))
weight_changes = []
for v in skirt.data.vertices:
    old = {skirt.vertex_groups[g.group].name:g.weight for g in v.groups}
    z,x = v.co.z,v.co.x
    if z>3.40 and sum(w for n,w in old.items() if n!='neutral_bone')>.01:
        new = {n:w for n,w in old.items() if n!='neutral_bone'}
        total=sum(new.values());new={n:w/total for n,w in new.items()}
    else:
        lower=smooth((3.40-z)/.60)
        follow=.99*lower
        left=.5+.5*math.tanh(x/.035)
        new={'下半身':1-follow,'足.L':follow*left,'足.R':follow*(1-left)}
    if old != new:
        weight_changes.append({'vertex':v.index,'original':old,'motion':new})
        for group in skirt.vertex_groups:group.remove([v.index])
        for name,weight in new.items():
            group=skirt.vertex_groups.get(name) or skirt.vertex_groups.new(name=name)
            group.add([v.index],weight,'REPLACE')
motion_skin_sha=digest_meshes()
(OUT/'skirt_weight_changes.json').write_text(json.dumps({'mesh':skirt.name,'changes':weight_changes},ensure_ascii=False,indent=2)+'\n')

def curve(points, x):
    for (a, va), (b, vb) in zip(points, points[1:]):
        if x <= b:
            return va + (vb-va)*smooth((x-a)/(b-a))
    return points[-1][1]

def orient(name, quaternion):
    pb = rig.pose.bones[name]
    local_rest = (pb.parent.bone.matrix_local.inverted() @ pb.bone.matrix_local).to_quaternion() if pb.parent else pb.bone.matrix_local.to_quaternion()
    parent = pb.parent.matrix.to_quaternion() if pb.parent else Quaternion()
    pb.rotation_quaternion = local_rest.inverted() @ parent.inverted() @ quaternion
    bpy.context.view_layer.update()

def aim(name, rest_vector, vector):
    q = rest_vector.rotation_difference(vector) @ rig.data.bones[name].matrix_local.to_quaternion()
    orient(name, q)

def global_rotation(name, x=0, y=0, z=0):
    q = Quaternion((0,0,1),z) @ Quaternion((0,1,0),y) @ Quaternion((1,0,0),x)
    orient(name, q @ rig.data.bones[name].matrix_local.to_quaternion())

def translate_global(name, offset):
    pb = rig.pose.bones[name]
    mat = pb.matrix.copy()
    mat.translation += offset
    pb.matrix = mat
    bpy.context.view_layer.update()

leg_vectors = {}
for side in ('L','R'):
    names = ['足.'+side,'ひざ.'+side,'足首.'+side]
    heads = [rig.data.bones[n].head_local.copy() for n in names]
    leg_vectors[side] = (heads[1]-heads[0], heads[2]-heads[1])

max_target_error = 0

def leg(side, ankle, pitch):
    global max_target_error
    hip = rig.pose.bones['足.'+side].head.copy()
    av,bv = leg_vectors[side]
    a,b = av.length,bv.length
    v = ankle-hip
    d = v.length
    assert d < a+b, ('unreachable leg',side,d,a+b)
    axis = v.normalized()
    pole = Vector((0,-1,0))
    pole = (pole-axis*pole.dot(axis)).normalized()
    along = (a*a-b*b+d*d)/(2*d)
    knee = hip+axis*along+pole*math.sqrt(max(0,a*a-along*along))
    aim('足.'+side,av,knee-hip)
    aim('ひざ.'+side,bv,ankle-knee)
    global_rotation('足首.'+side,x=pitch,z=-.035 if side=='L' else .035)
    # Toe follows the foot during this low-stride study; no separate toe hinge.
    max_target_error = max(max_target_error,(rig.pose.bones['足首.'+side].head-ankle).length)

def foot(g, phase, side):
    duty = g['duty']
    travel = g['distance']*duty/SCALE
    def contact(u):
        pitch = curve([(0,-.13),(.18,0),(.65,0),(1,.46)],u)
        pivot = Vector((0, .10 + (-.34-.10)*smooth((u-.30)/.50), -.172))
        ground = Vector((.21 if side=='L' else -.21, -travel/2+travel*u+pivot.y, .00443))
        return ground-Matrix.Rotation(pitch,3,'X') @ pivot, pitch
    if phase <= duty:
        return contact(phase/duty)
    u = (phase-duty)/(1-duty)
    start,_ = contact(1)
    end,_ = contact(0)
    progress = curve([(0,0),(.3,.19),(.7,.83),(1,1)],u)
    target = start.lerp(end,progress)
    target.z += (g['lift']/SCALE)*math.sin(math.pi*u)**1.2
    pitch = curve([(0,.46),(.35,.24),(.75,-.22),(1,-.13)],u)
    return target,pitch

def pose(clip,phase):
    for pb in rig.pose.bones:
        pb.location = (0,0,0)
        pb.rotation_quaternion = Quaternion()
        pb.scale = (1,1,1)
    bpy.context.view_layer.update()
    moving = clip in GAITS
    g = GAITS.get(clip)
    wave = math.sin(math.tau*phase)
    if moving:
        # Contact compression followed by support rise, authored in source units.
        drop = (-.22-.16*math.cos(math.tau*2*phase)) if clip=='walk' else (-.30-.13*math.cos(math.tau*2*phase))
        shift = .035*math.sin(math.tau*phase-.6)
        targets = {s:foot(g,(phase+off)%1,s) for s,off in [('L',0),('R',.5)]}
    else:
        drop = -.045 + .006*wave
        shift = .014*math.sin(math.tau*phase)
        targets = {s:(Vector((.21 if s=='L' else -.21,.052,.176)),0) for s in ('L','R')}
    translate_global('センター',Vector((shift,0,drop)))
    # Lower pelvis just enough for strict, unscaled IK reach; never clamp ankles.
    extra_drop = 0
    for s,(target,pitch) in targets.items():
        hip = rig.pose.bones['足.'+s].head.copy()
        a,b = leg_vectors[s]
        reach = a.length+b.length-.018
        horizontal = Vector((target.x-hip.x,target.y-hip.y)).length_squared
        max_z = target.z+math.sqrt(max(0,reach*reach-horizontal))
        extra_drop = min(extra_drop,max_z-hip.z)
    if extra_drop<0:
        translate_global('センター',Vector((0,0,extra_drop)))
    for s,(target,pitch) in targets.items():
        leg(s,target,pitch)
    lean = g['lean'] if moving else .006
    # Forward is Blender -Y. Lead slightly from the upper torso, not the head.
    global_rotation('上半身',x=lean,z=.025*wave if moving else .004*wave)
    global_rotation('上半身2',x=lean*.65,z=-.025*wave if moving else -.003*wave)
    global_rotation('首',x=lean*.25,z=-.006*wave)
    global_rotation('頭',x=0,z=.004*wave)
    for side,sign in [('L',1),('R',-1)]:
        shoulder = rig.pose.bones['腕.'+side].head.copy()
        upper_rest = rig.data.bones['ひじ.'+side].head_local-rig.data.bones['腕.'+side].head_local
        fore_rest = rig.data.bones['手首.'+side].head_local-rig.data.bones['ひじ.'+side].head_local
        swing = (g['arm']*sign*math.cos(math.tau*phase)) if moving else .014*sign*wave
        bend = g['elbow'] if moving else .18
        up = Vector((sign*.21,math.sin(swing),-math.cos(swing))).normalized()
        # A light elbow bend places the hands forward, with no locked elbows.
        fore = Vector((sign*.08,math.sin(swing-bend),-math.cos(swing-bend))).normalized()
        aim('腕.'+side,upper_rest,up)
        aim('ひじ.'+side,fore_rest,fore)
        # Preserve wrist local rest; no independent wrist-flapping or broken palms.
        pb=rig.pose.bones['手首.'+side]
        pb.rotation_quaternion=Quaternion((1,0,0),.025)
    # Small delayed authored hair sway, not a physical simulation.
    for name in ['Bone.003.L','Bone.003.R','Bone.004.L','Bone.004.R','lone bone','Bone.002.R']:
        pb=rig.pose.bones[name]
        pb.rotation_quaternion=Quaternion((1,0,0),(.018 if moving else .004)*math.sin(math.tau*phase-.6))
    bpy.context.view_layer.update()

rig.animation_data_create()
actions=[]
for clip in ['idle','walk','run']:
    action=bpy.data.actions.new(clip)
    action.use_fake_user=True
    rig.animation_data.action=action
    for frame in range(0,61):
        scene.frame_set(frame)
        pose(clip,frame/60)
        for pb in rig.pose.bones:
            pb.keyframe_insert(data_path='location',frame=frame,group=pb.name)
            pb.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=pb.name)
    actions.append(action)
assert geometry_sha==digest_meshes(False),'Mesh or UV changed'
assert motion_skin_sha==digest_meshes(),'Unexpected skin changes after isolated skirt repair'
assert rests=={b.name:[list(r) for r in b.matrix_local] for b in rig.data.bones},'Bone rest changed'
rig.animation_data.action=actions[0]
scene.frame_set(0)
# Pack existing embedded image data into the new editable working file.
for image in bpy.data.images:
    if image.size[0]>0 and not image.packed_file:
        image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mutsumi_motion.blend'))
for obj in bpy.context.selected_objects:obj.select_set(False)
rig.select_set(True)
for obj in meshes:obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'mutsumi_motion.glb'),export_format='GLB',use_selection=True,
    export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False,
    export_force_sampling=True,export_frame_step=1,export_skins=True,export_morph=False,
    export_rest_position_armature=True,export_cameras=False,export_lights=False,export_extras=False)
assert source_sha==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
raw=(OUT/'mutsumi_motion.glb').read_bytes()
size,kind=struct.unpack_from('<I4s',raw,12)
gltf=json.loads(raw[20:20+size])
report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':source_sha,'source_unchanged':True,
        'autoexec_enabled':False,'mesh_uv_unchanged':True,'rest_unchanged':True,
        'source_mesh_skin_sha256':source_skin_sha,'motion_mesh_skin_sha256':motion_skin_sha,
        'skirt_reweighted_vertices':len(weight_changes),'skirt_weight_scope':skirt.name,
        'meshes':len(gltf['meshes']),'joint_counts':[len(s['joints']) for s in gltf['skins']],
        'clips':[a['name'] for a in gltf.get('animations',[])], 'fps':60,
        'cycle_seconds':1.0,'walk_reference_speed':1.25,'run_reference_speed':1.8,
        'walk_game_speed':1.25,'run_game_speed':2.8,
        'max_blender_ankle_target_error_source_units':max_target_error,
        'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
        'limits':['Original procedural animation study, not motion capture or final hand-polished animation',
                  'Skirt-only derived weights repair neutral-bone unweighted region; no physical skirt/hair simulation or terrain foot IK',
                  'Original simplified PBR preview materials retained, not author toon shader reproduction',
                  'All third-party/derived assets remain local, ignored, without confirmed release rights']}
# Reimport the actual GLB, audit clips and render representative real poses.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'mutsumi_motion.glb'))
scene=bpy.context.scene
scene.render.fps=FPS
rig=next(o for o in scene.objects if o.type=='ARMATURE')
mesh_objects=[o for o in scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)]
for obj in list(scene.objects):
    if obj != rig and obj not in mesh_objects:bpy.data.objects.remove(obj,do_unlink=True)
report['reimport_bones']=len(rig.data.bones)
report['reimport_meshes']=len(mesh_objects)
report['reimport_actions']=[a.name for a in bpy.data.actions]
report['preserved_bone_names']=len(set(rests)&set(rig.data.bones.keys()))
report['missing_bone_names']=sorted(set(rests)-set(rig.data.bones.keys()))
assert not report['missing_bone_names']
report['reimport_rest_matrix_max_abs_delta']=max(abs(x-y) for name in rests for old,new in zip(rests[name],rig.data.bones[name].matrix_local) for x,y in zip(old,new))
assert report['reimport_rest_matrix_max_abs_delta']<.0001
report['clip_time_ranges']={c['name']:[min(gltf['accessors'][s['input']]['min'][0] for s in c['samplers']),max(gltf['accessors'][s['input']]['max'][0] for s in c['samplers'])] for c in gltf['animations']}
report['gltf_triangles']=sum(gltf['accessors'][p['indices']]['count']//3 for mesh in gltf['meshes'] for p in mesh['primitives'])
report['body_faces_hidden']=False
report['material_count']=len(gltf['materials'])
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=512;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('MotionReviewWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.16,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
center=Vector((0,0,HEIGHT*.48))
for pos,power in [((-1.8,-2.1,2),220),((1.5,-1,1.3),110),((.5,1.4,2),250)]:
    data=bpy.data.lights.new('MotionReviewLight','AREA');data.energy=power*HEIGHT*HEIGHT/4;data.size=HEIGHT*1.5
    light=bpy.data.objects.new('MotionReviewLight',data);scene.collection.objects.link(light)
    light.location=center+Vector(pos)*HEIGHT;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('MotionReviewCamera');data.type='ORTHO';data.ortho_scale=HEIGHT*1.2
cam=bpy.data.objects.new('MotionReviewCamera',data);scene.collection.objects.link(cam);scene.camera=cam
for clip,angle,phases in [('idle',0,[0]),('walk',90,[0,.25,.5,.75]),('run',90,[0,.25,.5,.75]),('run',30,[.25])]:
    action=next(a for a in bpy.data.actions if a.name==clip or a.name.endswith('|'+clip))
    rig.animation_data.action=action
    if hasattr(action,'slots') and len(action.slots):rig.animation_data.action_slot=action.slots[0]
    for phase in phases:
        scene.frame_set(round(phase*60))
        bpy.context.view_layer.update()
        rad=math.radians(angle)
        cam.location=center+Vector((math.sin(rad)*3.2,-math.cos(rad)*3.2,.04))*HEIGHT
        cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(OUT/('%s_%03d_%02d.png'%(clip,angle,round(phase*100))))
        bpy.ops.render.render(write_still=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
print('MUTSUMI_MOTION_EXPORT_COMPLETE')
