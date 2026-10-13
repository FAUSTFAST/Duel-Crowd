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
					# Wrapped curved mineral patches avoid a grid of square moss stamps.
					var patch := sin(x * TAU / 32.0 + sin(y * TAU / 64.0) * 1.8) + cos(y * TAU / 64.0 - sin(x * TAU / 64.0))
					value = 0.85 + floorf(coarse * 3) * 0.045
					if patch > 1.25:
						tint = Color(0.75, 0.86, 0.6)
						value -= 0.1
					elif patch > 0.9:
						tint = Color(0.88, 0.95, 0.76)
					var crack := (x + y / 3 + int(sin(y * 0.18) * 3) + 64) % 47
					if crack < 1 and y > 16 and y < 43:
						value = 0.58
					elif crack == 1 and y > 16 and y < 43:
						value = 1.0
				"grass":
					value = 0.77 + coarse * 0.15
					if (x + y / 3) % 11 < 2 and y % 16 > 4:
						value = 1.02
						tint = Color(0.9, 1.0, 0.76)
				"wood":
					var grain := x + int(sin(y * TAU / 64.0 + x * 0.3) * 2)
					value = 0.78 + _noise(grain / 4, y / 32, 19) * 0.19
					if grain % 17 == 0:
						value = 0.53
					var knot := pow((x - 38.0) / 7.0, 2) + pow((y - 31.0) / 12.0, 2)
					if knot < 1.0:
						value -= 0.12 if knot > 0.55 else 0.21
				"earth":
					var patch := _smooth_noise(x, y, 16, 43) * 0.65 + _smooth_noise(x, y, 8, 25) * 0.35
					value = 0.82 + floorf(patch * 5) * 0.04
					if patch > 0.64:
						tint = Color(0.9, 0.97, 0.78)
					elif patch < 0.38:
						tint = Color(1.01, 0.94, 0.83)
					if _noise(x / 2, y / 2, 23) > 0.95:
						value -= 0.09
				"bark":
					value = 0.7 + _noise((x + y / 12) / 4, y / 24, 19) * 0.28 + coarse * 0.05
					if (x + y / 10) % 12 == 0:
						value = 0.48
				"leaves":
					value = 0.72 + floorf(coarse * 4) * 0.075
					if sin(x * TAU / 32.0 + sin(y * TAU / 32.0)) + cos(y * TAU / 16.0) > 1.25:
						value += 0.1
				"steel":
					value = 0.83 + floorf(_smooth_noise(x, y, 16, 32) * 4) * 0.05
					if x % 32 == 0:
						value = 0.64
					elif x % 32 == 1:
						value = 1.08
					if x % 32 in [4, 5] and y % 32 in [4, 5]:
						value = 1.13
					if y % 27 == 8 and x > 16 and x < 28:
						value -= 0.09
				"cloth":
					value = 0.8 + _noise(x / 4, 0, 13) * 0.18
			image.set_pixel(x, y, Color(tint.r * value, tint.g * value, tint.b * value))
	image.generate_mipmaps()
	var result := ImageTexture.create_from_image(image)
	cache[kind] = result
	return result

# Periodic interpolated clusters: tileable without sine stripes or square stamps.
static func _smooth_noise(x: int, y: int, cell: int, seed_value: int) -> float:
	var ix: int = x / cell
	var iy: int = y / cell
	var period: int = 64 / cell
	var fx := smoothstep(0.0, 1.0, float(x % cell) / cell)
	var fy := smoothstep(0.0, 1.0, float(y % cell) / cell)
	var a := lerpf(_noise(ix % period, iy % period, seed_value), _noise((ix + 1) % period, iy % period, seed_value), fx)
	var b := lerpf(_noise(ix % period, (iy + 1) % period, seed_value), _noise((ix + 1) % period, (iy + 1) % period, seed_value), fx)
	return lerpf(a, b, fy)

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
