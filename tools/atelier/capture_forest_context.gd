extends SceneTree

var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle(count: int = 60) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func capture() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	await settle()
	var player: CharacterBody3D = game.world.player
	var orbit: Node3D = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	game.world.set_art_animation(false)
	player.set_physics_process(false)
	orbit.yaw = 0.16
	orbit.pitch = -0.48
	orbit.distance = 7.0
	for use_new in [false, true]:
		if use_new:
			# Transient fixture replacement only; no production scene/resource saved.
			player.visual.free()
			player.visual_scene = load("res://scenes/characters/thorn_knight_visual.tscn")
			player._build_visual()
			player.set_visual_animation_enabled(false)
		await settle(120)
		var prefix := "new" if use_new else "old"
		assert(root.get_texture().get_image().save_png("res://docs/atelier/" + prefix + "_forest_context.png") == OK)
		game.set_pixel_enabled(false)
		await settle(30)
		assert(root.get_texture().get_image().save_png("res://docs/atelier/" + prefix + "_forest_native.png") == OK)
		game.set_pixel_enabled(true)
	game.world.set_art_animation(true)
	player.set_physics_process(true)
	var strip := Image.create_empty(1280, 720, false, Image.FORMAT_RGBA8)
	Input.action_press("move_forward")
	Input.action_press("sprint")
	for i in 4:
		await settle(10)
		var frame: Image = game.viewport.get_texture().get_image()
		frame.convert(Image.FORMAT_RGBA8)
		strip.blit_rect(frame, Rect2i(0,0,640,360), Vector2i(i%2*640,int(i/2)*360))
	Input.action_release("move_forward")
	Input.action_release("sprint")
	assert(strip.save_png("res://docs/atelier/new_forest_running.png") == OK)
	print("FOREST_CANDIDATE actual run on_floor=", player.is_on_floor(), " state=", player.visual.current_state, " position=",player.position)
	quit(0 if player.is_on_floor() and player.visual.current_state == "run" else 1)
