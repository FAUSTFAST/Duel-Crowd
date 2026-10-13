extends RefCounted

static var cache: Dictionary = {}

# Original, deterministic 64px cluster textures. No photographic noise or assets.
static func texture(kind: String) -> Texture2D:
	if cache.has(kind):
		return cache[kind]
	var image := Image.create(64, 64, false, Image.FORMAT_RGB8)
	for y in 64:
		for x in 64:
			var coarse := _noise(x / 4, y / 4, 17)
			var value := 0.85 + coarse * 0.22
			var tint := Color.WHITE
			match kind:
				"stone", "road":
					var row: int = y / 16
					var column: int = (x + (row % 2) * 16) % 32
					value = 0.8 + _noise((x + (row % 2) * 16) / 32, row, 37) * 0.24 + coarse * 0.08
					if y % 16 == 0 or column == 0:
						value = 0.48
					elif y % 16 == 1 or column == 1:
						value += 0.12
					elif y % 16 == 15:
						value -= 0.12
					if _noise(x / 8, y / 8, 51) > 0.82:
						tint = Color(0.78, 0.9, 0.65)
				"earth":
					value = 0.88 + _noise(x / 8, y / 8, 17) * 0.12
					if _noise(x / 8, y / 8, 23) > 0.68:
						tint = Color(1.04, 0.99, 0.88)
					if (x % 8 == 2 and y % 8 < 3):
						value += 0.035
				"bark":
					value = 0.7 + _noise(x / 3, 0, 19) * 0.35 + coarse * 0.08
				"leaves":
					value = 0.85 + coarse * 0.13
					if (x + y) % 8 < 2:
						value += 0.06
				"steel":
					value = 0.85 + coarse * 0.13
					if x % 16 == 0:
						value = 0.65
				"cloth":
					value = 0.8 + _noise(x / 4, 0, 13) * 0.18
			image.set_pixel(x, y, Color(tint.r * value, tint.g * value, tint.b * value))
	image.generate_mipmaps()
	var result := ImageTexture.create_from_image(image)
	cache[kind] = result
	return result

static func _noise(x: int, y: int, seed_value: int) -> float:
	var hashed: int = ((x * 374761393 + y * 668265263 + seed_value * 1447) ^ (x * y * 127)) & 0x7fffffff
	hashed = ((hashed ^ (hashed >> 13)) * 1274126177) & 0x7fffffff
	return float(hashed % 101) / 100.0

static func apply(mat: StandardMaterial3D, kind: String, repeats_per_meter: float = 0.7) -> void:
	mat.albedo_texture = texture(kind)
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	mat.uv1_triplanar = true
	mat.uv1_world_triplanar = true
	mat.uv1_triplanar_sharpness = 16.0
	mat.uv1_scale = Vector3.ONE * repeats_per_meter
