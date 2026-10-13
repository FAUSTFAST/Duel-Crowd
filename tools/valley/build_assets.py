"""Original forest-valley Blender study. Blender 4.5, metres, GLB Y-up.
Run: Blender --background --factory-startup --python tools/valley/build_assets.py
Generated study assets are revisable source art, not final commercial assets.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
from mathutils import noise

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/valley/models'
TEX = ROOT / 'assets/valley/textures'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(8102026)


def material(name, kind=None, color=(1,1,1,1), metallic=0, roughness=.86, leaf=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=roughness; bs.inputs['Metallic'].default_value=metallic
    if kind:
        suffix = '' if leaf else '_albedo'
        im = bpy.data.images.load(str(TEX / f'{kind}{suffix}.png'), check_existing=True)
        tex = m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=im; tex.interpolation='Closest'
        m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
        if leaf:
            m.node_tree.links.new(tex.outputs['Alpha'], bs.inputs['Alpha'])
            m.surface_render_method='DITHERED'; m.use_backface_culling=False
        for channel in ('normal','roughness'):
            path = TEX / f'{kind}_{channel}.png'
            if not path.exists(): continue
            node = m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=bpy.data.images.load(str(path),check_existing=True)
            node.image.colorspace_settings.name='Non-Color'
            if channel=='normal':
                normal=m.node_tree.nodes.new('ShaderNodeNormalMap'); normal.inputs['Strength'].default_value=.45
                m.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']); m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
            else: m.node_tree.links.new(node.outputs['Color'],bs.inputs['Roughness'])
    return m

SOIL=material('ValleySoil','soil'); BARK=material('ValleyBark','bark'); ROCK=material('ValleySlate','slate')
LEAF=material('ValleyLeaf','leaf_spray',leaf=True)
GRASS=material('ValleyGrass',color=(.21,.31,.12,1)); FLOWER=material('ValleyFlower',color=(.6,.56,.73,1))
STEEL=material('StudySteel','steel',metallic=.38,roughness=.64)
DARK=material('StudyLeather','leather',metallic=0,roughness=.9)
CLOTH=material('StudyCloth','cloth'); CLOTH.use_backface_culling=False
BRASS=material('StudyBrass',color=(.43,.32,.12,1),metallic=.5,roughness=.63)


def empty(name, parent=None, location=(0,0,0)):
    obj=bpy.data.objects.new(name,None); bpy.context.collection.objects.link(obj); obj.parent=parent; obj.location=location
    return obj


def mesh_obj(name, verts, faces, mat, uvs=None, colors=None, parent=None, smooth=True):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.parent=parent
    mesh.materials.append(mat)
    for p in mesh.polygons: p.use_smooth=smooth
    if uvs:
        layer=mesh.uv_layers.new(name='UVMap')
        for loop in mesh.loops: layer.data[loop.index].uv=uvs[loop.vertex_index]
    else:
        bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=.9,island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT')
    if colors:
        layer=mesh.color_attributes.new(name='TerrainMix',type='FLOAT_COLOR',domain='POINT')
        for i,c in enumerate(colors): layer.data[i].color=c
    return obj


def tube(name, points, radii, mat, parent, sides=16, grooves=.06):
    pts=[Vector(p) for p in points]; verts=[]; uv=[]; faces=[]; distance=0
    for row,p in enumerate(pts):
        tangent=(pts[min(row+1,len(pts)-1)]-pts[max(0,row-1)]).normalized()
        ref=Vector((1,0,0)) if abs(tangent.z)>.8 else Vector((0,0,1))
        u=tangent.cross(ref).normalized(); v=tangent.cross(u).normalized()
        if row: distance+=(pts[row]-pts[row-1]).length
        for i in range(sides+1):
            a=i*math.tau/sides
            radius=radii[row]*(1+grooves*math.sin(a*7+p.z*2)+grooves*.5*math.cos(a*11-p.z))
            verts.append(tuple(p+radius*(u*math.cos(a)+v*math.sin(a))))
            uv.append((i/sides*math.tau*radii[0]*.5,distance*.5))
        if row:
            for i in range(sides):
                n=row*(sides+1)+i; prev=n-(sides+1); faces.append((prev,prev+1,n+1,n))
    faces.append(tuple(reversed(range(sides)))); faces.append(tuple((len(pts)-1)*(sides+1)+i for i in range(sides)))
    return mesh_obj(name,verts,faces,mat,uv,parent=parent)


def join(objects,name,parent):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]; bpy.ops.object.join()
    result=objects[0]; result.name=name; result.parent=parent; return result


def export(root, filename):
    # Explicit triangles ensure the exported tangent basis exists on capped tubes.
    for obj in root.children_recursive:
        if obj.type != 'MESH': continue
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('ExportTriangles','TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for obj in root.children_recursive: obj.select_set(True)
    opts=dict(filepath=str(OUT/filename),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_tangents=True,export_materials='EXPORT')
    props=bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
    if 'export_all_vertex_colors' in props: opts['export_all_vertex_colors']=True
    bpy.ops.export_scene.gltf(**opts)
    print('EXPORTED',filename)


def path_x(z): return math.sin(z*.22)*1.25-.3

def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a))); return t*t*(3-2*t)

def height(x,z):
    d=abs(x-path_x(z)); ridge=smooth(1.55,8.2,d)
    base=.25+.024*(12-z)+.35*math.sin(z*.23)
    macro=ridge*(4.4+1.1*math.sin(z*.31+x*.14))
    detail=(.12*math.sin(x*1.7+z*.54)+.08*math.cos(z*1.1-x*.38))*(.3+ridge)
    return base+macro+detail+smooth(12,18,-z)*2.8


def terrain():
    root=empty('ValleyTerrainAsset'); verts=[];uv=[];cols=[];faces=[];heights=[]
    width,depth,step=61,81,.4
    for iz in range(depth):
        z=-18+iz*step
        for ix in range(width):
            x=-12+ix*step; h=height(x,z); verts.append((x,-z,h)); uv.append((x*.28,-z*.28)); heights.append(h)
            slope=math.hypot((height(x+.1,z)-height(x-.1,z))/.2,(height(x,z+.1)-height(x,z-.1))/.2)
            rock=smooth(.55,1.0,slope)*.9
            moss=smooth(1.0,2.5,abs(x-path_x(z)))*(1-rock)*(.68+.24*math.sin(x*.3+z*.7)**2)
            cols.append((moss,rock,0,1))
    for iz in range(depth-1):
        for ix in range(width-1):
            a=iz*width+ix;b=a+1;c=a+width+1;d=a+width
            # Blender XY: -z coordinates reverse winding versus Godot ground.
            faces.extend([(a,c,b),(a,d,c)])
    mesh_obj('TerrainSurface',verts,faces,SOIL,uv,cols,root)
    # glTF only emits an active colour attribute referenced by its material.
    mix = SOIL.node_tree.nodes.new('ShaderNodeVertexColor'); mix.layer_name='TerrainMix'
    SOIL.node_tree.links.new(mix.outputs['Color'],SOIL.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    data={'width':width,'depth':depth,'step':step,'min_x':-12,'min_z':-18,'heights':heights,'path':[[path_x(z),height(path_x(z),z),z] for z in [10,8,6,4,2,0,-2,-4,-6,-8,-10,-12,-14]]}
    (ROOT/'assets/valley/source/heightfield.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    resource='[gd_resource type="Resource" load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://scripts/valley/valley_heightfield.gd" id="1"]\n\n[resource]\nscript = ExtResource("1")\n'
    for key in ('width','depth','step','min_x','min_z'): resource+=f'{key} = {data[key]}\n'
    resource+='heights = PackedFloat32Array('+','.join(f'{h:.7f}' for h in heights)+')\n'
    resource+='path = PackedVector3Array('+','.join(f'{v:.7f}' for p in data['path'] for v in p)+')\n'
    (ROOT/'assets/valley/source/heightfield.tres').write_text(resource)
    return root


def rock(seed):
    rng=random.Random(seed); root=empty(f'StratifiedRock{seed}'); verts=[];faces=[]
    sides=24; levels=[0,.13,.38,.64,.9,1.12,1.36,1.55]
    for row,h in enumerate(levels):
        for i in range(sides):
            a=i*math.tau/sides
            # Unequal erosion planes and taper; narrow seams instead of tiered discs.
            profile=1.2-.18*h-.23*smooth(.8,1.55,h)
            r=profile*(1+.21*math.sin(a*3+seed)+.09*math.cos(a*5+seed*.8))
            seam=.018*math.sin(h*25+a*2)
            warped_h=h+(h/1.55)*(.14*math.sin(a*2+seed)+.08*math.cos(a*5))
            p=Vector((math.cos(a)*(r+seam)+h*.17,math.sin(a)*(r+seam)*.75,warped_h))
            p+=Vector((.055,.045,.035))*noise.noise_vector(p*2.3)
            verts.append(tuple(p))
        if row:
            for i in range(sides):
                a=(row-1)*sides+i;b=(row-1)*sides+(i+1)%sides;c=row*sides+(i+1)%sides;d=row*sides+i
                faces.append((a,b,c,d))
    verts.append((.22,0,1.65)); tip=len(verts)-1
    for i in range(sides): faces.append(((len(levels)-1)*sides+i,(len(levels)-1)*sides+(i+1)%sides,tip))
    faces.append(tuple(reversed(range(sides))))
    obj=mesh_obj('SlateErosion',verts,faces,ROCK,parent=root,smooth=True)
    mod=obj.modifiers.new('SmallWeatheredEdges','BEVEL');mod.width=.035;mod.segments=2;mod.limit_method='ANGLE';mod.angle_limit=.6
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    return root


def tree(seed):
    rng=random.Random(seed);root=empty(f'ForestOak{seed}');bark=[]
    pts=[(0,0,0),(.04,.06,.35),(-.1,.02,1.1),(.12,-.04,2.1),(.2,.1,3.2),(.08,.12,4.5),(.25,.2,5.5)]
    bark.append(tube('Trunk',pts,[.56,.42,.31,.26,.22,.14,.035],BARK,root,24,.12))
    for i in range(7):
        a=i*math.tau/7
        bark.append(tube('Root',[(0,0,.38),(.6*math.cos(a),.6*math.sin(a),.12),(1.2*math.cos(a),1.2*math.sin(a),.015)],[.2,.12,.025],BARK,root,12,.09))
    foliage=[]
    for i in range(11):
        a=i*2.4+seed;z=2.4+(i%4)*.65
        tip=Vector((math.cos(a)*(1.5+(i%3)*.25),math.sin(a)*(1.3+(i%2)*.3),z+1.0))
        base=Vector((.12,0,z)); mid=base.lerp(tip,.6)-Vector((0,0,.23))
        bark.append(tube('Limb',[base,mid,tip],[.14,.09,.025],BARK,root,14,.07))
        for j in range(3):
            a2=a+(j-1)*.6; twig=tip+Vector((math.cos(a2)*.72,math.sin(a2)*.72,.35+j*.15))
            bark.append(tube('Twig',[mid,tip,twig],[.06,.035,.006],BARK,root,8,.04))
            foliage.append(twig)
    join(bark,'OakBark',root)
    verts=[];faces=[];uv=[]
    for center in foliage:
        for j in range(9):
            p=center+Vector((rng.uniform(-.6,.6),rng.uniform(-.6,.6),rng.uniform(-.2,.48)))
            a=rng.uniform(0,math.tau);u=Vector((math.cos(a),math.sin(a),rng.uniform(-.25,.25))).normalized()
            v=Vector((-u.y,u.x,rng.uniform(.7,1.3))).normalized(); span=rng.uniform(.58,.94)
            n=len(verts)
            for point,coord in zip([p-u*span/2-v*span/2,p+u*span/2-v*span/2,p+u*span/2+v*span/2,p-u*span/2+v*span/2],[(0,0),(1,0),(1,1),(0,1)]):
                verts.append(tuple(point));uv.append(coord)
            faces.append((n,n+1,n+2,n+3))
    mesh_obj('OakFoliage',verts,faces,LEAF,uv,parent=root,smooth=False)
    return root


def grass_patch(seed=21, flowers=False):
    rng=random.Random(seed);root=empty('FlowerPatch' if flowers else 'GrassPatch');verts=[];faces=[];uv=[]
    for i in range(70 if not flowers else 18):
        a=rng.random()*math.tau;r=rng.random()**.5*.6;x,y=math.cos(a)*r,math.sin(a)*r
        h=rng.uniform(.18,.54);w=rng.uniform(.018,.035)
        u=Vector((math.cos(a),math.sin(a),0));p=Vector((x,y,0));n=len(verts)
        for point,coord in zip([p-u*w,p+u*w,p+u*w*.7+Vector((.04,.02,h*.55)),p+Vector((.09,.03,h)),p-u*w*.7+Vector((.04,.02,h*.55))],[(0,0),(1,0),(1,.6),(.5,1),(0,.6)]):
            verts.append(tuple(point));uv.append(coord)
        faces.extend([(n,n+1,n+2,n+4),(n+4,n+2,n+3)])
        if flowers:
            for petal in range(5):
                a=petal*math.tau/5; center=Vector((x+.09,y+.03,h)); p2=center+Vector((math.cos(a)*.065,math.sin(a)*.065,.025))
                n=len(verts);verts.extend([tuple(center),tuple(p2+Vector((-.025,0,0))),tuple(p2+Vector((.025,0,0)))]);uv.extend([(0,0),(1,0),(.5,1)]);faces.append((n,n+1,n+2))
    obj=mesh_obj('FlowerBlades' if flowers else 'GrassBlades',verts,faces,GRASS,uv,parent=root,smooth=False)
    if flowers:
        obj.data.materials.append(FLOWER)
        # Each stalk produces two green polygons followed by five petals.
        for i,p in enumerate(obj.data.polygons):
            if i%7>=2:p.material_index=1
    return root


def shrub(seed=31):
    rng=random.Random(seed); root=empty('ForestBramble'); verts=[];uv=[];faces=[]
    for i in range(9):
        a=i*2.4; tip=Vector((.6*math.cos(a),.6*math.sin(a),rng.uniform(.45,.8)))
        tube('BrambleBranch',[(0,0,0),tuple(tip*.45),tuple(tip)],[.04,.02,.003],BARK,root,8,.06)
        for j in range(4):
            center=tip*(.42+j*.18); u=Vector((math.cos(a),math.sin(a),.45)).normalized()*.28
            v=Vector((-math.sin(a),math.cos(a),.6)).normalized()*.27
            n=len(verts)
            verts.extend([tuple(center-u-v),tuple(center+u-v),tuple(center+u+v),tuple(center-u+v)])
            uv.extend([(0,0),(1,0),(1,1),(0,1)]);faces.append((n,n+1,n+2,n+3))
    bark=[o for o in root.children if o.type=='MESH']
    join(bark,'BrambleWood',root)
    mesh_obj('BrambleLeaves',verts,faces,LEAF,uv,parent=root,smooth=False)
    return root


def armour_piece(name,rings,mat,parent,sides=20):
    # Elliptical anatomical cross sections, real UVs and rounded plate surfaces.
    verts=[];uv=[];faces=[]
    for row,(rx,ry,z) in enumerate(rings):
        for i in range(sides+1):
            a=i*math.tau/sides; verts.append((math.cos(a)*rx,math.sin(a)*ry,z));uv.append((i/sides,row/(len(rings)-1)))
        if row:
            for i in range(sides):
                n=row*(sides+1)+i;p=n-sides-1;faces.append((p,p+1,n+1,n))
    faces.extend([tuple(reversed(range(sides))),tuple((len(rings)-1)*(sides+1)+i for i in range(sides))])
    return mesh_obj(name,verts,faces,mat,uv,parent=parent)


def knight():
    root=empty('ValleyKnightVisual'); torso=empty('Torso',root)
    armour_piece('Cuirass',[(.22,.14,.91),(.28,.19,1.07),(.3,.21,1.3),(.26,.17,1.43),(.19,.13,1.48)],STEEL,torso)
    armour_piece('Fauld',[(.32,.21,.75),(.31,.2,.84),(.26,.16,1.02)],STEEL,torso)
    for z in [.81,.88,.95]: armour_piece('PlateRim',[(.315,.208,z),(.31,.202,z+.024)],BRASS,torso)
    armour_piece('Gorget',[(.23,.16,1.4),(.2,.14,1.5),(.16,.12,1.54)],BRASS,torso)
    armour_piece('HelmetShell',[(.18,.16,1.54),(.215,.19,1.66),(.217,.2,1.78),(.18,.17,1.9),(.055,.06,1.96)],STEEL,torso,24)
    # Recessed horizontal visor and projecting brow follow the helmet curvature.
    verts=[(-.185,.152,1.715),(-.08,.205,1.715),(.08,.205,1.715),(.185,.152,1.715),(-.185,.152,1.75),(-.08,.208,1.75),(.08,.208,1.75),(.185,.152,1.75)]
    mesh_obj('Visor',verts,[(0,1,5,4),(1,2,6,5),(2,3,7,6)],DARK,parent=torso,smooth=False)
    tube('HelmetRidge',[(0,-.16,1.82),(0,-.02,1.967),(0,.13,1.88)],[.018,.022,.012],BRASS,torso,8,0)
    tube('NasalGuard',[(0,.211,1.8),(0,.213,1.65)],[.018,.014],BRASS,torso,8,0)
    # Folded cloth has actual shape and UV seams, not a flat red box.
    verts=[];faces=[];uv=[]
    for row in range(7):
        t=row/6;z=1.46-t*.97
        for i in range(9):
            x=(i/8-.5)*(.45+t*.28);y=-.2-t*.2+math.sin(i*math.pi/2)*(.025+t*.035)
            verts.append((x,y,z+(0.03*math.sin(i*1.7) if row==6 else 0)));uv.append((i/8,t))
            if row and i:
                n=row*9+i;faces.append((n-10,n-9,n,n-1))
    mesh_obj('FoldedCape',verts,faces,CLOTH,uv,parent=torso)
    for side in (-1,1):
        leg=empty('LeftLeg' if side==-1 else 'RightLeg',root,(side*.145,0,.83))
        armour_piece('Greave',[(.09,.09,-.69),(.11,.12,-.5),(.105,.1,-.31),(.125,.12,-.25),(.105,.105,-.12),(.12,.12,0)],STEEL,leg,16)
        armour_piece('Boot',[(.105,.17,-.8),(.115,.18,-.69),(.09,.11,-.59)],DARK,leg,16)
        arm=empty('LeftArm' if side==-1 else 'RightArm',root,(side*.36,0,1.43))
        armour_piece('ArmPlate',[(.085,.08,-.52),(.1,.1,-.37),(.105,.105,-.22),(.1,.095,-.11),(.205,.21,.02),(.18,.18,.12),(.06,.065,.19)],STEEL,arm,18)
        armour_piece('ShoulderRim',[(.203,.208,-.015),(.21,.216,.014)],BRASS,arm,18)
        if side==-1:
            verts=[(0,.15,-.8),(-.24,.15,-.49),(-.27,.12,-.04),(-.17,.17,.1),(.17,.17,.1),(.27,.12,-.04),(.24,.15,-.49),(0,.23,-.2)]
            obj=mesh_obj('KiteShield',verts,[(7,i,(i+1)%7) for i in range(7)],CLOTH,parent=arm,smooth=False)
            for i in range(7): tube('ShieldRim',[verts[i],verts[(i+1)%7]],[.024,.024],BRASS,arm,8,0)
            tube('ShieldSigil',[(0,.235,-.55),(0,.245,-.02)],[.018,.018],BRASS,arm,8,0)
            tube('ShieldSigil', [(-.13,.244,-.19),(.13,.244,-.19)],[.017,.017],BRASS,arm,8,0)
    return root

assets=[(terrain(),'valley_terrain.glb'),(rock(3),'slate_a.glb'),(rock(7),'slate_b.glb'),(tree(3),'oak_a.glb'),(tree(8),'oak_b.glb'),(shrub(),'shrub.glb'),(grass_patch(),'grass_patch.glb'),(grass_patch(13,True),'flower_patch.glb'),(knight(),'knight_study.glb')]
for root,name in assets: export(root,name)
# Preserve a native source library with modules arranged for inspection.
for i,(root,name) in enumerate(assets[1:]):root.location=(i%4*7,10+i//4*8,0)
(ROOT/'assets/valley/source/blender').mkdir(parents=True,exist_ok=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/valley/source/blender/valley_studies.blend'))
manifest={'blender_version':bpy.app.version_string,'assets':[],'status':'original scripted Blender visual study, not hand-sculpted production art'}
for root,name in assets:
    objects=[o for o in root.children_recursive if o.type=='MESH']
    manifest['assets'].append({'file':name,'vertices':sum(len(o.data.vertices) for o in objects),'polygons':sum(len(o.data.polygons) for o in objects)})
(ROOT/'assets/valley/source/model_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('VALLEY_BUILD_COMPLETE',manifest)
