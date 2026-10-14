"""Validate exported GLB skin weights, UV/tangents and in-place animation.
Uses only Python's standard library. A zero exit code is not visual acceptance.
"""
import json, struct, math
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'assets/characters/ashen_knight/ashen_knight.glb'
data=p.read_bytes();size=struct.unpack_from('<I',data,12)[0]
j=json.loads(data[20:20+size]);start=20+size+8;buf=data[start:]
components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
types={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
def accessor(index):
    a=j['accessors'][index];view=j['bufferViews'][a['bufferView']]
    fmt,width=types[a['componentType']];num=components[a['type']]
    step=view.get('byteStride',num*width);off=view.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*num,buf,off+i*step) for i in range(a['count'])]
assert len(j['skins'])==1 and len(j['skins'][0]['joints'])==38
vertices=triangles=0;blended=0;max_error=0;surface_count=0
for mesh in j['meshes']:
    for prim in mesh['primitives']:
        surface_count+=1;a=prim['attributes']
        assert all(k in a for k in ('POSITION','NORMAL','TEXCOORD_0','TANGENT','JOINTS_0','WEIGHTS_0'))
        positions=accessor(a['POSITION']);weights=accessor(a['WEIGHTS_0']);joints=accessor(a['JOINTS_0'])
        assert len(positions)==len(weights)==len(joints)
        for w,b in zip(weights,joints):
            error=abs(sum(w)-1);max_error=max(max_error,error)
            assert error<.001 and all(v>=0 and math.isfinite(v) for v in w)
            assert all(0<=idx<38 for idx in b)
            blended+=sum(v>.001 for v in w)>1
        vertices+=len(positions);triangles+=len(accessor(prim['indices']))//3
assert surface_count==5 and blended>200
assert {a['name'] for a in j['animations']}=={'idle','walk','run','turn_left','turn_right'}
for animation in j['animations']:
    for channel in animation['channels']:
        if channel['target']['path']=='translation' and j['nodes'][channel['target']['node']]['name']=='Root':
            values=accessor(animation['samplers'][channel['sampler']]['output'])
            assert max(v[0] for v in values)-min(v[0] for v in values)<.0001
            assert max(v[2] for v in values)-min(v[2] for v in values)<.0001
            assert max(v[1] for v in values)-min(v[1] for v in values)<.0001
print(f'PASS GLB: 38 bones, 5 surfaces, {triangles} triangles, {vertices} vertices, {blended} blended vertices; maximum weight error {max_error:.8f}; 5 in-place clips.')
