extends SceneTree

var game: Node
var failures := 0
var checks := 0

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	checks += 1
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures += 1

func settle(frames: int = 6) -> void:
	for i in frames:
		await physics_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func _run() -> void:
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	if not is_instance_valid(game.world.player):
		quit(1)
		return
	var world: Node3D = game.world
	var player: CharacterBody3D = world.player
	var orbit: Node3D = player.orbit
	await settle(180)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "valley starts with captured mouse")
	# Only test fixtures disable external mouse motion for deterministic frames.
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	world.set_art_animation(false)
	check(player.is_on_floor(), "knight grounded on imported terrain collision")
	var minimum := 1000.0
	var maximum := -1000.0
	for h in world.field.heights:
		minimum = minf(minimum, h)
		maximum = maxf(maximum, h)
	check(maximum - minimum > 5, "terrain has >5m of actual elevation range")
	var arrays: Array = world.terrain.mesh.surface_get_arrays(0)
	check(arrays[Mesh.ARRAY_VERTEX].size() >= 4900, "terrain is an authored continuous mesh")
	check(arrays[Mesh.ARRAY_TEX_UV].size() == arrays[Mesh.ARRAY_VERTEX].size(), "terrain has UV coordinates")
	check(arrays[Mesh.ARRAY_TANGENT].size() == arrays[Mesh.ARRAY_VERTEX].size() * 4, "terrain has exported tangent basis")
	var moss_found := false
	var slate_found := false
	for c in arrays[Mesh.ARRAY_COLOR]:
		moss_found = moss_found or c.r > 0.5
		slate_found = slate_found or c.g > 0.5
	check(moss_found and slate_found, "GLB retains distinct moss and cliff weights")
	var space := world.get_world_3d().direct_space_state
	var collision_ok := true
	for p in world.trail:
		var query := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 10, p - Vector3.UP * 2)
		query.exclude = [player.get_rid()]
		var hit := space.intersect_ray(query)
		collision_ok = collision_ok and not hit.is_empty() and absf(hit.position.y - p.y) < 0.04
	check(collision_ok, "13 trail samples match the rendered terrain collision")
	check(world.trees.size() == 23 and world.rocks.size() == 42, "original branching trees and stratified rock modules loaded")
	var batches := world.find_children("*Batch", "MultiMeshInstance3D", false, false)
	check(batches.size() == 2, "ground cover uses two MultiMesh batches")
	check(world.surface_library.cache["ValleyBark"].normal_enabled, "bark has normal map enabled")
	check(world.surface_library.cache["ValleyBark"].albedo_texture.get_image().has_mipmaps(), "actual imported texture includes mipmaps")
	check(world.surface_library.cache["ValleySlate"].roughness_texture != null, "rock has roughness texture")
	check(world.surface_library.cache["ValleyLeaf"].transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR, "leaf silhouette uses alpha cutout")
	check(player.visual.find_child("HelmetShell", true, false) != null and player.left_leg != null and player.right_arm != null, "GLB knight preserves independent animated limbs")
	check(game.viewport.size == Vector2i(640, 360) and game.hud.get_viewport() == root, "shared pixel viewport and separate HD UI")
	await settle(30)
	var before: PackedByteArray = game.viewport.get_texture().get_image().get_data()
	await settle(30)
	check(before == game.viewport.get_texture().get_image().get_data(), "stationary valley pixels stable with fire frozen")
	world.set_art_animation(true)
	await settle(13)
	check(before != game.viewport.get_texture().get_image().get_data(), "real fire animation changes rendered image")
	world.set_art_animation(false)
	for i in 3:
		game.set_resolution(i)
		await settle()
		check(game.viewport.size == game.RESOLUTIONS[i] and is_equal_approx(game.presentation_rect.size.x / game.presentation_rect.size.y, 16.0 / 9.0), "resolution %s preserves aspect" % game.viewport.size)
	game.set_resolution(1)
	game.set_pixel_enabled(false)
	await settle()
	check(game.viewport.size == Vector2i(1280, 720), "native comparison is true native rendering")
	game.set_pixel_enabled(true)
	key(KEY_F3)
	check(world.terrain_material.get_shader_parameter("detail_enabled") == false and not world.surface_library.cache["ValleyBark"].normal_enabled, "F3 compares albedo, normals and roughness")
	key(KEY_F3)
	check(world.surface_library.cache["ValleyBark"].normal_enabled, "F3 restores material detail")
	var image := root.get_texture().get_image()
	var repeat_ok := true
	await settle()
	image = root.get_texture().get_image()
	for y in range(170, 640, 16):
		for x in range(520, 1250, 16):
			for offset in [Vector2i(1, 0), Vector2i(0, 1), Vector2i(1, 1)]:
				repeat_ok = repeat_ok and image.get_pixel(x, y) == image.get_pixel(x + offset.x, y + offset.y)
	check(repeat_ok, "presentation uses exact nearest 2x2 texels")
	orbit.set_process_input(true)
	orbit.set_process_unhandled_input(true)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	var yaw: float = orbit.yaw
	var motion := InputEventMouseMotion.new()
	motion.screen_relative = Vector2(10, 0)
	root.push_input(motion)
	check(is_equal_approx(angle_difference(yaw, orbit.yaw), -0.04), "mouse orbit uses a single forwarded screen-relative event")
	var distance: float = orbit.distance
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	root.push_input(wheel)
	check(orbit.distance < distance, "wheel zoom retained")
	key(KEY_ESCAPE)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "Esc releases mouse")
	var click := InputEventMouseButton.new()
	click.pressed = true
	click.button_index = MOUSE_BUTTON_LEFT
	click.position = game.presentation_rect.get_center()
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "image click recaptures mouse")
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.yaw = 0
	# Traverse the actual curved trail with the original player controller, not teleportation.
	player.position = world.trail[0] + Vector3.UP * 0.08
	player.velocity = Vector3.ZERO
	player.reset_physics_interpolation()
	await settle(30)
	Input.action_press("sprint")
	var travelled := 0
	var max_speed := 0.0
	for target in world.trail.slice(1):
		for tick in 100:
			var delta: Vector3 = target - player.position
			var horizontal := Vector2(delta.x, delta.z)
			if horizontal.length() < 0.23:
				travelled += 1
				break
			var direction := horizontal.normalized()
			Input.action_press("move_left", maxf(-direction.x, 0))
			Input.action_press("move_right", maxf(direction.x, 0))
			Input.action_press("move_forward", maxf(-direction.y, 0))
			Input.action_press("move_back", maxf(direction.y, 0))
			await physics_frame
			max_speed = maxf(max_speed, Vector2(player.velocity.x, player.velocity.z).length())
	for action in ["move_left", "move_right", "move_forward", "move_back", "sprint"]:
		Input.action_release(action)
	await settle(30)
	check(travelled == 12 and player.is_on_floor(), "knight physically traverses all 12 curved trail segments")
	check(max_speed > player.walk_speed + 1, "Shift running retains higher speed")
	check(orbit.global_position.distance_to(player.global_position + orbit.follow_offset) < 0.1, "camera smoothly follows moving knight")
	# Viewport.push_input dispatches callbacks but doesn't update global action state.
	Input.action_press("reset")
	await physics_frame
	Input.action_release("reset")
	await settle(30)
	check(player.position.distance_to(player.spawn_point) < 0.15, "R returns to valley spawn point")
	world.set_art_animation(true)
	await settle(30)
	var times: Array[float] = []
	for i in 180:
		var begin := Time.get_ticks_usec()
		await process_frame
		times.append((Time.get_ticks_usec() - begin) / 1000.0)
	times.sort()
	var sum := 0.0
	for t in times:
		sum += t
	print("PERF valley640 mean %.2f ms p95 %.2f ms draws %d objects %d" % [sum / times.size(), times[int(times.size() * 0.95)], Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME), Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)])
	print("RESULT: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)
