extends SceneTree

var game: Node

func _initialize() -> void:
	call_deferred("_capture")

func settle(frames: int = 90) -> void:
	for i in frames:
		await physics_frame
	await RenderingServer.frame_post_draw

func save_image(label: String) -> void:
	var image := root.get_texture().get_image()
	if image.get_size() != Vector2i(1280, 720):
		push_error("Capture window changed: %s" % image.get_size())
		quit(1)
		return
	var result := image.save_png("res://docs/valley/" + label + ".png")
	print("CAPTURE ", label, " ", result)

func _capture() -> void:
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	game.world.set_art_animation(false)
	var orbit: Node3D = game.world.player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.yaw = 0.22
	orbit.pitch = -0.48
	orbit.distance = 10.0
	await settle(180)
	save_image("valley_640_ui")
	game.hud.visible = false
	for i in 3:
		game.set_resolution(i)
		await settle(30)
		save_image("valley_%d" % game.viewport.size.x)
	game.set_pixel_enabled(false)
	await settle(30)
	save_image("valley_native")
	game.set_pixel_enabled(true)
	game.set_resolution(1)
	game.world.set_material_detail(false)
	await settle(30)
	save_image("valley_flat_same_camera")
	game.world.set_material_detail(true)
	game.world.player.position = Vector3(game.world.path_x(-5), game.world.height_at(game.world.path_x(-5), -5) + 0.08, -5)
	game.world.player.reset_physics_interpolation()
	orbit.yaw = -0.55
	orbit.pitch = -0.32
	orbit.distance = 9.0
	await settle()
	save_image("valley_path")
	orbit.yaw = PI + 0.25
	orbit.pitch = -0.27
	orbit.distance = 4.0
	await settle()
	save_image("valley_knight")
	game.world.player.position = game.world.player.spawn_point
	game.world.player.velocity = Vector3.ZERO
	game.world.player.reset_physics_interpolation()
	orbit.yaw = 0.16
	orbit.pitch = -0.48
	orbit.distance = 10.0
	game.world.set_art_animation(true)
	await settle()
	var motion := Image.create_empty(1280, 720, false, Image.FORMAT_RGBA8)
	Input.action_press("move_forward")
	for i in 4:
		orbit.yaw += 0.08
		await settle(8)
		var frame: Image = game.viewport.get_texture().get_image()
		frame.convert(Image.FORMAT_RGBA8)
		motion.blit_rect(frame, Rect2i(0, 0, 640, 360), Vector2i(i % 2 * 640, i / 2 * 360))
	Input.action_release("move_forward")
	print("CAPTURE valley_motion ", motion.save_png("res://docs/valley/valley_motion.png"))
	quit()
