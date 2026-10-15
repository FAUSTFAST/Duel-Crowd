"""Only the independent atelier imports; never changes existing assets."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'assets/characters/thorn_knight'
for path in root.glob('*.glb.import'):
    path.write_text(path.read_text().replace('gltf/embedded_image_handling=1','gltf/embedded_image_handling=3'))
for path in (root/'textures').glob('*.png.import'):
    path.write_text(path.read_text().replace('mipmaps/generate=false','mipmaps/generate=true'))
print('Atelier-only import policy: embedded GLB textures, real PNG mipmaps.')
