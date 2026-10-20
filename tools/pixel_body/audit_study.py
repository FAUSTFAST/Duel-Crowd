"""Reopen the saved stage-2 source and static GLB, audit and render old reference.

No production files are saved. This is not a binding/deformation acceptance test.
"""
import bpy
import bmesh
import json
import sys
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'assets/characters/pixel_adventurer_v3'
OUT=ROOT/'docs/pixel_body_study/v3'
blend=BASE/'source/blender/adventurer_blockout.blend'
bpy.ops.wm.open_mainfile(filepath=str(blend))
model=bpy.data.collections['PIXEL_BODY_STAGE_2']
meshes=list(model.objects)
def topology(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    remaining=set(bm.verts);components=0
    while remaining:
        todo=[remaining.pop()];components+=1
        while todo:
            v=todo.pop()
            for e in v.link_edges:
                q=e.other_vert(v)
                if q in remaining:remaining.remove(q);todo.append(q)
    result={'components':components,'boundary_edges':sum(e.is_boundary for e in bm.edges),
        'nonmanifold_internal_edges':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),
        'degenerate_faces':sum(f.calc_area()<1e-10 for f in bm.faces),
        'loose_vertices':sum(not v.link_faces for v in bm.verts),
        'quads':sum(len(f.verts)==4 for f in bm.faces),'faces':len(bm.faces)}
    bm.free();return result
report={'source':str(blend.relative_to(ROOT)),'status':'stage-2 geometry/export audit; not art approval',
    'armatures':sum(o.type=='ARMATURE' for o in bpy.data.objects),'actions':len(bpy.data.actions),
    'objects':{o.name:topology(o) for o in meshes},'blender':bpy.app.version_string}
assert report['armatures']==0 and report['actions']==0
assert all(x['degenerate_faces']==0 and x['loose_vertices']==0 for x in report['objects'].values())
for name in ['HeadNeck_continuous','Tunic_shoulders_sleeves_CONTINUOUS',
             'Trousers_seat_crotch_legs_CONTINUOUS','Forearm_hand_-1','Forearm_hand_1']:
    assert report['objects'][name]['components']==1,name
    assert report['objects'][name]['nonmanifold_internal_edges']==0,name
source_tri=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes)
coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
report['bounds_m']=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
report['source_triangles']=source_tri
report['source_mesh_objects']=len(meshes)
report['palette_materials_used']=sorted({m.name for o in meshes for m in o.data.materials})

# Import exported GLB into a separate empty scene, checking actual content.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(BASE/'adventurer_blockout.glb'))
objects=list(bpy.context.scene.objects)
assert all(o.type in {'MESH','EMPTY'} for o in objects),'Studio/rig leaked into export'
loaded=[o for o in objects if o.type=='MESH']
assert len(loaded)==report['source_mesh_objects']
tri=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in loaded)
assert tri==source_tri
assert not any('Review_' in o.name or 'reference' in o.name.lower() for o in objects)
report['glb_import']={'mesh_objects':len(loaded),'triangles':tri,'cameras_lights_rigs':0}

# Actual previous source, under exactly the same review cameras and lights.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/characters/reference_silhouette/source/blender/wayfarer.blend'))
scene=bpy.context.scene
rig=bpy.data.objects.get('WayfarerRig')
rig.animation_data.action=bpy.data.actions['idle'];scene.frame_set(0)
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'} or o.name=='StudioFloor':bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(blend),link=False) as (data_from,data_to):
    data_to.collections=['REVIEW_STUDIO_EXCLUDED_FROM_GLB']
    data_to.worlds=['NeutralReview']
scene.collection.children.link(data_to.collections[0]);scene.world=data_to.worlds[0]
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG'
scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
for view in ['front','side','threequarter']:
    scene.camera=bpy.data.objects['Review_'+view]
    for label,w,h in [('native',640,800),('pixel96',78,96)]:
        scene.render.resolution_x=w;scene.render.resolution_y=h
        scene.render.filepath=str(OUT/f'before_{view}_{label}.png')
        bpy.ops.render.render(write_still=True)
        print('RENDER_PREVIOUS_SAME_CAMERA',view,label,flush=True)
report['before_comparison']='Previous source idle frame 0, identical cameras/lights/world/color management; no mesh retouch or rescale.'
report['not_tested']=['Skinning','joint deformation','slope IK','Godot gameplay/performance','final UVs','sprite export animation']
(OUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS REOPEN SOURCE CONNECTIVITY AND GLB ROUNDTRIP; SIX PREVIOUS RENDERS',flush=True)
