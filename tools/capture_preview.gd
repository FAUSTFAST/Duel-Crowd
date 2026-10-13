extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func settle() -> void:
	for i in 300:
		await process_frame
	await RenderingServer.frame_post_draw

func save_preview(path: String) -> void:
	var result := root.get_texture().get_image().save_png(path)
	print("Preview ", path, ": ", result)
	if result != OK:
		quit(1)

func _capture() -> void:
	var game: Node = load("res://scenes/rendering/pixel_game.tscn").instantiate()
	root.add_child(game)
	game.world.player.orbit.set_process_input(false)
	game.world.player.orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.world.player.orbit.yaw = 0.55
	game.world.player.orbit.pitch = -0.65
	game.world.player.orbit.distance = 12.0
	await settle()
	save_preview("res://docs/prototype_preview.png")
	save_preview("res://docs/visual_pixel_640.png")
	game.set_pixel_enabled(false)
	await settle()
	save_preview("res://docs/visual_native.png")
	game.set_pixel_enabled(true)
	for index in [0, 2]:
		game.set_resolution(index)
		await settle()
		save_preview("res://docs/visual_pixel_%d.png" % game.viewport.size.x)
	game.set_resolution(1)
	game.world.player.orbit.yaw = 0.55
	game.world.player.orbit.pitch = -0.65
	var strip := Image.create(1280, 720, false, Image.FORMAT_RGB8)
	Input.action_press("move_forward")
	for index in 4:
		game.world.player.orbit.yaw += 0.09
		for frame in 20:
			await physics_frame
		await RenderingServer.frame_post_draw
		var frame_image: Image = game.viewport.get_texture().get_image()
		frame_image.convert(Image.FORMAT_RGB8)
		strip.blit_rect(frame_image, Rect2i(0, 0, 640, 360), Vector2i((index % 2) * 640, (index / 2) * 360))
	Input.action_release("move_forward")
	print("Motion strip: ", strip.save_png("res://docs/visual_motion.png"))
	quit()
