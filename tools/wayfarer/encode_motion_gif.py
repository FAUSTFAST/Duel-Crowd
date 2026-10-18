"""Encode actual Godot PNG frames; no synthesized motion or artwork.

Uses Pillow from the bundled project runtime. 10fps preview of the first 10s;
one shared palette avoids frame-to-frame palette flicker. Refuses overwrite.
"""
from pathlib import Path
import sys
from PIL import Image

source=Path(sys.argv[1]);output=Path(sys.argv[2])
assert not output.exists(),'Save the existing review before overwriting'
paths=sorted(source.glob('frame_*.png'))
assert len(paths)==360,'Expected the complete 12 second 30fps recording'
samples=Image.new('RGB',(640,360))
for i,index in enumerate(range(0,300,20)):
    with Image.open(paths[index]) as frame:
        samples.paste(frame.convert('RGB').resize((160,90)),((i%4)*160,(i//4)*90))
palette=samples.quantize(colors=256)
frames=[]
for path in paths[:300:3]:
    with Image.open(path) as frame:
        frames.append(frame.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))
frames[0].save(output,save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=False)
with Image.open(output) as check:
    assert check.n_frames==100 and check.size==(640,360)
print('PASS actual Godot motion GIF: 100 frames, 10fps, 10s, 640x360')
