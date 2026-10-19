"""Blender UV/material integration only; preserve meshes, rests and nine actions.

Run AFTER prepare_equipment_patterns.py and a Git checkpoint. Keeps original
UVs as PrePatternUV and updates both editable source and merged export parts.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Quaternion

BASE=Path(__file__).resolve().parents[2]/'assets/characters/reference_silhouette'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
rig=bpy.data.objects['WayfarerRig']
def vertex_digest():
    h=hashlib.sha256()
    for ob in sorted((o for o in bpy.data.objects if o.type=='MESH' and o.get('region')),key=lambda o:o.name):
        h.update(ob.name.encode())
        for v in ob.data.vertices:h.update(repr(tuple(v.co)).encode())
    return h.hexdigest()
before=vertex_digest();rests={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
actions={a.name for a in bpy.data.actions if a.use_fake_user}
tiles=json.loads((BASE/'source/art/pattern_manifest.json').read_text())
mats={}
metal_names={'steel','chest_front','chest_back','helmet','blade','brass'}
for name in tiles:
    key='Way_pattern_'+name
    mat=bpy.data.materials.get(key) or bpy.data.materials.new(key)
    mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
    nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');output=nodes.new('ShaderNodeOutputMaterial')
    links.new(bs.outputs['BSDF'],output.inputs['Surface'])
    for suffix,socket in [('albedo','Base Color'),('roughness','Roughness')]:
        path=BASE/'textures'/f'pattern_{name}_{suffix}.png'
        image=bpy.data.images.load(str(path),check_existing=True)
        if suffix=='roughness':image.colorspace_settings.name='Non-Color'
        image.pack()
        tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest'
        links.new(tex.outputs['Color'],bs.inputs[socket])
    bs.inputs['Metallic'].default_value=.55 if name in metal_names else 0
    bs.inputs['Roughness'].default_value=.63 if name in metal_names else .90
    mat.diffuse_color=(1,1,1,1);mats[name]=mat

usage={}
for ob in list(bpy.data.objects):
    if ob.type!='MESH' or not ob.get('region'):continue
    region=ob['region'];mesh=ob.data
    olduv=mesh.uv_layers.get('PrePatternUV')
    if olduv is None:
        olduv=mesh.uv_layers.new(name='PrePatternUV',do_init=True)
    uv=mesh.uv_layers['TailoredUV'];mesh.uv_layers.active=uv;uv.active_render=True
    if 'pre_pattern_material_names' not in mesh:
        mesh['pre_pattern_material_names']=[m.name for m in mesh.materials]
        mesh['pre_pattern_material_indices']=[int(p.material_index) for p in mesh.polygons]
    original_names=list(mesh['pre_pattern_material_names'])
    original_indices=list(mesh['pre_pattern_material_indices'])
    indices={}
    for face in mesh.polygons:
        kind=original_names[original_indices[face.index]].removeprefix('Way_')
        center=face.center
        name=None;mapping='original'
        if region=='chest':
            name='chest_front' if center.y>=0 else 'chest_back';mapping='chest'
            if center.z>1.47 or center.z<1.085:name='brass';mapping='original'
        elif region=='helmet':name='helmet';mapping='helmet'
        elif region=='shield':
            name='steel' if kind=='steel' else 'shield';mapping='shield'
        elif region=='sword':name='blade' if kind=='steel' else 'leather'
        elif kind=='linen':name='hem' if region=='tunic_hem' else 'linen'
        elif kind=='wool':name='scarf'
        elif kind=='leather':name='leather'
        elif kind=='bronze':name='brass'
        if name is None:continue
        if name not in indices:
            mesh.materials.append(mats[name]);indices[name]=len(mesh.materials)-1
        face.material_index=indices[name]
        usage[name]=usage.get(name,0)+1
        for li in face.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co
            u,v=olduv.data[li].uv
            u=(u-.02)/.96;v=(v-.02)/.96
            if mapping=='chest':u=.5+co.x/.42;v=(co.z-1.067)/.403
            elif mapping=='helmet':u=.5+co.x/.23;v=(co.z-1.61)/.215
            elif mapping=='shield':u=.5+(co.x+.252)/.39;v=(co.z-.625)/.50
            uv.data[li].uv=(.02+.96*max(0,min(1,u)),.02+.96*max(0,min(1,v)))
    # Remove unreferenced original slots so the imported material list is exact.
    used=sorted(set(p.material_index for p in mesh.polygons));newslots=[mesh.materials[i] for i in used]
    lookup={old:i for i,old in enumerate(used)};newids=[lookup[p.material_index] for p in mesh.polygons]
    mesh.materials.clear()
    for mat in newslots:mesh.materials.append(mat)
    for face,index in zip(mesh.polygons,newids):face.material_index=index
    ob['pattern_uv_status']='Purpose-mapped atlas tiles; original coordinates kept in PrePatternUV'

assert before==vertex_digest(),'Positions changed during a material-only update'
assert rests=={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
assert actions=={a.name for a in bpy.data.actions if a.use_fake_user}
rig.animation_data.action=bpy.data.actions['idle'];bpy.context.scene.frame_set(0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source/blender/wayfarer.blend'))
# Select only merged export surfaces, never editable duplicates or studio.
merged=[ob for ob in bpy.context.scene.objects if ob.type=='MESH' and '__' in ob.name and ob.get('region') and not any(c.name=='EDITABLE_SURFACES' for c in ob.users_collection)]
opts=dict(export_format='GLB',use_selection=True,export_yup=True,export_tangents=True,
 export_skins=True,export_materials='EXPORT',export_animation_mode='ACTIONS',
 export_frame_range=False,export_force_sampling=True,export_bake_animation=True,
 export_anim_single_armature=True,export_extras=True)
available=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def export(path,regions,animated,skin):
    bpy.ops.object.select_all(action='DESELECT')
    if skin:rig.select_set(True);bpy.context.view_layer.objects.active=rig
    gear=bpy.data.collections['TEST_EQUIPMENT_optional'];gear.hide_viewport=False
    for ob in merged:
        if ob['region'] in regions:ob.hide_set(False);ob.select_set(True)
    options=dict(opts,filepath=str(path),export_animations=animated)
    bpy.ops.export_scene.gltf(**{k:v for k,v in options.items() if k in available})
regions=set(ob['region'] for ob in merged)-{'chest','helmet','sword','shield'}
export(BASE/'wayfarer.glb',regions,True,True)
rig.animation_data.action=None
for pb in rig.pose.bones:pb.rotation_quaternion=Quaternion();pb.location=(0,0,0)
bpy.context.view_layer.update()
for name in ['chest','helmet','sword','shield']:export(BASE/'equipment'/f'{name}.glb',{name},False,name in ['chest','helmet'])
manifest_path=BASE/'source/build_manifest.json';manifest=json.loads(manifest_path.read_text())
manifest['patterns']={'tiles':len(tiles),'materials_used':sorted(usage),'positions_sha256':before,
 'rest_and_actions_unchanged':True,'uv_backup':'PrePatternUV',
 'source':'user supplied earlier generated atlases, authorized 2026-10-19',
 'normal_maps':'none; painted companion used only for broad roughness study'}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
print('PATTERN_BUILD',json.dumps(manifest['patterns']))
