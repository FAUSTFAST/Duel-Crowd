extends SceneTree
## Actual imported rig + controller regression. No headless visual claims.
var checks := 0
var failures := 0
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

func settle(count := 10) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func sample(clip: String, time: float, bone: String) -> Vector3:
	var motion: Node = game.world.motion
	motion.animation_player.play(clip)
	motion.animation_player.seek(time, true)
	motion.skeleton.force_update_all_bone_transforms()
	var index: int = motion.skeleton.find_bone(bone)
	assert(index >= 0, "Missing bone " + bone)
	return game.world.player.global_transform.affine_inverse() * motion.skeleton.global_transform * motion.skeleton.get_bone_global_pose(index).origin

func run() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/local_model_motion.tscn").instantiate()
	root.add_child(game)
	check(game.world.load_error.is_empty(), "motion GLB loads: " + game.world.load_error)
	if not game.world.load_error.is_empty():
		quit(1)
		return
	var world: Node3D = game.world
	var player: CharacterBody3D = world.player
	var orbit: Node3D = player.orbit
	var motion: Node = world.motion
	check(not world.inspecting and player.is_physics_processing(), "starts with playable Mutsumi")
	check(world.display_root.get_parent() == player and not player.visual.visible, "local visual attached to existing controller; original knight retained hidden")
	check(motion.tree.get_node_or_null(motion.tree.root_node) != null and motion.tree.get_node_or_null(motion.tree.anim_player) == motion.animation_player, "animation root and player paths survive reparenting")
	check(motion.skeleton.get_bone_count() == 204, "204 imported bones preserved")
	check(not game.pixel_enabled and game.viewport.size == Vector2i(1280, 720) and game.hud.get_viewport() == root, "native rendering is the default; HD UI intact")
	check(game.display.material == null and game.display.texture_filter == CanvasItem.TEXTURE_FILTER_LINEAR, "native presentation has no pixel quantization shader and uses linear filtering")
	check(game.viewport.msaa_3d == Viewport.MSAA_4X, "native rendering uses 4x geometry antialiasing")
	for clip in ["idle", "walk", "run"]:
		check(motion.animation_player.has_animation(clip), "actual imported clip: " + clip)
		check(is_equal_approx(motion.animation_player.get_animation(clip).length, 1.0), "one-second exact loop: " + clip)
	check(is_equal_approx(world.animation_bake_fps, 60.0), "runtime GLTF generation explicitly preserves 60fps")
	check(is_equal_approx(player.walk_speed, 1.25) and is_equal_approx(player.run_speed, 2.8), "motion-specific movement speeds")
	key(KEY_ESCAPE)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "Esc releases cursor")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = Vector2(640, 360)
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "click recaptures cursor")
	var old_yaw: float = orbit.yaw
	var mouse := InputEventMouseMotion.new()
	mouse.screen_relative = Vector2(20, 0)
	root.push_input(mouse)
	check(is_equal_approx(orbit.yaw, old_yaw - 20 * orbit.mouse_sensitivity), "mouse relative movement forwarded once")
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await settle(100)
	check(player.is_on_floor(), "capsule grounded on forest terrain")
	check(motion.current_state == "idle", "standing selects idle")
	# Imported clip sampling, independent of controller displacement.
	motion.set_enabled(false)
	motion.tree.active = false
	player.set_physics_process(false)
	motion.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var idle_a := sample("idle", .0, "上半身")
	var idle_extent := 0.0
	for i in 16:
		idle_extent = maxf(idle_extent, idle_a.distance_to(sample("idle", i / 16.0, "上半身")))
	print("IDLE_ROOT_EXTENT_M ", idle_extent)
	check(idle_extent > .0001, "imported idle has subtle body motion across its loop")
	# Head/feet move through the actual imported skin hierarchy.
	var foot_a := sample("walk", .1, "足首.L")
	var foot_b := sample("walk", .2, "足首.L")
	var slip := absf((foot_b.z - foot_a.z) - 1.25 * .1)
	print("WALK_IMPORTED_SUPPORT_RESIDUAL_M ", slip, " feet=", foot_a, " -> ", foot_b)
	check(slip < .04, "walk support displacement matches 1.25m phase stride within 4cm")
	var low := 1000.0
	var high := -1000.0
	for i in 40:
		var p := sample("walk", i / 40.0, "足首.L")
		low = minf(low, p.y)
		high = maxf(high, p.y)
	check(high - low > .025, "walk foot lifts during swing")
	for clip in ["idle", "walk", "run"]:
		var first := sample(clip, 0, "足首.L")
		var last := sample(clip, motion.animation_player.get_animation(clip).length - .0001, "足首.L")
		check(first.distance_to(last) < .015, clip + " foot loop seam <1.5cm")
	motion.animation_player.stop()
	motion.tree.active = true
	motion.set_enabled(true)
	player.set_physics_process(true)
	orbit.yaw = 0
	var start: Vector3 = player.position
	Input.action_press("move_forward")
	await settle(50)
	check(motion.current_state == "walk" and motion.move_weight > .95, "WASD blends into walking")
	check(absf(Vector2(player.velocity.x, player.velocity.z).length() - 1.25) < .05, "walking reaches calibrated speed")
	check(player.position.distance_to(start) > .6, "walk actually traverses the map")
	var ankle: int = motion.skeleton.find_bone("足首.L")
	var animated_a: Vector3 = motion.skeleton.get_bone_global_pose(ankle).origin
	await settle(15)
	var animated_b: Vector3 = motion.skeleton.get_bone_global_pose(ankle).origin
	check(animated_a.distance_to(animated_b) * world.local_model.scale.y > .03, "active animation tree actually moves imported bones while walking")
	check(absf(angle_difference(world.display_root.rotation.y, player.visual.rotation.y + PI)) < .001, "+Z imported forward matches controller heading")
	Input.action_press("sprint")
	await settle(50)
	check(motion.current_state == "run" and motion.run_weight > .95, "Shift blends to jogging")
	check(absf(Vector2(player.velocity.x, player.velocity.z).length() - 2.8) < .05, "jogging reaches calibrated speed")
	check(absf(float(motion.tree.get("parameters/cadence/scale")) - 2.8 / 1.8) < .03, "jog cadence follows actual speed and authored stride")
	Input.action_release("sprint")
	Input.action_release("move_forward")
	await settle(50)
	check(motion.current_state == "idle" and motion.move_weight < .01, "release input brakes and returns to idle")
	var position_before: Vector3 = world.display_root.global_position
	key(KEY_TAB)
	await settle(5)
	check(world.inspecting and not player.is_physics_processing(), "Tab enters inspection")
	check(world.display_root.global_position.distance_to(position_before) < .001, "inspection preserves world position")
	key(KEY_TAB)
	await settle(5)
	check(not world.inspecting and player.is_physics_processing(), "Tab returns to playable model")
	check(world.display_root.global_position.distance_to(position_before) < .05, "returning does not teleport model")
	game.set_pixel_enabled(true)
	check(game.display.material != null and game.display.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST and game.viewport.msaa_3d == Viewport.MSAA_DISABLED, "optional pixel comparison restores its own shader/filter/AA")
	for i in 3:
		game.set_resolution(i)
		await settle(2)
		check(game.viewport.size == game.RESOLUTIONS[i], "resolution preset %d works" % i)
	game.set_pixel_enabled(false)
	await settle(2)
	check(game.viewport.size == Vector2i(1280, 720) and game.display.material == null and game.viewport.msaa_3d == Viewport.MSAA_4X, "returning to native restores resolution and smooth presentation")
	print("LOCAL_MODEL_MOTION_TEST_COMPLETE: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)
