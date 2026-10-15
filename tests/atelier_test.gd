extends SceneTree

var failures := 0
var checks := 0
var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok:
		failures += 1

func frames(count: int = 30) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func run() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/knight_atelier.tscn").instantiate()
	root.add_child(game)
	await frames(90)
	var world: Node3D = game.world
	var player: CharacterBody3D = world.player
	var orbit: Node3D = player.orbit
	check(world.new_variant, "independent lab defaults to new candidate")
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "startup mouse capture")
	check(player.is_on_floor(), "original controller settles on lab collision")
	var capsule: Resource = player.get_child(0).shape
	check(is_equal_approx(capsule.radius, 0.3) and is_equal_approx(capsule.height, 1.8), "original capsule dimensions")
	check(player.visual.skeleton.get_bone_count() == 38, "new imported skeleton has 38 bones")
	check(player.study_materials.materials.size() == 5, "new GLB has five skinned materials")
	for clip in ["idle", "walk", "run", "turn_left", "turn_right"]:
		check(player.visual.animation_player.has_animation(clip), "new clip " + clip)
	check(game.hud.get_viewport() == root and world.get_viewport() == game.viewport, "HD UI remains outside world viewport")
	check(world.botanicals.get_child_count() == 3, "three reusable cutout cards, no new map dressing")
	var fern_mat: StandardMaterial3D = world.botanicals.get_child(0).material_override
	var fern: Image = fern_mat.albedo_texture.get_image()
	check(fern.detect_alpha() != Image.ALPHA_NONE and fern_mat.transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR, "real alpha cutout uses hard-edge scissor")
	for index in [0, 1, 2]:
		game.set_resolution(index)
		var yaw: float = orbit.yaw
		var motion := InputEventMouseMotion.new()
		motion.screen_relative = Vector2(10, 0)
		root.push_input(motion)
		check(is_equal_approx(angle_difference(yaw, orbit.yaw), -0.04), "single mouse event route at resolution " + str(index))
	game.set_resolution(1)
	var original_orbit: int = orbit.get_instance_id()
	var location := player.position
	key(KEY_B)
	check(not world.new_variant and player.visual.scene_file_path.ends_with("ashen_knight_visual.tscn"), "B swaps to preserved previous knight once")
	check(player.orbit.get_instance_id() == original_orbit and player.position == location and player.get_child(0).shape == capsule, "comparison preserves player, camera, collision and position")
	key(KEY_F3)
	check(player.study_materials.materials[0].albedo_texture == null, "material isolation comparison disables atlas")
	key(KEY_B)
	check(world.new_variant and player.study_materials.materials[0].albedo_texture == null, "variant swap preserves material comparison state")
	key(KEY_F3)
	check(player.study_materials.materials[0].albedo_texture != null, "atlas comparison restores original texture")
	key(KEY_L)
	check(world.forest_light and world.environment.fog_enabled, "forest light preset")
	key(KEY_L)
	check(not world.forest_light and not world.environment.fog_enabled, "neutral lighting restored")
	key(KEY_2)
	await frames()
	check(player.preview_speed == 3.2 and player.visual.current_state == "walk", "in-place walk inspection uses animation state machine")
	key(KEY_3)
	await frames()
	check(player.visual.current_state == "run", "in-place run inspection")
	key(KEY_0)
	orbit.yaw = 0.0
	Input.action_press("move_forward")
	await frames()
	check(player.preview_speed < 0 and player.visual.current_state == "walk" and player.position.distance_to(location)>1, "WASD movement drives walking")
	Input.action_press("sprint")
	await frames()
	check(player.visual.current_state == "run" and Vector2(player.velocity.x,player.velocity.z).length()>5.5, "Shift running drives speed-matched animation")
	Input.action_release("move_forward")
	Input.action_release("sprint")
	await frames()
	check(player.visual.current_state == "idle", "deceleration returns to breathing idle")
	key(KEY_ESCAPE)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "Escape releases cursor")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = Vector2(640, 360)
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "click recaptures cursor")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	var distance: float = orbit.distance
	root.push_input(wheel)
	check(orbit.distance < distance, "wheel zoom preserved")
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	player.position = Vector3.ZERO
	player.reset_physics_interpolation()
	orbit.yaw = PI + 0.3
	orbit.pitch = -0.2
	orbit.distance = 3.8
	world.set_art_animation(false)
	await frames(120)
	var still: PackedByteArray = game.viewport.get_texture().get_image().get_data()
	await frames()
	check(still == game.viewport.get_texture().get_image().get_data(), "frozen character has stable actual pixels")
	world.set_art_animation(true)
	await frames(25)
	check(still != game.viewport.get_texture().get_image().get_data(), "real skeletal animation changes rendered pixels")
	# Short real frame intervals, animation enabled. Window/VSync affect results.
	for variant in [false, true]:
		world.select_variant(variant)
		await frames(45)
		var samples: Array[float] = []
		var last := Time.get_ticks_usec()
		for i in 180:
			await process_frame
			var now := Time.get_ticks_usec()
			samples.append((now-last)/1000.0)
			last = now
		samples.sort()
		var total := 0.0
		for sample in samples:
			total += sample
		print("PERF ", "new" if variant else "old", " frame_interval mean_ms=", total/samples.size(), " p95_ms=", samples[int(samples.size()*.95)], " draw_calls=", Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	check(world.animation_enabled, "animation restored before performance sampling")
	print("ATELIER RESULT ", checks, " checks, ", failures, " failures")
	quit(1 if failures else 0)
