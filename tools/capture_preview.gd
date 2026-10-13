extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var world: Node3D = load("res://scenes/world/forest_ruins.tscn").instantiate()
	root.add_child(world)
	for i in 45:
		await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var result := image.save_png("res://docs/prototype_preview.png")
	print("Preview saved: ", result)
	quit(result)
