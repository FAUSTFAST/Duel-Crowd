extends SceneTree
## Actual runtime orthographic anatomy review. Does not edit production scenes.

var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle(count: int = 8) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func save(label: String) -> void:
	assert(root.get_texture().get_image().save_png("res://docs/proportions/" + label + ".png") == OK)
	print("PROPORTION_CAPTURE ", label)

func capture() -> void:
	DirAccess.make_dir_recursive_absolute("res://docs/proportions")
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/character_equipment_lab.tscn").instantiate()
	root.add_child(game)
	await settle(60)
	var player: CharacterBody3D = game.world.player
	var orbit: Node3D = player.orbit
	var visual: Node3D = player.visual
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	orbit.set_physics_process(false)
	player.set_physics_process(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	game.world.set_art_animation(false)
	visual.animation_player.stop()
	visual.skeleton.reset_bone_poses()
	var camera: Camera3D = orbit.camera
	# SpringArm internally writes child positions even when the orbit script is
	# paused. Detach this review camera so it cannot overwrite the chosen pose.
	camera.reparent(game.world, true)
	camera.top_level = true
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.15
	game.set_pixel_enabled(false)
	var origin: Vector3 = player.global_position
	for view in [["front", Vector3(0, .92, -4)], ["side", Vector3(4, .92, 0)], ["three_quarter", Vector3(2, .92, -4)]]:
		camera.global_position = origin + view[1]
		camera.look_at(origin + Vector3(0,.92,0))
		camera.reset_physics_interpolation()
		await settle()
		save("after_ortho_" + view[0])
	# Portrait still uses actual 3D lighting/materials, no image retouching.
	camera.size = .55
	camera.global_position = origin + Vector3(.10,1.64,-4)
	camera.look_at(origin + Vector3(0,1.64,0))
	camera.reset_physics_interpolation()
	await settle()
	save("after_portrait_native")
	quit()
