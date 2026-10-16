"""Actual Blender source renders; does not modify the saved model or animations."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/characters/wayfarer/source/blender/wayfarer.blend'))
scene=bpy.context.scene
for name in ['Front','Side','Back','ThreeQuarter']:
    scene.camera=bpy.data.objects['Review_'+name]
    scene.render.filepath=str(root/'docs/adventurer_reference'/('blender_'+name.lower()+'.png'))
    bpy.ops.render.render(write_still=True)
    print('BLENDER_REVIEW',scene.render.filepath)
