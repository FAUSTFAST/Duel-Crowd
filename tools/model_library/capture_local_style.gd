extends SceneTree
## Actual same-pose native/pixel screenshots, local only; never rewrites source assets.
var output := "res://local_assets/bang_dream/previews/mutsumi_native_20261105/"

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle() -> void:
	for i in 6:
		await process_frame
	await RenderingServer.frame_post_draw

func capture() -> void:
	if DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(output)):
		push_error("Refusing to overwrite style review")
		quit(2)
		return
	root.size = Vector2i(1280, 720)
	var game: Node = load("res://scenes/visual_lab/local_model_motion.tscn").instantiate()
	root.add_child(game)
	if not game.world.load_error.is_empty():
		push_error(game.world.load_error)
		quit(1)
		return
	var orbit: Node3D = game.world.player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.distance = 4.1
	orbit.yaw = PI + .32
	orbit.pitch = -.24
	for i in 90:
		await process_frame
	game.world.set_inspecting(true)
	game.world.set_art_animation(false)
	game.hud.visible = false
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output))
	for pixel in [true, false]:
		game.set_pixel_enabled(pixel)
		game.set_resolution(1)
		await settle()
		var path: String = output + ("pixel_640.png" if pixel else "native_1280.png")
		if root.get_texture().get_image().save_png(path) != OK:
			quit(1)
			return
	var report := {"engine": Engine.get_version_info().string, "window": [1280, 720], "native_internal": [game.viewport.size.x, game.viewport.size.y], "native_msaa": game.viewport.msaa_3d, "same_camera_pose": true, "source_model_modified": false, "material_limit": "Existing simplified PBR, not author's complete toon shader"}
	FileAccess.open(output + "review.json", FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	print("LOCAL_NATIVE_STYLE_CAPTURE_COMPLETE ", JSON.stringify(report))
	quit(0)
