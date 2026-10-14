"""Original pixel material tiles, deterministic and project-local. No external art.
These are drawn microdetails, not high-poly baked normals. Run with Pillow/numpy.
Only overwrites assets/characters/ashen_knight/textures; checkpoint edits first.
"""
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/characters/ashen_knight/textures'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(15102026)
for kind, base, rough in [('steel', (115, 135, 146), 158), ('bronze', (142, 109, 60), 174),
                         ('cloth', (90, 27, 44), 224), ('leather', (41, 33, 29), 232), ('mail', (64, 74, 81), 208)]:
    size = 128
    im = Image.new('RGB', (size, size), base)
    dr = ImageDraw.Draw(im)
    height = Image.new('L', (size, size), 128); hd = ImageDraw.Draw(height)
    for y in range(size):
        for x in range(size):
            n = random.choice([-7, -3, 0, 0, 3, 6])
            if kind == 'cloth': n += (3 if (x + y) % 3 == 0 else -2)
            if kind == 'leather': n += ((x * 13 + y * 17) % 5) - 2
            im.putpixel((x, y), tuple(max(0, min(255, c + n)) for c in base))
    if kind in ('steel', 'bronze'):
        # Chased edges, broken tooling lines and rivets are visible when mapped
        # around individual fitted armor panels, not world-space noise.
        bright = tuple(min(255, c + 38) for c in base)
        dark = tuple(max(0, c - 30) for c in base)
        for y in (3, 7, 119, 124):
            dr.line((0, y, 127, y), fill=bright if y in (3, 119) else dark)
            hd.line((0, y, 127, y), fill=155)
        for x in range(8, 128, 16):
            for y in (13, 114):
                dr.rectangle((x, y, x+2, y+2), fill=dark)
                dr.point((x, y), fill=bright); hd.rectangle((x, y, x+2, y+2), fill=165)
        for i in range(52):
            x, y = random.randrange(128), random.randrange(19, 106)
            dr.line((x, y, min(127, x+random.randint(1, 5)), y-1), fill=dark)
            hd.point((x, y), fill=110)
        for x in range(16, 124, 32):
            dr.line((x-5, 62, x, 53, x+5, 62, x, 71, x-5, 62), fill=dark, width=1)
            dr.point((x, 62), fill=bright)
    elif kind == 'mail':
        for y in range(0, 128, 6):
            for x in range((y//6 % 2)*3, 128, 6):
                dr.ellipse((x, y, x+4, y+4), outline=(123, 132, 134))
                dr.point((x+1, y+3), fill=(23, 30, 33))
                hd.ellipse((x, y, x+4, y+4), outline=168)
    elif kind == 'cloth':
        for x in (5, 10, 116, 121):
            dr.line((x, 0, x, 127), fill=(151, 91, 69)); hd.line((x, 0, x, 127), fill=147)
        for y in range(0, 128, 8):
            for x in (8, 119):
                dr.line((x-2, y, x, y+3, x+2, y), fill=(168, 111, 80))
    else:
        for y in range(0, 128, 8):
            dr.line((3, y, 5, y+2), fill=(125, 96, 69)); hd.line((3, y, 5, y+2), fill=155)
    im.save(OUT/f'{kind}_albedo.png')
    h = np.asarray(height, dtype=float)/255
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * .7
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * .7
    n = np.stack([-dx, -dy, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(np.uint8((n*.5+.5)*255)).save(OUT/f'{kind}_normal.png')
    Image.fromarray(np.uint8(np.clip(rough + (h-.5)*35, 0, 255))).save(OUT/f'{kind}_roughness.png')
print('Painted five original 128px material sets: albedo, shallow detail normal, roughness.')
