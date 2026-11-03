extends "res://scripts/valley/valley_world.gd"
## Local, static model inspection. Third-party files remain in the ignored library.
## Uses the original valley/controller; never saves or replaces their resources.

@export_file("*.glb") var local_model_path := "res://local_assets/bang_dream/models/mutsumi/map_preview_v2/mutsumi_map.glb"
@export var display_height := 1.58
var display_root: Node3D
var local_model: Node3D
var inspecting := true
var load_error := ""
var model_mesh_count := 0
var model_bone_count := 0
var display_bounds := AABB()

func _ready() -> void:
	super._ready()
	if not FileAccess.file_exists(local_model_path):
		load_error = "Local model missing. See local_assets/bang_dream/README.md."
		return
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var result := document.append_from_file(ProjectSettings.globalize_path(local_model_path), state)
	if result != OK:
		load_error = "Local GLB could not load (error %d)." % result
		return
	local_model = document.generate_scene(state) as Node3D
	if not is_instance_valid(local_model):
		load_error = "Local GLB did not produce a 3D scene."
		return
	display_root = Node3D.new()
	display_root.name = "LocalModelDisplay"
	add_child(display_root)
	display_root.add_child(local_model)
	# The source contains no motion. Restore its single-frame display pose only.
	for animation in local_model.find_children("*", "AnimationPlayer", true, false):
		for clip in animation.get_animation_list():
			if String(clip).ends_with("source_display_pose"):
				animation.play(clip)
				animation.seek(0.0, true)
				animation.pause()
	var has_bounds := false
	for mesh in local_model.find_children("*", "MeshInstance3D", true, false):
		model_mesh_count += 1
		var transformed: AABB = (local_model.global_transform.affine_inverse() * mesh.global_transform) * mesh.get_aabb()
		display_bounds = display_bounds.merge(transformed) if has_bounds else transformed
		has_bounds = true
	for skeleton in local_model.find_children("*", "Skeleton3D", true, false):
		model_bone_count += skeleton.get_bone_count()
	if not has_bounds or display_bounds.size.y < 0.01:
		load_error = "Local model has no usable mesh bounds."
		display_root.queue_free()
		display_root = null
		return
	var factor := display_height / display_bounds.size.y
	local_model.scale = Vector3.ONE * factor
	local_model.position = -Vector3(display_bounds.get_center().x, display_bounds.position.y, display_bounds.get_center().z) * factor
	var z := 6.0
	display_root.position = Vector3(path_x(z), height_at(path_x(z), z) + 0.02, z)
	player.orbit.min_distance = 2.4
	player.orbit.distance = 4.6
	player.orbit.yaw = 0.22
	player.orbit.pitch = -0.28
	set_inspecting(true)
	print("LOCAL_MODEL_LOADED: %d meshes, %d bones; static display only" % [model_mesh_count, model_bone_count])

func set_inspecting(enabled: bool) -> void:
	if not is_instance_valid(display_root):
		return
	inspecting = enabled
	player.set_physics_process(not enabled)
	player.velocity = Vector3.ZERO
	player.visual.visible = not enabled
	player.orbit.target = display_root if enabled else player
	player.orbit.follow_offset = Vector3(0, 0.95 if enabled else 1.2, 0)
	player.orbit.reset_physics_interpolation()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_TAB:
		set_inspecting(not inspecting)
		get_viewport().set_input_as_handled()
