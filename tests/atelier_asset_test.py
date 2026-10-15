"""Validate actual GLB UV charts, skins, materials, and reusable animations.
Standard library only. Passing does not certify artistic quality.
"""
from pathlib import Path
import json, struct, math
root=Path(__file__).resolve().parents[1]
asset=root/'assets/characters/thorn_knight'
data=(asset/'thorn_knight.glb').read_bytes()
length=struct.unpack_from('<I',data,12)[0]
doc=json.loads(data[20:20+length]);buf=data[28+length:]
formats={5121:('B',1),5123:('H',2),5125:('I',4),5126:('f',4)}
dimensions={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def values(index):
    a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
    fmt,width=formats[a['componentType']];n=dimensions[a['type']]
    offset=v.get('byteOffset',0)+a.get('byteOffset',0);step=v.get('byteStride',width*n)
    return [struct.unpack_from('<'+fmt*n,buf,offset+i*step) for i in range(a['count'])]
assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==38
primitives=[p for m in doc['meshes'] for p in m['primitives']]
assert len(primitives)==5
assert {m['name'] for m in doc['materials']}=={'Thorn_'+n for n in ['steel','brass','cloth','mail','leather']}
vertices=triangles=blended=0;regions=set();max_error=0
for p in primitives:
    a=p['attributes']
    assert all(k in a for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0','JOINTS_0','WEIGHTS_0'])
    uv=values(a['TEXCOORD_0']);normals=values(a['NORMAL'])
    weights=values(a['WEIGHTS_0']);joints=values(a['JOINTS_0']);indices=values(p['indices'])
    vertices+=len(uv);triangles+=len(indices)//3
    for w,j,n in zip(weights,joints,normals):
        assert all(math.isfinite(x) and x>=0 for x in w)
        error=abs(sum(w)-1);max_error=max(max_error,error);assert error<.001
        assert all(0<=x<38 for x in j)
        assert abs(sum(x*x for x in n)-1)<.01
        blended+=sum(x>.001 for x in w)>1
    for u,v in uv:
        assert 0<u<1 and 0<v<1
        # UVs remain inside deliberately padded named atlas regions.
        assert .02<=(u*4)%1<=.98 and .02<=(v*4)%1<=.98
        regions.add((int(u*4),int(v*4)))
    for i in range(0,len(indices),3):
        charts={(int(uv[k[0]][0]*4),int(uv[k[0]][1]*4)) for k in indices[i:i+3]}
        assert len(charts)==1,'triangle crosses atlas tile boundary'
assert 10000<triangles<70000 and blended>200 and len(regions)==16
names={a['name'] for a in doc['animations']}
assert names=={'idle','walk','run','turn_left','turn_right'}
for animation in doc['animations']:
    for channel in animation['channels']:
        target=channel['target']
        if target['path']=='translation' and doc['nodes'][target['node']]['name']=='Root':
            positions=values(animation['samplers'][channel['sampler']]['output'])
            assert all(max(v[axis] for v in positions)-min(v[axis] for v in positions)<.0001 for axis in range(3))
assert (asset/'source/blender/thorn_knight.blend').read_bytes()[:7]==b'BLENDER'
assert '<svg' in (asset/'source/equipment_uv.svg').read_text()
for texture in ['equipment_albedo.png','equipment_roughness.png','fern_cutout.png']:
    path=asset/'textures'/texture
    assert path.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    assert 'mipmaps/generate=true' in path.with_suffix('.png.import').read_text()
manifest=json.loads((asset/'source/build_manifest.json').read_text())
assert manifest['triangles']==triangles
audit=json.loads((asset/'source/source_audit.json').read_text())
assert min(audit['flat_ground_blade_min_z'].values())>=.025
print(f'PASS ATELIER ASSET: {triangles} triangles, {vertices} vertices, 38 bones, 5 surfaces, '
      f'16 padded UV regions, {blended} blended vertices, max weight error {max_error:.8f}, 5 in-place clips.')
