extends SceneTree

const Materials = preload("res://scripts/rendering/pixel_materials.gd")
func _initialize() -> void:
	Materials.use_saved_textures = false
	for kind in ["stone", "road", "granite", "flagstone", "earth", "bark", "wood", "grass", "leaves", "steel", "cloth"]:
		var image: Image = Materials.texture(kind).get_image()
		var result := image.save_png("res://assets/textures/%s.png" % kind)
		print(kind, ": ", result)
		if result != OK:
			quit(1)
			return
	quit()
