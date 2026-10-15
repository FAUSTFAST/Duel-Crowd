"""Actual binary GLBs: anatomy is art-reviewed separately from these assertions."""
from pathlib import Path
import json,struct,math
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/characters/wayfarer'
class GLB:
    def __init__(self,path):
        raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
        self.doc=json.loads(raw[20:20+length]);self.buf=raw[28+length:]
    def values(self,index):
        a=self.doc['accessors'][index];v=self.doc['bufferViews'][a['bufferView']]
        fmt,width={5121:('B',1),5123:('H',2),5125:('I',4),5126:('f',4)}[a['componentType']]
        n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        offset=v.get('byteOffset',0)+a.get('byteOffset',0);step=v.get('byteStride',width*n)
        return [struct.unpack_from('<'+fmt*n,self.buf,offset+i*step) for i in range(a['count'])]
    def rig(self):
        skin=self.doc['skins'][0]
        return {self.doc['nodes'][n]['name']:pose for n,pose in zip(skin['joints'],self.values(skin['inverseBindMatrices']))}
base=GLB(BASE/'wayfarer.glb');doc=base.doc
assert len(doc['skins'])==1 and len(doc['skins'][0]['joints'])==32
assert {a['name'] for a in doc['animations']}=={'idle','walk','run','turn_left','turn_right'}
assert not any('steel' in mat['name'] or 'wood' in mat['name'] for mat in doc['materials'])
base_names={n['name'] for n in doc['nodes']}
assert not any(any(item in name.lower() for item in ['helmet','chestplate','sword','shield']) for name in base_names)
assert {'Head','Neck','Hand_L','Hand_R','Foot_L','Foot_R'}<=set(base.rig())
totals={};mixed=0
for asset_name,asset in [('base',base)]+[(n,GLB(BASE/'equipment'/f'{n}.glb')) for n in ['helmet','chest','sword','shield']]:
    tris=verts=0
    skinned=asset_name in ('base','helmet','chest')
    if skinned:
        assert set(asset.rig())==set(base.rig())
        for name,pose in asset.rig().items():
            assert max(abs(a-b) for a,b in zip(pose,base.rig()[name]))<.00001,'different bind rest'
    else:assert not asset.doc.get('skins')
    for mesh in asset.doc['meshes']:
        for p in mesh['primitives']:
            a=p['attributes'];assert all(k in a for k in ['POSITION','NORMAL','TANGENT','TEXCOORD_0'])
            pos=asset.values(a['POSITION']);uv=asset.values(a['TEXCOORD_0'])
            assert all(all(math.isfinite(v) for v in row) for row in pos)
            assert all(.019<u<.981 and .019<v<.981 for u,v in uv)
            assert all(abs(sum(x*x for x in n)-1)<.01 for n in asset.values(a['NORMAL']))
            indices=asset.values(p['indices']);assert len(indices)%3==0
            assert all(0<=i[0]<len(pos) for i in indices)
            verts+=len(pos);tris+=len(indices)//3
            if skinned:
                assert 'JOINTS_0' in a and 'WEIGHTS_0' in a
                for weights,joints in zip(asset.values(a['WEIGHTS_0']),asset.values(a['JOINTS_0'])):
                    assert abs(sum(weights)-1)<.0001 and all(v>=0 for v in weights)
                    assert all(0<=j<32 for j in joints)
                    if asset_name=='base':mixed+=sum(w>.001 for w in weights)>1
    totals[asset_name]={'triangles':tris,'vertices':verts}
assert mixed>200
for action in doc['animations']:
    for channel in action['channels']:
        if channel['target']['path']=='translation' and doc['nodes'][channel['target']['node']]['name']=='Root':
            values=base.values(action['samplers'][channel['sampler']]['output'])
            assert all(max(v[i] for v in values)-min(v[i] for v in values)<.0001 for i in range(3))
assert (BASE/'source/blender/wayfarer.blend').read_bytes()[:7]==b'BLENDER'
for texture in (BASE/'textures').glob('*.png'):
    assert struct.unpack_from('>II',texture.read_bytes(),16)==(128,128)
    assert 'mipmaps/generate=true' in texture.with_suffix('.png.import').read_text()
for import_file in BASE.rglob('*.glb.import'):
    assert 'gltf/embedded_image_handling=3' in import_file.read_text()
audit=json.loads((BASE/'source/source_audit.json').read_text())
assert audit['source_reopen']=='PASS' and audit['bones']==32 and audit['packed_images']==8
assert 6.8<audit['proportions']['head_units_excluding_hair']<7.3
assert audit['proportions']['connected_shirt_components']==audit['proportions']['connected_trousers_components']==1
print('PASS WAYFARER ASSETS',json.dumps(totals),'blended base vertices',mixed)
