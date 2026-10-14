extends SceneTree

var game: Node

func _initialize() -> void:
	call_deferred("capture")

func settle(frames: int = 90) -> void:
	for i in frames:
		await physics_frame
	await RenderingServer.frame_post_draw

func capture() -> void:
	root.mode = Window.MODE_WINDOWED
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	game.world.set_art_animation(false)
	game.hud.visible = false
	var orbit: Node3D = game.world.player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var label := "before" if "--before" in OS.get_cmdline_user_args() else "after"
	for view in [["gameplay", 0.16, -0.48, 10.0], ["front", PI + 0.25, -0.22, 3.5], ["rear", 0.35, -0.25, 3.5]]:
		orbit.yaw = view[1]
		orbit.pitch = view[2]
		orbit.distance = view[3]
		await settle(120)
		var image := root.get_texture().get_image()
		print("CAPTURE ", label, " ", view[0], " ", image.save_png("res://docs/knight/%s_%s.png" % [label, view[0]]))
	if label == "after":
		orbit.yaw = PI + 0.25
		orbit.pitch = -0.22
		orbit.distance = 3.5
		game.set_resolution(2)
		await settle()
		root.get_texture().get_image().save_png("res://docs/knight/after_front_960.png")
		game.set_pixel_enabled(false)
		await settle(30)
		root.get_texture().get_image().save_png("res://docs/knight/after_front_native.png")
		game.set_pixel_enabled(true)
		game.set_resolution(1)
		var player: CharacterBody3D = game.world.player
		var model: Node3D = player.visual
		player.set_physics_process(false)
		model.animation_tree.active = false
		model.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		for clip in ["walk", "run", "turn_left"]:
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
			print("POSE CAPTURE ", clip, " ", strip.save_png("res://docs/knight/" + clip + "_poses.png"))
		model.animation_player.stop()
		model.animation_tree.active = true
		player.set_physics_process(true)
		game.world.set_art_animation(true)
		player.position = player.spawn_point
		player.reset_physics_interpolation()
		orbit.yaw = 0.16
		orbit.pitch = -0.3
		orbit.distance = 5.0
		await settle()
		var actual_motion := Image.create_empty(1280, 720, false, Image.FORMAT_RGBA8)
		Input.action_press("move_forward")
		Input.action_press("sprint")
		for i in 4:
			await settle(8)
			var frame: Image = game.viewport.get_texture().get_image()
			frame.convert(Image.FORMAT_RGBA8)
			actual_motion.blit_rect(frame, Rect2i(0, 0, 640, 360), Vector2i(i % 2 * 640, int(i / 2) * 360))
		Input.action_release("move_forward")
		Input.action_release("sprint")
		print("MOVING CAPTURE ", actual_motion.save_png("res://docs/knight/run_in_game.png"))
	quit()
