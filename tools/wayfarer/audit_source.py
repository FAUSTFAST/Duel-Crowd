"""Re-open saved Blender source: rig, editable parts, packing and skin weights."""
import bpy,json,sys
from pathlib import Path
STUDY='--silhouette-study' in sys.argv
BASE=Path(__file__).resolve().parents[2]/('assets/characters/reference_silhouette' if STUDY else 'assets/characters/wayfarer')
bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
rig=bpy.data.objects['WayfarerRig']
assert len(rig.data.bones)==32
actions=[a.name for a in bpy.data.actions if a.use_fake_user]
assert set(actions)=={'idle','walk','run','turn_left','turn_right'}
parts=list(bpy.data.collections['EDITABLE_SURFACES'].objects)
assert len(parts)>40 and all(ob.data.uv_layers.active.name=='TailoredUV' for ob in parts)
packed=[image for image in bpy.data.images if image.packed_file]
assert len(packed)==10
assert bpy.data.collections['TEST_EQUIPMENT_optional'].hide_viewport
assert bpy.data.collections['TEST_EQUIPMENT_optional'].hide_render
assert all(bpy.data.objects.get('Review_'+name) is not None for name in ['Front','Side','Back','ThreeQuarter'])
assert ((BASE.parent/'wayfarer' if STUDY else BASE)/'source/reference/adventurer_concept.png').exists()
assert all(len(ob.vertex_groups)>0 for ob in parts if ob['region'] not in ('sword','shield'))
def part(prefix):return next(ob for ob in parts if ob.name.startswith(prefix))
def bounds(ob):
    return [[min(v.co[i] for v in ob.data.vertices),max(v.co[i] for v in ob.data.vertices)] for i in range(3)]
def components(ob):
    adjacent=[set() for v in ob.data.vertices]
    for edge in ob.data.edges:
        a,b=edge.vertices;adjacent[a].add(b);adjacent[b].add(a)
    remaining=set(range(len(adjacent)));count=0
    while remaining:
        stack=[remaining.pop()];count+=1
        while stack:
            for i in adjacent[stack.pop()] & remaining:
                remaining.remove(i);stack.append(i)
    return count
head=bounds(part('SculptedHead'))
head_height=head[2][1]-head[2][0];head_width=head[0][1]-head[0][0]
head_units=head[2][1]/head_height
assert 6.8<head_units<7.3 and .175<head_width<(.205 if STUDY else .195)
assert components(part('TailoredShirtAndSleeves'))==1
assert components(part('TailoredTrousers'))==1
assert rig.data.bones['UpperArm_L'].length>rig.data.bones['Forearm_L'].length
assert abs(rig.data.bones['Thigh_L'].length-rig.data.bones['Thigh_R'].length)<1e-6
proportions={'head_height_m':head_height,'head_width_m':head_width,
 'head_units_excluding_hair':head_units,'connected_shirt_components':1,
 'connected_trousers_components':1,'note':'rest-geometry checks; not an art approval'}
# Verify no bone scaling (equipment and skin must not squash or stretch).
for name in actions:
    rig.animation_data.action=bpy.data.actions[name]
    for frame in range(int(bpy.data.actions[name].frame_range[1])+1):
        bpy.context.scene.frame_set(frame)
        assert all(max(abs(v-1) for v in b.scale)<1e-5 for b in rig.pose.bones)
result={'source_reopen':'PASS','bones':32,'actions':actions,'editable_parts':len(parts),'packed_images':len(packed),'no_animated_bone_scaling':True,'native_review_unarmored':True,'native_review_cameras':4,'proportions':proportions}
(BASE/'source/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('SOURCE_AUDIT',json.dumps(result))
