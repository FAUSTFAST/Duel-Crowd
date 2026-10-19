"""Only this new candidate's sidecars; preserve all old asset imports."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]/('assets/characters/reference_silhouette' if '--silhouette-study' in sys.argv else 'assets/characters/wayfarer')
for path in root.rglob('*.glb.import'):
    text=path.read_text().replace('gltf/embedded_image_handling=1','gltf/embedded_image_handling=3')
    if '--silhouette-study' in sys.argv and path.name=='wayfarer.glb.import':
        text=text.replace('animation/fps=30','animation/fps=60')
    path.write_text(text.replace('skins/use_named_skins=false','skins/use_named_skins=true'))
for path in (root/'textures').glob('*.png.import'):
    path.write_text(path.read_text().replace('mipmaps/generate=false','mipmaps/generate=true'))
print(root.name+': named skin binds, embedded maps, nearest+mip import policy.')
