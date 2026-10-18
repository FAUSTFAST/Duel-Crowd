"""Blender's bundled FFmpeg encodes actual frames; no new 3D render.

Blender --background --factory-startup --python-exit-code 1
        --python encode_motion_video.py -- FRAME_DIR OUTPUT.mp4
"""
import bpy,sys
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:]
assert len(args)==2,'Expected frame directory and MP4 output'
source=Path(args[0]);output=Path(args[1])
assert not output.exists(),'Save the existing review before overwriting'
assert len(list(source.glob('frame_*.png')))==360
scene=bpy.context.scene
scene.render.resolution_x=640;scene.render.resolution_y=360
scene.render.resolution_percentage=100
scene.render.fps=30;scene.frame_start=1;scene.frame_end=360
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='HIGH'
scene.render.filepath=str(output)
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
editor=scene.sequence_editor_create()
strip=editor.strips.new_image('Actual Godot frames',str(source/'frame_0000.png'),channel=1,frame_start=1)
for i in range(1,360):strip.elements.append('frame_%04d.png'%i)
scene.render.use_sequencer=True
bpy.ops.render.render(animation=True)
assert output.exists() and output.stat().st_size>10000
print('PASS MP4: 360 actual Godot frames, 30fps, 12s, 640x360; no synthesized motion.')
