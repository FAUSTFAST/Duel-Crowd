extends SceneTree

const Renderer = preload("res://scripts/rendering/pixel_renderer.gd")
var game: Node
var failures: int = 0

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Rendering acceptance needs a graphical window.")
		quit(2)
		return
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures += 1

func settle(count: int = 6) -> void:
	for i in count:
		await process_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func _run() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/rendering/pixel_game.tscn").instantiate()
	root.add_child(game)
	await settle(300)
	check(game.viewport.size == Vector2i(640, 360), "default internal resolution 640x360")
	check(game.viewport.get_camera_3d() == game.world.player.orbit.camera, "camera renders only in world viewport")
	check(game.hud.get_viewport() == root and game.world.get_viewport() == game.viewport, "HD UI separate from low resolution world")
	check(game.viewport.msaa_3d == Viewport.MSAA_DISABLED, "no post antialias blur")
	var presented := root.get_texture().get_image()
	var repeat_ok := true
	for y in range(170, 640, 10):
		for x in range(520, 1250, 10):
			var color := presented.get_pixel(x, y)
			for offset in [Vector2i(1, 0), Vector2i(0, 1), Vector2i(1, 1)]:
				if color != presented.get_pixel(x + offset.x, y + offset.y):
					repeat_ok = false
	check(repeat_ok, "640p presentation repeats exact 2x2 texels")
	var still_before: PackedByteArray = game.viewport.get_texture().get_image().get_data()
	await settle(30)
	check(still_before == game.viewport.get_texture().get_image().get_data(), "stationary view has no temporal flicker")
	for index in [2, 0, 1]:
		key(KEY_F2)
		await settle()
		check(game.viewport.size == Renderer.RESOLUTIONS[index], "F2 cycles to %s" % game.viewport.size)
		var rect: Rect2 = game.presentation_rect
		check(is_equal_approx(rect.size.x / rect.size.y, 16.0 / 9.0), "resolution keeps aspect ratio")
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		var yaw: float = game.world.player.orbit.yaw
		var motion := InputEventMouseMotion.new()
		motion.screen_relative = Vector2(10, 0)
		root.push_input(motion)
		check(is_equal_approx(angle_difference(yaw, game.world.player.orbit.yaw), -0.04), "mouse sensitivity unchanged by resolution")
	key(KEY_F1)
	await settle()
	check(not game.pixel_enabled and game.viewport.size == Vector2i(1280, 720), "F1 native resolution comparison")
	key(KEY_F1)
	await settle()
	check(game.viewport.size == Vector2i(640, 360), "F1 restores chosen pixel resolution")
	key(KEY_F3)
	check(game.world.detailed_materials[0].albedo_texture == null, "F3 disables texture detail")
	key(KEY_F3)
	check(game.world.detailed_materials[0].albedo_texture != null, "F3 restores original pixel texture")
	var fog_before: bool = game.world.environment.fog_enabled
	key(KEY_F4)
	check(game.world.environment.fog_enabled != fog_before, "F4 fog comparison")
	key(KEY_F4)
	var ambient_before: float = game.world.environment.ambient_light_energy
	key(KEY_EQUAL)
	check(game.world.environment.ambient_light_energy > ambient_before, "ambient parameter adjustment")
	key(KEY_MINUS)
	root.size = Vector2i(1000, 700)
	await settle(10)
	check(game.viewport.size == Vector2i(640, 360) and game.presentation_rect.size == Vector2(640, 360), "non 16:9 window keeps integer pixel sizes")
	check(game.presentation_rect.position == Vector2(180, 170), "non 16:9 view centered with letterbox")
	key(KEY_ESCAPE)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = Vector2(2, 2)
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "letterbox click does not capture mouse")
	click.position = game.presentation_rect.get_center()
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "game image click recaptures mouse after resize")
	key(KEY_F6)
	await settle()
	check(game.presentation_rect.size == Vector2(1000, 562.5), "fit mode preserves aspect without stretching")
	key(KEY_F1)
	await settle()
	check(game.viewport.size == Vector2i(992, 558), "native comparison uses exact 16:9 whole pixel dimensions")
	key(KEY_F1)
	key(KEY_F6)
	root.size = Vector2i(640, 360)
	game.set_resolution(2)
	await settle()
	check(game.presentation_rect.size == Vector2(640, 360), "small window downsizes 960p without distortion")
	root.size = Vector2i(1280, 720)
	game.set_resolution(1)
	await settle(30)
	var sample_times: Array[float] = []
	for i in 180:
		var begin := Time.get_ticks_usec()
		await process_frame
		sample_times.append((Time.get_ticks_usec() - begin) / 1000.0)
	sample_times.sort()
	var total := 0.0
	for sample in sample_times:
		total += sample
	print("PERF: 640x360 average frame %.2f ms, p95 %.2f ms, objects %d, draw calls %d" % [total / sample_times.size(), sample_times[int(sample_times.size() * 0.95)], Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME), Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)])
	print("RESULT: ", failures, " failures")
	quit(1 if failures else 0)
