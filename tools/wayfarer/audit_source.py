"""Re-open saved Blender source: rig, editable parts, packing and skin weights."""
import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]/'assets/characters/wayfarer'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
rig=bpy.data.objects['WayfarerRig']
assert len(rig.data.bones)==32
actions=[a.name for a in bpy.data.actions if a.use_fake_user]
assert set(actions)=={'idle','walk','run','turn_left','turn_right'}
parts=list(bpy.data.collections['EDITABLE_SURFACES'].objects)
assert len(parts)>40 and all(ob.data.uv_layers.active.name=='TailoredUV' for ob in parts)
packed=[image for image in bpy.data.images if image.packed_file]
assert len(packed)==8
assert all(len(ob.vertex_groups)>0 for ob in parts if ob['region'] not in ('sword','shield'))
# Verify no bone scaling (equipment and skin must not squash or stretch).
for name in actions:
    rig.animation_data.action=bpy.data.actions[name]
    for frame in range(int(bpy.data.actions[name].frame_range[1])+1):
        bpy.context.scene.frame_set(frame)
        assert all(max(abs(v-1) for v in b.scale)<1e-5 for b in rig.pose.bones)
result={'source_reopen':'PASS','bones':32,'actions':actions,'editable_parts':len(parts),'packed_images':len(packed),'no_animated_bone_scaling':True}
(BASE/'source/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('SOURCE_AUDIT',json.dumps(result))
