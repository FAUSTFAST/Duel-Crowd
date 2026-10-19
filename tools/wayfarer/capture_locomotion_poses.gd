extends SceneTree
## Actual imported motion poses in fixed front/side cameras. No synthetic images.
var game: Node
func _initialize() -> void:
	call_deferred("capture")
func capture() -> void:
	root.size = Vector2i(1280,720)
	game = load("res://scenes/visual_lab/reference_silhouette.tscn").instantiate()
	root.add_child(game)
	for i in 30: await physics_frame
	var player: CharacterBody3D = game.world.player
	var visual: Node3D = player.visual
	player.set_physics_process(false)
	player.position = Vector3.ZERO
	player.visual.rotation.y = 0
	player.orbit.set_physics_process(false)
	player.orbit.set_process_input(false)
	player.orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	game.world.set_art_animation(false)
	visual.animation_tree.active = false
	visual.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var camera: Camera3D = player.orbit.camera
	camera.reparent(game.world,true)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.1
	DirAccess.make_dir_recursive_absolute("res://docs/locomotion_review/poses")
	for view in [["side",Vector3(4,.94,0)],["front",Vector3(0,.94,-4)]]:
		camera.position = view[1]
		camera.look_at(Vector3(0,.94,0))
		camera.reset_physics_interpolation()
		for clip in ["walk","run"]:
			visual.animation_player.play(clip)
			for frame in 8:
				visual.animation_player.seek(float(frame)/8, true)
				for i in 2: await process_frame
				await RenderingServer.frame_post_draw
				var path := "res://docs/locomotion_review/poses/%s_%s_%d.png" % [clip,view[0],frame]
				assert(game.viewport.get_texture().get_image().save_png(path)==OK)
	quit()
