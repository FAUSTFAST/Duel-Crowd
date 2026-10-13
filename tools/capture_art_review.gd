extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _settle() -> void:
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1280, 720)
	for i in 150:
		await physics_frame
	await RenderingServer.frame_post_draw

func _save_capture(path: String) -> Error:
	var image := root.get_texture().get_image()
	if image.get_size() != Vector2i(1280, 720):
		push_error("Comparison window size changed: %s" % image.get_size())
		return ERR_INVALID_DATA
	return image.save_png(path)

func _capture() -> void:
	var prefix := "stage4_before" if OS.get_cmdline_user_args().has("--before") else "stage4_after"
	var game: Node = load("res://scenes/rendering/pixel_game.tscn").instantiate()
	root.add_child(game)
	game.hud.visible = false
	if game.world.has_method("set_art_animation"):
		game.world.set_art_animation(false)
	var orbit: Node3D = game.world.player.orbit
	# Freeze real mouse input during automated comparisons, not game logic.
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.yaw = 0.55
	orbit.pitch = -0.65
	orbit.distance = 12.0
	await _settle()
	var result := _save_capture("res://docs/%s_overview.png" % prefix)
	print(prefix, " overview: ", result, " yaw=", orbit.yaw, " pitch=", orbit.pitch, " distance=", orbit.distance)
	if result != OK:
		quit(1)
		return
	orbit.yaw = PI + 0.35
	orbit.pitch = -0.27
	orbit.distance = 4.0
	await _settle()
	result = _save_capture("res://docs/%s_knight.png" % prefix)
	print(prefix, " knight: ", result, " yaw=", orbit.yaw, " pitch=", orbit.pitch, " distance=", orbit.distance)
	quit(0 if result == OK else 1)
