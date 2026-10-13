extends SceneTree

const Materials = preload("res://scripts/rendering/pixel_materials.gd")

func _initialize() -> void:
	Materials.use_saved_textures = false
	for kind in ["granite", "flagstone", "earth", "wood", "leaves", "steel"]:
		var image := Materials.texture(kind).get_image()
		var result := image.save_png("res://assets/textures/%s.png" % kind)
		print("Environment texture ", kind, ": ", result)
		if result != OK:
			quit(1)
			return
	# Eight original 32px flame drawings: split tongues, amber rim, hot core and embers.
	var atlas := Image.create(256, 32, false, Image.FORMAT_RGBA8)
	atlas.fill(Color.TRANSPARENT)
	for frame in 8:
		for y in range(4, 30):
			var t := float(29 - y) / 25.0
			var bend := sin(t * 5 + frame * TAU / 8.0) * (1 + t * 3)
			var width := (1.0 - t) * 8 + sin(t * PI) * 2
			for x in 32:
				var dx := absf(x - 15.5 - bend)
				if dx > width or (t > 0.4 and x < 15 + bend and x > 12 + bend and int(y + frame) % 12 < 4):
					continue
				var color := Color("df6631")
				if dx < width - 1.6:
					color = Color("f9a43b")
				if t < 0.68 and dx < width * 0.53:
					color = Color("ffe18a")
				if t < 0.33 and dx < width * 0.28:
					color = Color("fff3c9")
				atlas.set_pixel(frame * 32 + x, y, color)
		var ember_y := 2 + (frame * 3) % 8
		atlas.set_pixel(frame * 32 + 21 + frame % 3, ember_y, Color("f9a43b"))
	var result := atlas.save_png("res://assets/textures/torch_flame.png")
	print("Flame atlas: ", result)
	quit(0 if result == OK else 1)
