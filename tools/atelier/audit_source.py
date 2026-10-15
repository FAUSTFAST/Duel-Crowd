"""Re-open the actual saved .blend, independently of the builder process."""
import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
base=root/'assets/characters/thorn_knight'
bpy.ops.wm.open_mainfile(filepath=str(base/'source/blender/thorn_knight.blend'))
rig=bpy.data.objects['ThornHumanoid']
actions=[a.name for a in bpy.data.actions if a.use_fake_user]
assert set(actions)=={'idle','walk','run','turn_left','turn_right'}
assert len(rig.data.bones)==38
parts=list(bpy.data.collections['EDITABLE_SURFACES'].objects)
assert len(parts)>40 and all(o.type=='MESH' and o.data.uv_layers for o in parts)
packed=[im.name for im in bpy.data.images if im.packed_file]
assert len(packed)==2
assert all(o.vertex_groups for o in parts)
collection=bpy.data.collections['EDITABLE_SURFACES']
collection.hide_viewport=False
blade=bpy.data.objects['DiamondSectionBlade']
blade_clearance={}
for name in ['idle','walk','run']:
    rig.animation_data.action=bpy.data.actions[name]
    minimum=10
    for frame in range(int(bpy.data.actions[name].frame_range[1])+1):
        bpy.context.scene.frame_set(frame)
        evaluated=blade.evaluated_get(bpy.context.evaluated_depsgraph_get())
        minimum=min(minimum,min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices))
    blade_clearance[name]=minimum
print('BLADE_CLEARANCE', json.dumps(blade_clearance), flush=True)
assert min(blade_clearance.values())>=.025, 'Sword intersects flat ground during locomotion'
result={'bones':38,'preserved_actions':actions,'editable_surface_patches':len(parts),
    'packed_images':packed,'atlas_uv':'EquipmentUV','source_reopen':'PASS',
    'flat_ground_blade_min_z':blade_clearance}
(base/'source/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('SOURCE_AUDIT',json.dumps(result))
