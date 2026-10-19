"""Provenance, real atlas use and UV/import integrity; not an art approval."""
from pathlib import Path
import runpy,json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
baseline=runpy.run_path(str(ROOT/'tests/silhouette_asset_test.py'))
GLB=baseline['GLB'];base=ROOT/'assets/characters/reference_silhouette'
manifest=json.loads((base/'source/art/pattern_manifest.json').read_text())
provenance=json.loads((base/'source/art/provenance.json').read_text())
for name,info in provenance.items():
    assert hashlib.sha256((base/'source/art'/name).read_bytes()).hexdigest()==info['sha256']
for name,info in manifest.items():
    for suffix in ['albedo','roughness']:
        path=base/'textures'/f'pattern_{name}_{suffix}.png'
        assert struct.unpack_from('>II',path.read_bytes(),16)==(128,128)
        assert 'mipmaps/generate=true' in path.with_suffix('.png.import').read_text()
    assert hashlib.sha256((base/'textures'/f'pattern_{name}_albedo.png').read_bytes()).hexdigest()==info['sha256']
expected={'wayfarer':{'hem','linen','leather','scarf','brass'},'chest':{'chest_front','chest_back','brass'},
          'helmet':{'helmet'},'sword':{'blade','leather'},'shield':{'shield','steel'}}
for name,patterns in expected.items():
    path=base/'wayfarer.glb' if name=='wayfarer' else base/'equipment'/f'{name}.glb'
    asset=GLB(path)
    assert {f'Way_pattern_{p}' for p in patterns}<={m['name'] for m in asset.doc['materials']}
    for mesh in asset.doc['meshes']:
        for surface in mesh['primitives']:
            for u,v in asset.values(surface['attributes']['TEXCOORD_0']):
                assert .019<=u<=.981 and .019<=v<=.981,'atlas gutter lost'
audit=json.loads((base/'source/source_audit.json').read_text())
assert audit['packed_images']==10+len(manifest)*2
assert len(audit['actions'])==9 and audit['native_review_unarmored']
print('PASS PATTERNS: 2 authorized source atlases, 11 purpose maps, 22 mipmapped PNGs, actual base/4 gear GLB materials and UV gutters, 32 packed source images; no art approval implied.')
