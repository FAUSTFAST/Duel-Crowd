"""Re-author candidate actions only. Meshes, UVs, weights and bone rests stay intact.

Blender --background --factory-startup --python-exit-code 1 --python THIS
Requires a Git checkpoint; writes the candidate .blend, base GLB and manifest.
Original hand-designed contact curves, not motion capture or copied game clips.
"""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix

BASE=Path(__file__).resolve().parents[2]/'assets/characters/reference_silhouette'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
rig=bpy.data.objects['WayfarerRig']; scene=bpy.context.scene
FPS=60
def geometry_digest():
    h=hashlib.sha256()
    for ob in sorted((o for o in bpy.data.objects if o.type=='MESH' and o.get('region')),key=lambda o:o.name):
        h.update(ob.name.encode())
        for v in ob.data.vertices: h.update(repr(tuple(v.co)).encode())
        for uv in ob.data.uv_layers.active.data: h.update(repr(tuple(uv.uv)).encode())
    return h.hexdigest()
before=geometry_digest()
rests={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
rig.animation_data_clear(); rig.animation_data_create()
for action in list(bpy.data.actions): bpy.data.actions.remove(action)

def smooth(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def curve(points,x):
    for (a,va),(b,vb) in zip(points,points[1:]):
        if x<=b:return lerp(va,vb,smooth((x-a)/(b-a)))
    return points[-1][1]
def orient(name,q):
    pb=rig.pose.bones[name]
    local_rest=(pb.parent.bone.matrix_local.inverted()@pb.bone.matrix_local).to_quaternion() if pb.parent else pb.bone.matrix_local.to_quaternion()
    parent=pb.parent.matrix.to_quaternion() if pb.parent else Quaternion()
    pb.rotation_quaternion=local_rest.inverted()@parent.inverted()@q
    bpy.context.view_layer.update()
def direction(name,target):
    b=rig.data.bones[name]
    q=(b.tail_local-b.head_local).rotation_difference(Vector(target).normalized())@b.matrix_local.to_quaternion()
    orient(name,q)
def global_rot(name,x=0,y=0,z=0):
    q=Quaternion((0,0,1),z)@Quaternion((1,0,0),x)@Quaternion((0,1,0),y)
    orient(name,q@rig.data.bones[name].matrix_local.to_quaternion())
def leg(side,ankle,pitch=0,foot_yaw=0):
    hip=rig.pose.bones['Thigh_'+side].head.copy()
    a=rig.data.bones['Thigh_'+side].length; b=rig.data.bones['Shin_'+side].length
    v=ankle-hip; d=v.length
    assert d<a+b+.003,('unreachable ankle',side,d,a+b)
    d=min(d,a+b-.0005);axis=v.normalized()
    pole=Vector((0,1,0));pole=(pole-axis*pole.dot(axis)).normalized()
    along=(a*a-b*b+d*d)/(2*d)
    knee=hip+axis*along+pole*math.sqrt(max(0,a*a-along*along))
    direction('Thigh_'+side,knee-hip);direction('Shin_'+side,ankle-knee)
    global_rot('Foot_'+side,pitch,0,foot_yaw)
    global_rot('Toe_'+side,pitch*.65,0,foot_yaw)

# A heel strike, flat support, forefoot rocker, toe-off, recovery, next strike.
# During support the contact point moves backwards at exactly reference speed.
GAITS={
 'walk':dict(speed=1.8,period=.82,duty=.62,heel=.22,push=-.88,lift=.115,arm=.27,flex=.22,lean=.035),
 'jog':dict(speed=3.2,period=.72,duty=.43,heel=.255,push=-1.00,lift=.21,arm=.48,flex=.70,lean=.085),
 'run':dict(speed=4.6,period=.66,duty=.32,heel=.245,push=-1.08,lift=.29,arm=.67,flex=1.04,lean=.13)}
def foot(g,p,s):
    duty=g['duty'];travel=g['speed']*g['period']*duty
    def contact(u):
        roll=curve([(0,.24),(.17,0),(.60,0),(1,g['push'])],u)
        pivot=Vector((0,lerp(-.07,.20,smooth((u-.22)/.38)),-.105))
        ground=Vector((s*.115,g['heel']-travel*u+pivot.y+.07,0))
        ankle=ground-Matrix.Rotation(roll,3,'X')@pivot
        return ankle,roll
    if p<=duty:return contact(p/duty)
    u=(p-duty)/(1-duty);start,_=contact(1);end,_=contact(0)
    # Early knee recovery, then a controlled extension before heel contact.
    progress=curve([(0,0),(.32,.22),(.68,.77),(1,1)],u)
    ankle=start.lerp(end,progress)
    ankle.z+=g['lift']*math.sin(math.pi*u)**1.15
    roll=curve([(0,g['push']),(.35,-.55),(.73,.18),(1,.24)],u)
    return ankle,roll

def pose(gait,phase,intensity=1,settle=0,turn=0):
    for pb in rig.pose.bones:
        pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion();pb.location=(0,0,0);pb.scale=(1,1,1)
    g=GAITS.get(gait); moving=g is not None
    wave=math.sin(math.tau*phase)
    if moving:
        # Walk rises over the supporting leg; run compresses at impact then flies.
        if gait=='walk':height=.880+.036*math.sin(math.tau*phase)**2
        elif gait=='jog':height=.858+.050*math.sin(math.tau*phase)**2
        else:height=.838+.068*math.sin(math.tau*phase)**2
        side_shift=-.014*math.sin(math.tau*phase+1.0)
        lean=g['lean'];twist=.040*wave
    else:height=.919+.0015*math.sin(math.tau*phase);side_shift=.006;lean=.008;twist=.012
    height=lerp(.919,height,intensity)-settle
    # Keep both chains within their unchanged anatomical reach. This is a
    # pelvis translation, never bone scaling or a silently clamped foot target.
    if moving:
        for offset,s in [(0,-1),(.5,1)]:
            ankle,_=foot(g,(phase+offset)%1,s)
            idle=Vector((s*.127,.012 if s<0 else -.012,.105))
            ankle=idle.lerp(ankle,intensity)
            length=rig.data.bones['Thigh_L'].length+rig.data.bones['Shin_L'].length-.004
            horizontal=(ankle.x-(s*.103+side_shift*intensity))**2+ankle.y**2
            height=min(height,ankle.z+math.sqrt(max(.01,length*length-horizontal)))
    pelvis=rig.pose.bones['Pelvis']
    pelvis.location=(side_shift*intensity,height-.935,0)
    global_rot('Pelvis',-.015*intensity, .015*wave*intensity,twist*intensity)
    global_rot('Spine',-lean*intensity,0,-twist*.30*intensity+turn*.30)
    global_rot('Chest',-lean*.72*intensity,0,-twist*.75*intensity+turn*.65)
    global_rot('Neck',-lean*.25*intensity,0,turn*.8)
    global_rot('Head',0,0,turn)
    for side,offset,s in [('L',0,-1),('R',.5,1)]:
        p=(phase+offset)%1
        idle=Vector((s*.127,.012 if s<0 else -.012,.105))
        if moving:
            ankle,pitch=foot(g,p,s);ankle=idle.lerp(ankle,intensity);pitch*=intensity
        else:ankle,pitch=idle,0
        leg(side,ankle,pitch,s*.035*(1-intensity if moving else 1))
        # Contralateral arms. Elbow flex varies through the swing, no rigid fists.
        swing=(-1 if side=='L' else 1)*math.cos(math.tau*phase)* (g['arm'] if moving else .012)*intensity
        flex=(g['flex'] if moving else .13)+.07*math.sin(math.tau*p)
        flex=lerp(.13,flex,intensity)
        shoulder=rig.pose.bones['UpperArm_'+side].head.copy()
        upper=rig.data.bones['UpperArm_'+side].length
        vec=Vector((s*.045,math.sin(swing)*upper,-math.cos(swing)*upper)).normalized()*upper
        direction('UpperArm_'+side,vec)
        direction('Forearm_'+side,(s*.013,math.sin(swing+flex),-math.cos(swing+flex)))
        # Rest hand already slopes 10.5 degrees forward. Align the wrist to
        # its forearm rather than folding the palm backwards on the run swing.
        global_rot('Hand_'+side,swing+flex-math.atan2(.020,.108),0,-s*.035)
        for i,finger in enumerate(['Index','Middle','Ring','Little']):
            rig.pose.bones[finger+'_'+side].rotation_quaternion=Quaternion((1,0,0),-.20-i*.025)
    return height

clips=[('idle',2.8),('walk',1.0),('jog',1.0),('run',1.0),('start',.28),
       ('stop_left',.30),('stop_right',.30),('turn_left',.46),('turn_right',.46)]
metrics={}
for name,duration in clips:
    action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
    end=round(duration*FPS)
    for frame in range(end+1):
        t=frame/end
        if name in GAITS:pose(name,t)
        elif name=='idle':pose(None,t)
        elif name=='start':pose('walk',0,intensity=smooth(t),settle=.008*math.sin(math.pi*t))
        elif name.startswith('stop_'):
            # Settle over the current support leg; no root translation.
            phase=0 if name=='stop_left' else .5
            pose('walk',phase,intensity=1-smooth(t),settle=.008*math.sin(math.pi*t))
        else:
            sign=1 if name=='turn_left' else -1
            pose(None,t,turn=sign*.22*math.sin(math.pi*t))
            # A short lifting/replant step rather than pivoting both flat soles.
            for side,s in [('L',-1),('R',1)]:
                weight=math.sin(math.pi*t)**2 if (s<0)==(sign>0) else math.sin(math.pi*max(0,min(1,(t-.25)/.75)))**2
                leg(side,Vector((s*.127,.012*s,.105+.040*weight)),0,sign*.15*math.sin(math.pi*t))
        for pb in rig.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            if pb.name=='Pelvis':pb.keyframe_insert('location',frame=frame,group=pb.name)
    for fc in action.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    metrics[name]={'duration':end/FPS,'loop':name in ('idle','walk','jog','run')}
    if name in GAITS:metrics[name].update(GAITS[name])

assert before==geometry_digest(),'Animation-only revision must not alter mesh or UV'
assert rests=={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
rig.animation_data.action=bpy.data.actions['idle'];scene.frame_set(0);scene.render.fps=FPS
scene['motion_status']='Contact-authored in-place locomotion study; manual polish and terrain IK pending'
scene.render.fps=FPS
# Avoid accumulating Blender backup files in the asset source.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and '__' in ob.name and ob.get('region') not in {'chest','helmet','sword','shield'}:
        if any(c.name=='EDITABLE_SURFACES' for c in ob.users_collection):continue
        # Include the hidden underlying body too: runtime visibility owns it.
        ob.hide_set(False);ob.select_set(True)
opts=dict(filepath=str(BASE/'wayfarer.glb'),export_format='GLB',use_selection=True,
 export_yup=True,export_tangents=True,export_skins=True,export_materials='EXPORT',
 export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,
 export_bake_animation=True,export_anim_single_armature=True,export_extras=True)
available=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
bpy.ops.export_scene.gltf(**{k:v for k,v in opts.items() if k in available})
manifest_path=BASE/'source/build_manifest.json'
manifest=json.loads(manifest_path.read_text());manifest['actions']=metrics
manifest['locomotion_revision']={'method':'authored contact/roll/recovery curves; analytic two-bone bake',
 'geometry_uv_sha256':before,'rest_unchanged':True,'fps':FPS,
 'root_motion':False,'terrain_ik':False,'source':'tools/wayfarer/build_locomotion.py'}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
print('LOCOMOTION_BUILD',json.dumps({'clips':metrics,'geometry_unchanged':True,'rest_unchanged':True}))
