"""Knight-only import policy, after the initial Godot import. No global config.
GLB images stay embedded; source PNGs generate real mipmaps for distant detail.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[2]/'assets/characters/ashen_knight'
for path in root.glob('*.glb.import'):
    path.write_text(path.read_text().replace('gltf/embedded_image_handling=1','gltf/embedded_image_handling=3'))
for path in (root/'textures').glob('*.png.import'):
    path.write_text(path.read_text().replace('mipmaps/generate=false','mipmaps/generate=true'))
print('Configured knight-only imports. Reimport with Godot.')
