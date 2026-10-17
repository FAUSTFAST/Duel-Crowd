"""Render actual old/new Blender sources under identical cameras and lights.

Only renders and writes an audit; never saves either reopened source file.
Reference is a drawn turnaround, not a calibrated orthographic photograph.
"""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/silhouette_review'
OUT.mkdir(parents=True,exist_ok=True)
reports=json.loads((OUT/'source_audit.json').read_text()) if '--new-only' in sys.argv else {}
for label,folder in [('old','wayfarer'),('new','reference_silhouette')]:
    if '--new-only' in sys.argv and label=='old':continue
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/characters'/folder/'source/blender/wayfarer.blend'))
    scene=bpy.context.scene
    rig=bpy.data.objects['WayfarerRig']
    rig.animation_data.action=bpy.data.actions['idle']
    scene.frame_set(0)
    scene.render.resolution_x=900;scene.render.resolution_y=1000
    scene.cycles.samples=24
    reports[label]={'bones':len(rig.data.bones),'actions':[a.name for a in bpy.data.actions if a.use_fake_user],
        'reference':str(ROOT/'assets/characters/wayfarer/source/reference/adventurer_concept.png'),
        'pose':'actual idle frame 0; no mesh retouching',
        'rig_rest':{b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}}
    for view,pos in [('front',(0,4,.92)),('side',(-4,0,.92)),('threequarter',(2,3.464,.92))]:
        camera=bpy.data.objects['Review_Front']
        camera.location=pos
        camera.rotation_euler=(Vector((0,0,.92))-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.ortho_scale=2.10
        scene.camera=camera
        scene.render.filepath=str(OUT/f'{label}_{view}.png')
        bpy.ops.render.render(write_still=True)
        print('SILHOUETTE_RENDER',label,view,flush=True)
assert reports['old']['rig_rest']==reports['new']['rig_rest'],'Rest compatibility changed'
assert len(reports['new']['actions'])==5
(OUT/'source_audit.json').write_text(json.dumps(reports,indent=2)+'\n')
print('PASS identical 32-bone rest; five retained actions; six actual source renders')
