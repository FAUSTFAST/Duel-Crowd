"""Prepare original atlas for the valley GLB study. Never edits legacy textures.

Run with Python + Pillow + numpy. The AI source remains unmodified. Pixel-sized
sampling, periodic edge conditioning and luminance-derived detail maps are import
preparation, not a claim of scanned / physically measured PBR materials.
"""
from pathlib import Path
import json
import math
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets/valley/textures"
OUT.mkdir(parents=True, exist_ok=True)
source = Image.open(ROOT / "assets/valley/source/forest_material_atlas.png").convert("RGB")
w, h = source.size

for name, x, y in [("soil", 0, 0), ("slate", 1, 0), ("moss", 0, 1), ("bark", 1, 1)]:
    crop = source.crop((x*w//2, y*h//2, (x+1)*w//2, (y+1)*h//2))
    albedo = crop.resize((256, 256), Image.Resampling.BOX)
    a = np.asarray(albedo, dtype=np.float32)
    # Match opposite edges with a narrow smooth blend, preserve material centres.
    for axis in (0, 1):
        for i in range(12):
            weight = 0.5 * (1.0 - i / 12.0) ** 2
            if axis == 0:
                top, bottom = a[i].copy(), a[-1-i].copy()
                a[i] = top*(1-weight) + bottom*weight
                a[-1-i] = bottom*(1-weight) + top*weight
            else:
                left, right = a[:, i].copy(), a[:, -1-i].copy()
                a[:, i] = left*(1-weight) + right*weight
                a[:, -1-i] = right*(1-weight) + left*weight
    albedo = Image.fromarray(a.clip(0,255).astype("uint8")).quantize(colors=96, dither=Image.Dither.NONE).convert("RGB")
    albedo.save(OUT / f"{name}_albedo.png")
    a = np.asarray(albedo, dtype=np.float32) / 255.0
    height = a @ np.array([0.2126, 0.7152, 0.0722])
    # Estimated fine relief only; macro structure belongs to the actual mesh.
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * 1.6
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * 1.6
    normals = np.stack([-dx, -dy, np.ones_like(dx)], axis=2)
    normals /= np.linalg.norm(normals, axis=2, keepdims=True)
    Image.fromarray(((normals*0.5+0.5)*255).astype("uint8")).save(OUT / f"{name}_normal.png")
    rough = np.clip(0.88 - height*0.16 + (0.03 if name == "bark" else 0), .62, .96)
    Image.fromarray((rough*255).astype("uint8")).save(OUT / f"{name}_roughness.png")

# Original leaf/spray drawing, with transparent gaps and visible branching.
leaf = Image.new("RGBA", (128, 128))
draw = ImageDraw.Draw(leaf)
draw.line([(63, 122), (66, 69), (62, 12)], fill=(70,64,35,255), width=3)
for i in range(9):
    side = -1 if i % 2 else 1
    base = (64, 20+i*10)
    tip = (64+side*(22+i%3*5), 8+i*10)
    mid = ((base[0]+tip[0])/2, (base[1]+tip[1])/2)
    color = [(84,102,52,255), (105,116,62,255), (64,85,45,255)][i%3]
    draw.polygon([base, (mid[0]-side*5, mid[1]-6), tip, (mid[0]+side*5, mid[1]+6)], fill=color)
    draw.line([base,tip], fill=(131,135,78,255), width=1)
leaf.save(OUT / "leaf_spray.png")

# Cloth and worked metal for the articulated knight study, locally authored.
for name in ("steel", "cloth", "leather"):
    im = Image.new("RGB", (128,128))
    pix = im.load()
    for y in range(128):
        for x in range(128):
            grain = math.sin(x*.21)*.025 + math.cos(y*.31+x*.13)*.018
            if name == "steel":
                v = .8 + grain + .08*math.sin(x*math.pi/64)
                col = (v*.88, v*.94, v)
            elif name == "cloth":
                v = .8 + grain + .08*math.sin(x*math.pi/32)
                col = (v*.46, v*.14, v*.19)
            else:
                v = .8 + grain
                col = (v*.29, v*.20, v*.13)
            pix[x,y] = tuple(int(min(1,max(0,c))*255) for c in col)
    im.save(OUT / f"{name}_albedo.png")

manifest = {"source": "forest_material_atlas.png", "method": "built-in imagegen original atlas + authored import preparation", "working_albedo": "256px / 96 colours", "normal": "estimated from albedo luminance; not measured or baked high-poly", "external_assets": False}
(ROOT / "assets/valley/source/material_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")
print("Prepared valley-only original texture maps:", OUT)
