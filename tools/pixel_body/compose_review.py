"""Arrange actual Blender renders; no repaint, filtering or generative images."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/pixel_body_study/v3'
BG=(35,46,50)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(size): return ImageFont.truetype(FONT,size)
def paste(canvas,source,box,nearest=False):
    im=Image.open(source).convert('RGBA')
    scale=min(box[2]/im.width,box[3]/im.height)
    size=(round(im.width*scale),round(im.height*scale))
    im=im.resize(size,Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS)
    canvas.paste(im,(box[0]+(box[2]-size[0])//2,box[1]+(box[3]-size[1])//2),im)
def canvas(w,h,title,subtitle):
    im=Image.new('RGB',(w,h),BG);d=ImageDraw.Draw(im)
    d.text((26,18),title,font=font(25),fill=(237,225,202))
    d.text((26,54),subtitle,font=font(15),fill=(175,191,193))
    return im
views=['front','side','threequarter']
board=canvas(1200,640,'PIXEL ADVENTURER / STAGE 2 / v3',
    'Actual Blender renders | silhouette candidate | unarmed | no rig or animation')
d=ImageDraw.Draw(board)
for i,v in enumerate(views):
    paste(board,OUT/f'{v}_native.png',(i*400,95,400,510))
    d.text((i*400+145,610),v.upper(),font=font(16),fill='white')
board.save(OUT/'review_board.png')
board=canvas(1080,1040,'LOW-RESOLUTION READABILITY / v3',
    'Direct low-resolution Blender renders, nearest-neighbor enlargement; labels are canvas height')
d=ImageDraw.Draw(board);measure={}
for row,h in enumerate([64,96,128]):
    for col,v in enumerate(views):
        p=OUT/f'{v}_pixel{h}.png';im=Image.open(p).convert('RGBA')
        alpha=im.getchannel('A').point(lambda x:255 if x>=128 else 0)
        bounds=alpha.getbbox();role_h=bounds[3]-bounds[1]
        measure[f'{v}_{h}']={'canvas':list(im.size),'alpha_50pct_bbox':list(bounds),'role_height_px':role_h}
        # Integer enlargement only; never stretch one axis independently.
        multiplier=4 if h==64 else 3 if h==96 else 2
        size=(im.width*multiplier,im.height*multiplier)
        bigger=im.resize(size,Image.Resampling.NEAREST)
        x=col*360+(360-size[0])//2;y=110+row*300+(280-size[1])//2
        board.paste(bigger,(x,y),bigger)
        d.text((col*360+62,92+row*300),f'{v} | canvas {h}px | role {role_h}px',font=font(14),fill='white')
board.save(OUT/'pixel_board.png')
board=canvas(1200,690,'PREVIOUS SOURCE vs PIXEL SILHOUETTE CANDIDATE',
    'Same orthographic cameras, lighting and world; previous idle frame 0 / new neutral modelling pose')
d=ImageDraw.Draw(board)
for i,v in enumerate(['front','threequarter']):
    for k,previous in enumerate([True,False]):
        x=i*600+k*300
        path=OUT/(f'before_{v}_native.png' if previous else f'{v}_native.png')
        paste(board,path,(x,115,300,515))
        d.text((x+75,95),('PREVIOUS' if previous else 'NEW v3')+' / '+v,font=font(15),fill='white')
d.text((26,656),'Arrangement only: no model retouch, recoloring or non-uniform scaling.',font=font(14),fill=(175,191,193))
board.save(OUT/'before_after.png')
(OUT/'pixel_measurements.json').write_text(json.dumps(measure,indent=2)+'\n')
print('PASS THREE REVIEW BOARDS from actual PNG renders; integer pixel enlargement')
