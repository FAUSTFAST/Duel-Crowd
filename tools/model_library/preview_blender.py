"""Isolated diagnostic GLB previews, not completed material/game adaptation.

The supplied GLB connects shadow/highlight maps to emission. The optional
clean-copy experiment does not recover missing albedo connections; its
colors are known to remain incorrect. Always preserve the downloaded source.
"""
from pathlib import Path
import json
import math
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "local_assets" / "bang_dream"
MODEL = LIBRARY / "models" / "mutsumi" / "还原睦.glb"
CLEAN = "--clean-copy" in sys.argv
LABEL = "mutsumi_prepared" if CLEAN else "mutsumi"
PREVIEW = LIBRARY / "previews" / LABEL
BLEND = LIBRARY / "reviews" / (LABEL + "_review.blend")
EXPORT = LIBRARY / "models" / "mutsumi" / "prepared" / "mutsumi_preview.glb"
if BLEND.exists() or PREVIEW.exists():
    raise RuntimeError("Review already exists; preserve manual edits and earlier previews before rebuilding")
PREVIEW.mkdir(parents=True)
BLEND.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(MODEL))
model_objects = list(bpy.context.scene.objects)
meshes = [o for o in model_objects if o.type == "MESH"]
armatures = [o for o in model_objects if o.type == "ARMATURE"]
excluded = []
if CLEAN:
    for obj in meshes:
        helper_material = any(slot.material and slot.material.name.startswith("mmd_tools_rigid_") for slot in obj.material_slots)
        unskinned_plane = obj.name == "平面" and not any(m.type == "ARMATURE" for m in obj.modifiers)
        if helper_material or unskinned_plane:
            obj.hide_render = True
            obj.hide_set(True)
            excluded.append(obj.name)
    meshes = [o for o in meshes if o.name not in excluded]
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        nodes = material.node_tree.nodes
        principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not principled:
            continue
        emission = principled.inputs.get("Emission Color")
        if emission and emission.is_linked:
            # The supplied glTF carries color maps in emission. Use those exact
            # image/UV outputs as lit base color in this separate review copy.
            color_output = emission.links[0].from_socket
            material.node_tree.links.new(color_output, principled.inputs["Base Color"])
            for link in list(emission.links):
                material.node_tree.links.remove(link)
            principled.inputs["Emission Color"].default_value = (0, 0, 0, 1)
            principled.inputs["Emission Strength"].default_value = 0
            principled.inputs["Metallic"].default_value = 0
            principled.inputs["Roughness"].default_value = 0.8
    # Selected export excludes rigid-body preview meshes and the supplied plane.
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in model_objects:
        if obj.name not in excluded:
            obj.select_set(True)
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    if EXPORT.exists():
        raise RuntimeError("Refusing to overwrite prepared GLB")
    bpy.ops.export_scene.gltf(filepath=str(EXPORT), export_format="GLB", use_selection=True, export_animations=False)
points = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (lo + hi) * 0.5
height = hi.z - lo.z
assert height > 0
images = [i for i in bpy.data.images if i.type == "IMAGE"]
assert all(i.size[0] > 0 and i.size[1] > 0 for i in images), "Missing image pixels"
report = {
    "blender_version": bpy.app.version_string,
    "source": str(MODEL.relative_to(ROOT)),
    "mesh_objects": len(meshes),
    "triangles": sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes),
    "armatures": len(armatures),
    "bones": [len(o.data.bones) for o in armatures],
    "actions": len(bpy.data.actions),
    "prepared_copy": CLEAN,
    "diagnostic_only": True,
    "material_colors_verified": False,
    "hidden_helper_objects": excluded,
    "images": [{"name": i.name, "size": list(i.size)} for i in images],
    "bounds": {"min": list(lo), "max": list(hi)},
    "limitations": ["Static import only; no locomotion, retargeting, physics or game license validation"],
}

studio = bpy.data.collections.new("LOCAL_REVIEW_STUDIO")
bpy.context.scene.collection.children.link(studio)


def studio_object(name, data):
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    return obj


def point_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


for name, offset, power, color in [
    ("Key", (-1.8, -2.1, 2.0), 850, (1.0, 0.92, 0.84)),
    ("Fill", (1.5, -1.0, 1.3), 550, (0.77, 0.86, 1.0)),
    ("Rim", (0.5, 1.4, 2.0), 900, (1.0, 0.92, 0.78)),
]:
    light_data = bpy.data.lights.new(name, "AREA")
    light_data.energy = power * height * height / 4
    light_data.color = color
    light_data.shape = "DISK"
    light_data.size = height * 1.5
    light = studio_object(name, light_data)
    light.location = center + Vector(offset) * height
    point_at(light, center)

camera_data = bpy.data.cameras.new("ReviewCamera")
camera_data.type = "ORTHO"
camera_data.ortho_scale = height * 1.3
camera_data.clip_end = max(1000, height * 30)
camera = studio_object("ReviewCamera", camera_data)
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.render.resolution_x = 512
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("NeutralReviewWorld")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.18, 0.21, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.5
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"

for name, angle in [("front", 0), ("threequarter", 35), ("back", 180)]:
    radians = math.radians(angle)
    camera.location = center + Vector((math.sin(radians) * 3.2, -math.cos(radians) * 3.2, 0.04)) * height
    point_at(camera, center)
    scene.render.filepath = str(PREVIEW / (name + ".png"))
    bpy.ops.render.render(write_still=True)

camera.location = center + Vector((1.8, -2.6, 0.15)) * height
point_at(camera, center)
for obj in bpy.context.selected_objects:
    obj.select_set(False)
if armatures:
    armatures[0].select_set(True)
    bpy.context.view_layer.objects.active = armatures[0]
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
report_path = LIBRARY / "reports" / ("blender_prepared.json" if CLEAN else "blender_import.json")
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False))
print("BLENDER_MODEL_REVIEW_COMPLETE")
