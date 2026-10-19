"""Extract user-authorized atlas tiles for purpose-mapped character UVs.

Pillow: nearest 128px albedo from pixel art; broad roughness study from the
painted companion. No new image synthesis, no claimed high-poly PBR bake.
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
import json, hashlib

BASE=Path(__file__).resolve().parents[2]/'assets/characters/reference_silhouette'
source=BASE/'source/art';dest=BASE/'textures';dest.mkdir(exist_ok=True)
pixel=Image.open(source/'pixel_equipment_atlas.png').convert('RGB')
paint=Image.open(source/'painted_equipment_atlas.png').convert('RGB')
# row, column, optional inset crop in tile coordinates. Broad cloth/leather
# fields are used on small accessories; ornamented panels get distinct maps.
TILES={
 'linen':(2,0,(.05,.04,.95,.69)), 'hem':(2,0,(0,0,1,1)),
 'scarf':(2,2,(.025,.025,.975,.975)), 'leather':(3,0,(.22,.24,.78,.70)),
 'steel':(3,2,(.025,.025,.975,.975)),
 'chest_front':(0,0,(0,0,1,1)), 'chest_back':(0,1,(0,0,1,1)),
 'helmet':(0,2,(0,0,1,1)), 'shield':(1,2,(0,0,1,1)),
 'blade':(3,1,(.025,.025,.975,.975)), 'brass':(1,3,(.08,.24,.92,.76))}
def extract(image,row,col,box):
    step=image.width/4
    tile=image.crop((round(col*step)+3,round(row*step)+3,round((col+1)*step)-3,round((row+1)*step)-3))
    w,h=tile.size
    return tile.crop(tuple(round(x*n) for x,n in zip(box,[w,h,w,h])))
report={}
for name,(row,col,box) in TILES.items():
    im=extract(pixel,row,col,box).resize((128,128),Image.Resampling.NEAREST)
    im.save(dest/f'pattern_{name}_albedo.png')
    detail=ImageOps.grayscale(extract(paint,row,col,box)).resize((64,64),Image.Resampling.BOX).filter(ImageFilter.GaussianBlur(.7))
    center=.63 if name in {'steel','chest_front','chest_back','helmet','blade','brass'} else .90
    rough=detail.point(lambda x:max(0,min(255,round(center*255+(x-128)*.10)))).resize((128,128),Image.Resampling.NEAREST)
    rough.save(dest/f'pattern_{name}_roughness.png')
    report[name]={'atlas_tile':[row,col],'crop':box,'albedo_px':[128,128],
     'albedo_source':'pixel_equipment_atlas.png','roughness_source':'painted_equipment_atlas.png',
     'roughness_status':'broad value-derived study, not measured or baked',
     'sha256':hashlib.sha256((dest/f'pattern_{name}_albedo.png').read_bytes()).hexdigest()}
(source/'pattern_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('PATTERN_TILES',len(report),'albedo + roughness maps; nearest 128px')
