extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var game: Node = load("res://scenes/rendering/pixel_game.tscn").instantiate()
	root.add_child(game)
	game.hud.visible = false
	game.world.player.orbit.set_process_input(false)
	game.world.player.orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var camera := Camera3D.new()
	game.world.add_child(camera)
	camera.position = Vector3(3.35, 2.45, 3.7)
	camera.look_at(Vector3(2.5, 1.98, 1.0))
	camera.fov = 42
	camera.make_current()
	for i in 60:
		await process_frame
	var sheet := Image.create(1280, 720, false, Image.FORMAT_RGBA8)
	var flames := get_nodes_in_group("art_flames")
	var frames: Array[int] = []
	for i in 4:
		await create_timer(0.105).timeout
		await RenderingServer.frame_post_draw
		var image: Image = game.viewport.get_texture().get_image()
		frames.append(flames[1].sprite.frame)
		sheet.blit_rect(image, Rect2i(0, 0, 640, 360), Vector2i((i % 2) * 640, (i / 2) * 360))
	var result := sheet.save_png("res://docs/stage4_flame_motion.png")
	print("Animated flame samples: ", frames, ", save: ", result)
	quit(0 if result == OK else 1)
