"""Finish the editable Blender delivery after exporting gameplay GLBs.

Reference image is supplied by the user; not our original concept art. Studio
objects and reference empties never enter the GLB exports. Default view is the
unarmored figure, with gear in a separate disabled viewport/render collection.
"""
import bpy,math
from mathutils import Vector

def setup(base,rig,merged):
    scene=bpy.context.scene
    gear=bpy.data.collections.new('TEST_EQUIPMENT_optional');scene.collection.children.link(gear)
    for ob in merged:
        if ob['region'] in {'helmet','chest','sword','shield'}:
            for col in list(ob.users_collection):col.objects.unlink(ob)
            gear.objects.link(ob)
    gear.hide_viewport=True;gear.hide_render=True
    for ob in merged:
        if ob['region']=='body_under_cloth':ob.hide_set(True);ob.hide_render=True
    studio=bpy.data.collections.new('REVIEW_STUDIO_not_exported');scene.collection.children.link(studio)
    def move(ob):
        for c in list(ob.users_collection):c.objects.unlink(ob)
        studio.objects.link(ob)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006))
    floor=bpy.context.object;floor.name='StudioFloor';move(floor)
    mat=bpy.data.materials.new('StudioNeutral');mat.diffuse_color=(.11,.13,.14,1)
    mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.11,.13,.14,1);bs.inputs['Roughness'].default_value=.9
    floor.data.materials.append(mat)
    for name,position,energy,size,color in [
        ('Key',(3,4,5),400,4,(1,.88,.75)),('Fill',(-3,2,3),260,3,(.72,.84,1)),
        ('Rim',(1,-3,4),500,3,(1,.78,.55))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
        ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=position
        ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
    for name,location in [('Front',(0,4,.92)),('Side',(-4,0,.92)),('Back',(0,-4,.92)),('ThreeQuarter',(2,4,1.2))]:
        data=bpy.data.cameras.new('Review_'+name);data.type='ORTHO';data.ortho_scale=2.14
        ob=bpy.data.objects.new('Review_'+name,data);studio.objects.link(ob);ob.location=location
        ob.rotation_euler=(Vector((0,0,.92))-ob.location).to_track_quat('-Z','Y').to_euler()
        if name=='ThreeQuarter':scene.camera=ob
    reference=bpy.data.collections.new('USER_REFERENCE_not_exported');scene.collection.children.link(reference)
    reference.hide_render=True
    img=bpy.data.images.load(str(base/'source/reference/adventurer_concept.png'),check_existing=True)
    img.filepath='//../reference/adventurer_concept.png'
    ob=bpy.data.objects.new('User supplied turnaround — reference only',None)
    reference.objects.link(ob);ob.empty_display_type='IMAGE';ob.data=img
    ob.empty_display_size=3.5;ob.location=(-2.3,0,1.0);ob.rotation_euler=(math.pi/2,0,0)
    ob['provenance']='User-provided concept sheet. Reference, not generated 3D evidence.'
    rig.animation_data.action=bpy.data.actions['idle'];scene.frame_set(0)
    scene.render.engine='CYCLES';scene.cycles.samples=32
    scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.world.color=(.16,.16,.16)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.shading.type='MATERIAL'
                area.spaces.active.region_3d.view_location=(0,0,.94)
                area.spaces.active.region_3d.view_distance=3.0
                area.spaces.active.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
                area.spaces.active.clip_end=100
    scene['asset_status']='Reference-guided model candidate. Manual art review still required.'
    bpy.ops.wm.save_as_mainfile(filepath=str(base/'source/blender/wayfarer.blend'))
