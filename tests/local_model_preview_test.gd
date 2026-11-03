extends SceneTree
## Graphical integration checks and actual captures; local assets are required.

var game: Node
var failures := 0
var checks := 0
const OUTPUT := "res://local_assets/bang_dream/previews/mutsumi_map_v2/"

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Run with a graphical window; screenshots require actual rendering.")
		quit(2)
		return
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	checks += 1
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures += 1

func settle(frames := 12) -> void:
	for i in frames:
		await physics_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func capture(label: String) -> void:
	var image := root.get_texture().get_image()
	check(image.get_size() == Vector2i(1280, 720), "capture has expected 1280x720 window")
	check(image.save_png(OUTPUT + label + ".png") == OK, "saved actual map render: " + label)

func _run() -> void:
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1280, 720)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
	game = load("res://scenes/visual_lab/local_model_preview.tscn").instantiate()
	root.add_child(game)
	var world: Node3D = game.world
	check(world.load_error.is_empty(), "local model loaded: " + world.load_error)
	if not world.load_error.is_empty():
		quit(1)
		return
	var player: CharacterBody3D = world.player
	var orbit: Node3D = player.orbit
	check(world.model_mesh_count >= 10 and world.model_mesh_count < 30, "character meshes loaded without MMD helper cloud")
	check(world.model_bone_count == 204, "203 source bones and exporter neutral_bone loaded")
	check(world.inspecting and orbit.target == world.display_root, "camera starts focused on static model")
	check(not player.is_physics_processing() and not player.visual.visible, "inspection does not move a mannequin as an animated player")
	check(player.visual.skeleton.get_bone_count() == 38, "original knight rig remains separate")
	check(is_equal_approx(world.display_bounds.size.y * world.local_model.scale.y, 1.58), "bind mesh bounds normalized to 1.58m; posed feet require visual review")
	var display_ground := Vector3(world.display_root.position.x, world.height_at(world.display_root.position.x, world.display_root.position.z), world.display_root.position.z)
	check(is_equal_approx(world.display_root.position.y - display_ground.y, 0.02), "static display root placed 2cm above sampled terrain")
	check(game.viewport.size == Vector2i(640, 360) and game.hud.get_viewport() == root, "shared pixel renderer and HD UI preserved")
	var clips := 0
	for animation in world.local_model.find_children("*", "AnimationPlayer", true, false):
		for clip in animation.get_animation_list():
			if clip != "RESET":
				clips += 1
				check(String(clip).ends_with("source_display_pose"), "only source pose snapshot; no invented movement clips")
	check(clips == 1, "single static pose snapshot loaded")
	key(KEY_ESCAPE)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "Esc releases mouse through shared input route")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = Vector2(640, 360)
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "click recaptures mouse")
	var yaw: float = orbit.yaw
	var motion := InputEventMouseMotion.new()
	motion.screen_relative = Vector2(20, 0)
	root.push_input(motion)
	check(is_equal_approx(orbit.yaw, yaw - 20 * orbit.mouse_sensitivity), "relative mouse motion forwarded once")
	var distance: float = orbit.distance
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	root.push_input(wheel)
	check(orbit.distance < distance, "mouse wheel zoom preserved")
	# Deterministic captures only: disable physical cursor changes, not production input.
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	world.set_art_animation(false)
	orbit.yaw = 0.0
	orbit.pitch = -0.25
	orbit.distance = 4.6
	await settle(150)
	capture("forest_front_640")
	orbit.yaw = 0.65
	orbit.pitch = -0.28
	await settle(45)
	capture("forest_three_quarter_640")
	game.set_pixel_enabled(false)
	await settle()
	capture("forest_three_quarter_native")
	for i in 3:
		game.set_resolution(i)
		game.set_pixel_enabled(true)
		await settle()
		check(game.viewport.size == game.RESOLUTIONS[i], "resolution preset %d loads" % i)
		check(is_equal_approx(game.presentation_rect.size.x / game.presentation_rect.size.y, 16.0 / 9.0), "16:9 preserved")
	game.set_resolution(1)
	key(KEY_TAB)
	check(not world.inspecting and player.is_physics_processing() and player.visual.visible, "Tab enables original knight exploration")
	check(orbit.target == player, "exploration camera follows original controller")
	await settle(45)
	check(player.is_on_floor(), "original capsule remains grounded")
	orbit.yaw = 0.0
	var start: Vector3 = player.position
	Input.action_press("move_forward")
	await settle(30)
	Input.action_release("move_forward")
	check(player.position.distance_to(start) > 0.6, "original WASD movement works beside static model")
	Input.action_press("move_forward")
	Input.action_press("sprint")
	await settle(20)
	check(Vector2(player.velocity.x, player.velocity.z).length() > 4.5, "original Shift run preserved")
	Input.action_release("sprint")
	Input.action_release("move_forward")
	await settle()
	key(KEY_TAB)
	check(world.inspecting and orbit.target == world.display_root, "Tab returns to model inspection")
	world.set_art_animation(true)
	await settle(30)
	var intervals: Array[float] = []
	var previous := Time.get_ticks_usec()
	for i in 120:
		await process_frame
		var now := Time.get_ticks_usec()
		intervals.append((now - previous) / 1000.0)
		previous = now
	intervals.sort()
	print("LOCAL_PREVIEW_FRAME_INTERVAL_MS: median=%.2f p95=%.2f (short window, not GPU timing)" % [intervals[60], intervals[114]])
	print("LOCAL_MODEL_PREVIEW_TEST_COMPLETE: %d checks, %d failures" % [checks, failures])
	quit(1 if failures else 0)
