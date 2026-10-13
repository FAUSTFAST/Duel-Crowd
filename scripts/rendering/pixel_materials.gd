extends RefCounted

static var cache: Dictionary = {}
static var use_saved_textures: bool = true

# Original, deterministic 64px cluster textures. No photographic noise or assets.
static func texture(kind: String) -> Texture2D:
	if cache.has(kind):
		return cache[kind]
	var source_path := "res://assets/textures/%s.png" % kind
	if use_saved_textures and ResourceLoader.exists(source_path):
		var imported: Texture2D = load(source_path)
		var source := imported.get_image()
		if source.is_compressed():
			source.decompress()
		source.generate_mipmaps()
		var loaded := ImageTexture.create_from_image(source)
		cache[kind] = loaded
		return loaded
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
				"granite", "flagstone":
					value = 0.84 + coarse * 0.14
					var crack := (x + y / 2 + int(_noise(0, y / 16, 61) * 12)) % 43
					if crack == 0 and y % 32 > 17:
						value = 0.6
					elif crack == 1 and y % 32 > 17:
						value = 1.02
					if _noise(x / 12, y / 12, 51) > 0.8:
						tint = Color(0.78, 0.91, 0.7)
					if _noise(x / 3, y / 3, 11) > 0.92:
						value -= 0.1
				"grass":
					value = 0.77 + coarse * 0.15
					if (x + y / 3) % 11 < 2 and y % 16 > 4:
						value = 1.02
						tint = Color(0.9, 1.0, 0.76)
				"wood":
					value = 0.75 + _noise(x / 6, y / 32, 19) * 0.22
					if x % 16 == 0:
						value = 0.45
					if (x + y / 12) % 7 == 0:
						value -= 0.09
				"earth":
					var patch := sin(x * 0.13 + sin(y * 0.16)) + cos(y * 0.15 - x * 0.07)
					value = 0.82 + floorf((patch + 2) * 1.5) * 0.035
					if patch > 0.65:
						tint = Color(0.84, 0.96, 0.73)
					elif patch < -0.5:
						tint = Color(1.04, 0.94, 0.79)
					if _noise(x / 2, y / 2, 23) > 0.93:
						value += 0.08
				"bark":
					value = 0.7 + _noise((x + y / 12) / 4, y / 24, 19) * 0.28 + coarse * 0.05
					if (x + y / 10) % 12 == 0:
						value = 0.48
				"leaves":
					value = 0.74 + floorf(coarse * 3) * 0.08
					if (x + y / 2) % 12 < 2:
						value += 0.12
				"steel":
					value = 0.85 + coarse * 0.13
					if x % 32 == 0:
						value = 0.62
					elif x % 32 == 1:
						value = 1.04
					if x % 16 in [3, 4] and y % 16 in [3, 4]:
						value = 1.1
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
