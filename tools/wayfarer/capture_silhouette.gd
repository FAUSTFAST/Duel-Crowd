extends SceneTree
## Review fixture only; production input/camera remains unchanged.
var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle(count: int = 8) -> void:
	for i in count: await physics_frame
	await RenderingServer.frame_post_draw

func save(label: String) -> void:
	assert(root.get_texture().get_image().save_png("res://docs/silhouette_review/" + label + ".png") == OK)
	print("GODOT_SILHOUETTE ", label)

func capture() -> void:
	root.size = Vector2i(1280, 720)
	for variant in ["old", "new"]:
		var path := "character_equipment_lab" if variant == "old" else "reference_silhouette"
		game = load("res://scenes/visual_lab/" + path + ".tscn").instantiate()
		root.add_child(game)
		await settle(60)
		var player: CharacterBody3D = game.world.player
		var orbit: Node3D = player.orbit
		orbit.set_process_input(false)
		orbit.set_process_unhandled_input(false)
		orbit.set_physics_process(false)
		player.set_physics_process(false)
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		game.hud.visible = false
		game.world.set_art_animation(false)
		# Capture the actual idle pose, not a different rest-pose mannequin.
		var visual: Node3D = player.visual
		visual.animation_tree.active = false
		visual.animation_player.play("idle")
		visual.animation_player.seek(0, true)
		visual.animation_player.pause()
		var camera: Camera3D = orbit.camera
		camera.reparent(game.world, true)
		camera.top_level = true
		camera.projection = Camera3D.PROJECTION_ORTHOGONAL
		camera.size = 2.1
		var origin: Vector3 = player.global_position
		for view in [["front", Vector3(0,.92,-4)], ["side",Vector3(4,.92,0)], ["threequarter",Vector3(-2,.92,-3.464)]]:
			camera.global_position = origin + view[1]
			camera.look_at(origin + Vector3(0,.92,0))
			camera.reset_physics_interpolation()
			for pixel in [false, true]:
				game.set_pixel_enabled(pixel)
				await settle()
				save("godot_" + variant + "_" + view[0] + ("_640" if pixel else "_native"))
		camera.projection = Camera3D.PROJECTION_PERSPECTIVE
		camera.global_position = origin + Vector3(2.0,4.4,-6.5)
		camera.look_at(origin + Vector3(0, .95, 0))
		camera.reset_physics_interpolation()
		await settle()
		save("godot_" + variant + "_gameplay_640")
		visual.animation_tree.active = true
		visual.set_animation_enabled(true)
		for state in [["walk",3.2],["run",5.8]]:
			for frame in 30:
				visual.update_locomotion(1.0/60.0,state[1])
				await process_frame
			await settle()
			save("godot_" + variant + "_" + state[0])
		game.queue_free()
		await settle()
	quit()
