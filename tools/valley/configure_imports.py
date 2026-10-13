"""Project-local GLB and texture import policy. Run after the first editor import.
Only adjusts assets/valley sidecars; never changes global editor settings.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT/'assets/valley/models').glob('*.glb.import'):
    path.write_text(path.read_text().replace('gltf/embedded_image_handling=1', 'gltf/embedded_image_handling=3'))
for path in (ROOT/'assets/valley/textures').glob('*.png.import'):
    path.write_text(path.read_text().replace('mipmaps/generate=false','mipmaps/generate=true'))
print('Configured valley-only embedded GLB previews and texture mipmaps. Reimport in Godot.')
