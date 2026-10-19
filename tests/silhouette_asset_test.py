"""Binary candidate rig/skin/animation compatibility, not an art approval."""
from pathlib import Path
import runpy,math,json
ROOT=Path(__file__).resolve().parents[1]
# Reuse the existing GLB reader and run the unchanged baseline asset checks.
baseline=runpy.run_path(str(ROOT/'tests/wayfarer_asset_test.py'))
GLB=baseline['GLB'];old=baseline['base']
base=ROOT/'assets/characters/reference_silhouette'
new=GLB(base/'wayfarer.glb')
assert new.rig()==old.rig(), '32 rest matrices must stay exactly compatible'
assert {a['name'] for a in new.doc['animations']}=={'idle','walk','jog','run','start','stop_left','stop_right','turn_left','turn_right'}
assert not any(n['name'].startswith(('Review_','Studio')) for n in new.doc['nodes'])
assert not any('steel' in m['name'] or 'wood' in m['name'] for m in new.doc['materials'])
count=0
for label,asset in [('base',new)]+[(n,GLB(base/'equipment'/f'{n}.glb')) for n in ['helmet','chest']]:
    assert asset.rig()==new.rig()
    for mesh in asset.doc['meshes']:
        for p in mesh['primitives']:
            a=p['attributes']
            assert {'POSITION','NORMAL','TANGENT','TEXCOORD_0','JOINTS_0','WEIGHTS_0'}<=a.keys()
            assert all(all(math.isfinite(v) for v in row) for row in asset.values(a['POSITION']))
            for weights in asset.values(a['WEIGHTS_0']):
                assert abs(sum(weights)-1)<1e-4
            count+=len(asset.values(p['indices']))//3
for animation in new.doc['animations']:
    for channel in animation['channels']:
        values=new.values(animation['samplers'][channel['sampler']]['output'])
        assert all(all(math.isfinite(x) for x in row) for row in values)
        if channel['target']['path']=='scale':
            assert all(max(abs(x-1) for x in row)<1e-5 for row in values)
for p in base.rglob('*.glb.import'):
    assert 'skins/use_named_skins=true' in p.read_text()
for p in (base/'textures').glob('*.png.import'):
    assert 'mipmaps/generate=true' in p.read_text()
source_audit=json.loads((ROOT/'docs/silhouette_review/source_audit.json').read_text())
assert source_audit['new']['rig_rest']==source_audit['old']['rig_rest']
assert source_audit['new']['bones']==32 and len(source_audit['new']['actions'])==5
manifest=json.loads((base/'source/build_manifest.json').read_text())
assert manifest['locomotion_revision']['rest_unchanged'] and len(manifest['actions'])==9
assert 'animation/fps=60' in (base/'wayfarer.glb.import').read_text()
print('PASS SILHOUETTE: exact rest compatibility, weighted UV GLBs, finite 9 clips, no animated scale;',count,'base + 2 armor triangles. ART APPROVAL PENDING.')
