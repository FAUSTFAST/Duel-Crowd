extends SceneTree
var game: Node
func _initialize() -> void:
	call_deferred("capture")
func settle() -> void:
	for i in 8: await process_frame
	await RenderingServer.frame_post_draw
func capture() -> void:
	root.size = Vector2i(1280,720)
	game = load("res://scenes/visual_lab/reference_silhouette.tscn").instantiate()
	root.add_child(game)
	for i in 30: await physics_frame
	var player: CharacterBody3D = game.world.player
	var visual: Node3D = player.visual
	player.set_physics_process(false)
	player.position = Vector3.ZERO
	visual.rotation.y = 0
	player.orbit.set_physics_process(false)
	player.orbit.set_process_input(false)
	player.orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	game.world.set_art_animation(false)
	var camera: Camera3D = player.orbit.camera
	camera.reparent(game.world,true)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.1
	var prefix := "before" if "--before" in OS.get_cmdline_user_args() else "after"
	var out := "res://docs/material_patterns/"
	DirAccess.make_dir_recursive_absolute(out)
	for equipped in [false,true]:
		if equipped:
			for id in visual.equipment.catalog: visual.equipment.equip(id)
		for view in [["front",Vector3(0,.95,-4)],["threequarter",Vector3(-2.4,.95,-3.2)],["back",Vector3(0,.95,4)]]:
			camera.position = view[1]
			camera.look_at(Vector3(0,.95,0))
			camera.reset_physics_interpolation()
			for pixels in [true,false]:
				game.set_pixel_enabled(pixels)
				await settle()
				var path := out+"%s_%s_%s_%s.png" % [prefix,"equipped" if equipped else "base",view[0],"640" if pixels else "native"]
				assert(root.get_texture().get_image().save_png(path)==OK)
				print("PATTERN_CAPTURE ",path)
	quit()
