extends SceneTree

var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle(count: int = 45) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func save(label: String) -> void:
	var result := root.get_texture().get_image().save_png("res://docs/atelier/" + label + ".png")
	assert(result == OK)
	print("CAPTURE ", label)

func capture() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/knight_atelier.tscn").instantiate()
	root.add_child(game)
	await settle(90)
	var player: CharacterBody3D = game.world.player
	var orbit: Node3D = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	player.set_physics_process(false)
	game.world.set_art_animation(false)
	for variant in [false, true]:
		game.world.select_variant(variant)
		var prefix := "new" if variant else "old"
		for view in [["front", PI + 0.3, -0.20, 3.8], ["rear", 0.3, -0.20, 3.8], ["gameplay", 0.16, -0.48, 8.0]]:
			orbit.yaw = view[1]
			orbit.pitch = view[2]
			orbit.distance = view[3]
			game.set_pixel_enabled(true)
			game.set_resolution(1)
			await settle(90)
			save(prefix + "_" + view[0] + "_640")
			if view[0] == "front":
				for res in [0, 2]:
					game.set_resolution(res)
					await settle()
					save(prefix + "_front_" + ["480", "640", "960"][res])
				game.set_pixel_enabled(false)
				await settle()
				save(prefix + "_front_native")
		game.world.set_forest_light(true)
		orbit.yaw = PI + 0.3
		orbit.pitch = -0.2
		orbit.distance = 3.8
		game.set_resolution(1)
		game.set_pixel_enabled(true)
		await settle()
		save(prefix + "_forest_light")
		game.world.set_forest_light(false)
	# Pose sheets show the actual imported GLB, not generated illustrations.
	var model: Node3D = player.visual
	model.animation_tree.active = false
	model.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for clip in ["walk", "run"]:
		var strip := Image.create_empty(1280, 720, false, Image.FORMAT_RGBA8)
		for i in 4:
			model.animation_player.stop()
			model.animation_player.play(clip)
			model.animation_player.advance(0)
			model.animation_player.advance(0.03 + i * 0.14)
			await settle(3)
			var frame: Image = game.viewport.get_texture().get_image()
			frame.convert(Image.FORMAT_RGBA8)
			strip.blit_rect(frame, Rect2i(0, 0, 640, 360), Vector2i(i % 2 * 640, int(i / 2) * 360))
		assert(strip.save_png("res://docs/atelier/new_" + clip + "_poses.png") == OK)
	model.animation_player.stop()
	model.animation_tree.active = true
	game.world.set_art_animation(true)
	player.set_physics_process(true)
	game.hud.visible = true
	await settle(30)
	save("lab_ui")
	quit()
