"""Make a local, simplified material/pose copy of the collected Mutsumi source.

Run Blender with --background --disable-autoexec --python-exit-code 1. Never
executes source Text blocks or saves the downloaded .blend. Output stays in the
ignored library. This is a static map display, not a rig/animation adaptation or
faithful port of the author's Shader-to-RGB materials.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import sys

import bpy
import numpy as np
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "local_assets/bang_dream"
SOURCE = LIBRARY / "source/mutsumi/01doing.blend"
args = argparse.ArgumentParser()
args.add_argument("--output", default="models/mutsumi/map_preview_v2")
options = args.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
OUT = (LIBRARY / options.output).resolve()
assert OUT.is_relative_to(LIBRARY.resolve()), "Output must stay in ignored local library"
if OUT.exists():
    raise RuntimeError("Refusing to overwrite an existing preview; choose a new --output")
OUT.mkdir(parents=True)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False)
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.file.find_missing_files(directory=str(SOURCE.parent / "textures"))
scene = bpy.context.scene
source_frame = scene.frame_current
source_actions = len(bpy.data.actions)
rigs = [o for o in scene.objects if o.type == "ARMATURE"]
assert len(rigs) == 1
rig = rigs[0]
rest = {b.name: list(map(list, b.matrix_local)) for b in rig.data.bones}
meshes = [o for o in scene.objects if o.type == "MESH" and not o.hide_render and o.name != "body.003"
          and any(m.type == "ARMATURE" and m.object == rig for m in o.modifiers)
          and not any(s.material and s.material.name.startswith("mmd_tools_") for s in o.material_slots)]
assert len(meshes) > 5
for obj in list(scene.objects):
    if obj not in meshes and obj != rig:
        obj.hide_render = True
        obj.hide_set(True)
for obj in meshes:
    # Source outlines, physics and smoothing helpers cannot be exported as
    # functional Godot effects. Remove them in memory in the derived copy only.
    for modifier in list(obj.modifiers):
        if modifier.name.startswith("OH_OUTLINE") or modifier.type in {"CLOTH", "COLLISION", "CORRECTIVE_SMOOTH", "NODES"}:
            obj.modifiers.remove(modifier)
        elif modifier.type == "SUBSURF":
            modifier.levels = min(1, modifier.levels)
            modifier.render_levels = min(1, modifier.render_levels)

textures = {}
def local_image(filename, label, tint=(1, 1, 1, 1)):
    key = (filename, label)
    if key in textures:
        return textures[key]
    src = bpy.data.images.load(str(SOURCE.parent / "textures" / filename), check_existing=False)
    image = src.copy()
    image.name = "LocalPreview_" + label
    image.scale(1024, 1024)
    if tint != (1, 1, 1, 1):
        pixels = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(pixels)
        pixels = pixels.reshape(-1, 4)
        pixels *= np.array(tint, dtype=np.float32)
        image.pixels.foreach_set(pixels.reshape(-1))
        image.update()
    image.filepath_raw = str(OUT / (label + ".png"))
    image.file_format = "PNG"
    image.save()
    textures[key] = image
    return image

material_mapping = []
created = {}
def replacement(original):
    if original.name in created:
        return created[original.name]
    name = original.name
    image = None
    note = "original albedo, resized to 1024"
    if any(x in name.lower() for x in ["clothes", "dress", "shoes", "kouzi", "white"]):
        image = local_image("mutsmi_clothes.png", "uniform")
    elif "hair" in name:
        # Source hair map is almost white. This local olive/sage factor derives
        # from the source Mix.007 highlight palette, approximating a lit midtone.
        # It does not recreate the source ramp/AO/Shader-to-RGB network.
        image = local_image("mutsmi_hair.001.png", "hair_sage_approx", (.58, .66, .44, 1))
        note = "approximate source palette tint; author toon lighting not reproduced"
    elif any(x in name.lower() for x in ["eye", "face", "body", "socks"]):
        tint = (1, 1, 1, 1)
        if "face" in name or "body" in name:
            tint = (1, .88, .84, 1)
        image = local_image("mutsmi_body_pants - 副本.png", "skin" if tint != (1, 1, 1, 1) else "eyes_socks", tint)
        note = "original colored face/eye/body atlas; skin-only material has mild warm tint"
    mat = bpy.data.materials.new("MapPreview_" + name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = .85
    bsdf.inputs["Metallic"].default_value = 0
    bsdf.inputs["Specular IOR Level"].default_value = .1
    if image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Linear"
        mat.node_tree.links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (.02, .02, .025, 1)
        note = "unused source outline fallback"
    created[name] = mat
    material_mapping.append({"source": name, "preview": mat.name, "albedo": image.name if image else None, "note": note})
    return mat

for obj in meshes:
    for slot in obj.material_slots:
        if slot.material:
            slot.material = replacement(slot.material)

# One constant frame stores the source display pose without editing rest bones.
# This is explicitly NOT locomotion, idle animation, retargeting or physics.
rig.animation_data_create()
action = bpy.data.actions.new("source_display_pose")
rig.animation_data.action = action
for bone in rig.pose.bones:
    for path in ("location", "rotation_quaternion", "rotation_euler", "scale"):
        bone.keyframe_insert(data_path=path, frame=source_frame, group=bone.name)
scene.frame_start = source_frame
scene.frame_end = source_frame
bpy.context.view_layer.update()
assert rest == {b.name: list(map(list, b.matrix_local)) for b in rig.data.bones}

for obj in bpy.context.selected_objects:
    obj.select_set(False)
rig.hide_set(False)
rig.select_set(True)
for obj in meshes:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
glb_path = OUT / "mutsumi_map.glb"
bpy.ops.export_scene.gltf(
    filepath=str(glb_path), export_format="GLB", use_selection=True,
    export_animations=True, export_animation_mode="ACTIVE_ACTIONS",
    export_nla_strips_merged_animation_name="source_display_pose",
    export_force_sampling=True, export_frame_range=True,
    export_current_frame=True, export_rest_position_armature=True,
    export_apply=True, export_morph=False, export_skins=True,
    export_cameras=False, export_lights=False, export_extras=False,
)
assert source_hash == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
raw = glb_path.read_bytes()
chunk_size, kind = struct.unpack_from("<I4s", raw, 12)
gltf = json.loads(raw[20:20+chunk_size])
report = {
    "source": str(SOURCE.relative_to(ROOT)), "source_sha256": source_hash,
    "source_unchanged": True, "source_actions": source_actions,
    "autoexec_enabled": bpy.context.preferences.filepaths.use_scripts_auto_execute,
    "preview_kind": "local static map display only",
    "native_mesh_objects": [o.name for o in meshes],
    "excluded_duplicate_body": "body.003 (second overlapping lower body; retained body.001 full body)",
    "native_bones": len(rig.data.bones), "rest_matrices_unchanged_before_export": True,
    "gltf_mesh_resources": len(gltf.get("meshes", [])),
    "gltf_joints": [len(s["joints"]) for s in gltf.get("skins", [])],
    "gltf_animations": [a.get("name") for a in gltf.get("animations", [])],
    "gltf_triangles": sum(gltf["accessors"][p["indices"]]["count"]//3 for m in gltf.get("meshes", []) for p in m["primitives"]),
    "material_mapping": material_mapping,
    "glb_sha256": hashlib.sha256(raw).hexdigest(), "glb_bytes": len(raw),
    "limitations": [
        "source_display_pose is one constant source-pose snapshot, not an animation performance",
        "simplified PBR; original toon color ramps/AO/outline have not been faithfully ported",
        "no locomotion/idle/retargeted animation/cloth physics/collision or publication rights adaptation",
        "third-party assets and this derived GLB remain ignored and local only",
    ],
}

# Reimport the actual exported GLB for bounds, pose and material visual checks.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb_path))
scene = bpy.context.scene
# Blender's glTF importer also builds a bone custom-shape Icosphere object.
# It isn't part of the GLB and must not affect measured model dimensions.
imported_meshes = [o for o in scene.objects if o.type == "MESH"
                   and any(m.type == "ARMATURE" for m in o.modifiers)]
for obj in scene.objects:
    if obj.type == "ARMATURE" and obj.animation_data and obj.animation_data.action:
        scene.frame_set(int(obj.animation_data.action.frame_range[0]))
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
points = [o.matrix_world @ Vector(c) for o in imported_meshes for c in o.evaluated_get(depsgraph).bound_box]
lo = Vector([min(p[i] for p in points) for i in range(3)])
hi = Vector([max(p[i] for p in points) for i in range(3)])
height = hi.z - lo.z
center = (lo + hi) / 2
report["blender_reimport_bounds"] = {"min": list(lo), "max": list(hi), "height": height}
report["blender_reimport_bounds"]["excludes_importer_custom_shapes"] = True
report["godot_suggested_scale_for_1_6m"] = 1.6 / height
report["front_direction"] = "Blender -Y, converted glTF/Godot +Z"
report["blender_reimport_mesh_objects"] = len(imported_meshes)
reimported_bones = {bone.name for obj in scene.objects if obj.type == "ARMATURE" for bone in obj.data.bones}
missing = sorted(set(rest) - reimported_bones)
report["preserved_source_bone_names"] = len(set(rest) & reimported_bones)
report["missing_source_bone_names"] = missing
report["extra_imported_bone_names"] = sorted(reimported_bones - set(rest))
assert not missing, "Export lost source bones: " + str(missing)
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 512
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world = bpy.data.worlds.new("LocalNeutralWorld")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.10, .12, .14, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = .45
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
for pos, power in [((-1.8, -2.1, 2), 220), ((1.5, -1, 1.3), 110), ((.5, 1.4, 2), 250)]:
    data = bpy.data.lights.new("LocalReviewLight", "AREA")
    data.energy = power * height * height / 4
    data.size = height * 1.5
    light = bpy.data.objects.new("LocalReviewLight", data)
    scene.collection.objects.link(light)
    light.location = center + Vector(pos) * height
    light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
camdata = bpy.data.cameras.new("LocalReviewCamera")
camdata.type = "ORTHO"
camdata.ortho_scale = height * 1.2
camdata.clip_end = max(1000, height * 20)
cam = bpy.data.objects.new("LocalReviewCamera", camdata)
scene.collection.objects.link(cam)
scene.camera = cam
for label, angle in [("front", 0), ("threequarter", 35)]:
    a = math.radians(angle)
    cam.location = center + Vector((math.sin(a)*3.2, -math.cos(a)*3.2, .04)) * height
    cam.rotation_euler = (center-cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUT / (label + ".png"))
    bpy.ops.render.render(write_still=True)
(OUT / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False))
print("LOCAL_MAP_EXPORT_COMPLETE")
