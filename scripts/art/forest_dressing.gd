extends RefCounted

const Kit = preload("res://scripts/art/ruins_kit.gd")
const Meshes = preload("res://scripts/art/art_meshes.gd")
const Geo = preload("res://scripts/world/geometry.gd")

# Continuous verge height, zero on the original road and inside the chapel.
# Used by both the mesh and its decorations; collision comes from the same mesh.
static func ground_height(x: float, z: float) -> float:
	var verge := smoothstep(2.1, 4.4, absf(x))
	var extent := 1.0 - smoothstep(8.5, 11.0, absf(x))
	var ends := smoothstep(-13.0, -10.5, z) * (1.0 - smoothstep(10.0, 13.0, z))
	var church := 1.0 - (1.0 - smoothstep(5.8, 7.0, absf(x))) * (1.0 - smoothstep(-2.3, -0.8, z))
	var hills := 0.24 + 0.2 * sin(x * 0.82 + z * 0.39) + 0.13 * cos(z * 0.73 - x * 0.25)
	return maxf(0.0, hills) * verge * extent * ends * church

static func terrain(parent: Node3D, earth: Material) -> void:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for iz in 52:
		for ix in 44:
			var x := -11.0 + ix * 0.5
			var z := -13.0 + iz * 0.5
			var points: Array[Vector3] = []
			for offset in [Vector2(0, 0), Vector2(0.5, 0), Vector2(0.5, 0.5), Vector2(0, 0.5)]:
				var px: float = x + offset.x
				var pz: float = z + offset.y
				points.append(Vector3(px, ground_height(px, pz) + 0.003, pz))
			for i in [0, 1, 2, 0, 2, 3]:
				surface.add_vertex(points[i])
	surface.generate_normals()
	var mesh := surface.commit()
	var instance := Kit.piece(parent, Vector3.ZERO, mesh, earth)
	instance.name = "CoreVergeTerrain"
	var body := StaticBody3D.new()
	body.name = "CoreVergeCollision"
	var shape := CollisionShape3D.new()
	shape.shape = mesh.create_trimesh_shape()
	body.add_child(shape)
	instance.add_child(body)

static func tuft(parent: Node3D, at: Vector3, size: float, mat: Material, seed_value: int) -> void:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 9:
		var angle := i * 2.39996 + seed_value * 0.13
		var radius := sqrt(float(i) / 9.0) * size * 0.23
		var base := Vector3(cos(angle) * radius, 0, sin(angle) * radius)
		var axis := Vector3(cos(angle + 0.7), 0, sin(angle + 0.7))
		var height := size * (0.4 + 0.23 * sin(i * 1.7 + seed_value))
		var a := base - axis * size * 0.045
		var b := base + axis * size * 0.045
		var c := base + axis * size * 0.06 + Vector3.UP * height
		var normal := -((b - a).cross(c - a)).normalized()
		for p in [a, b, c]:
			surface.set_normal(normal)
			surface.add_vertex(p)
	var instance := Kit.piece(parent, at, surface.commit(), mat)
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

static func shrub(parent: Node3D, at: Vector3, size: float, dark: Material, light: Material, seed_value: int) -> void:
	# Overlapping rounded branch masses, deliberately larger than single-pixel leaves.
	for i in 5:
		var angle := i * 2.4 + seed_value * 0.37
		var radius := size * (0.23 + (i % 3) * 0.07)
		var center := Vector3(cos(angle) * size * 0.32, size * (0.09 + (i % 2) * 0.14), sin(angle) * size * 0.3)
		var mesh := Meshes.profile([Vector3(radius * 0.6, 0, radius * 0.6), Vector3(radius, radius * 0.5, radius * 0.85), Vector3(radius * 0.78, radius * 1.2, radius * 0.7), Vector3(radius * 0.24, radius * 1.5, radius * 0.25)], 7, 0.22)
		var instance := Kit.piece(parent, at + center, mesh, dark if i % 3 else light)
		instance.rotation.y = angle
	# Broad serrated sprays break the rounded masses into readable leaf silhouettes.
	var spray := SurfaceTool.new()
	spray.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 12:
		var angle := i * 2.4 + seed_value * 0.37
		var rotation := Basis(Vector3.UP, angle)
		var height := size * (0.32 + 0.18 * sin(i * 2.2))
		var center := Vector3(0, height, size * 0.4)
		var outline := [Vector3(0, 0, -0.17), Vector3(-0.1, 0.055, -0.07), Vector3(-0.07, 0.09, 0), Vector3(-0.12, 0.11, 0.07), Vector3(0, 0.18, 0.24), Vector3(0.12, 0.11, 0.07), Vector3(0.07, 0.09, 0), Vector3(0.1, 0.055, -0.07)]
		for j in outline.size():
			var a: Vector3 = rotation * (center + Vector3(0, 0.1, 0))
			var b: Vector3 = rotation * (center + outline[j] * size)
			var c: Vector3 = rotation * (center + outline[(j + 1) % outline.size()] * size)
			var normal := -((b - a).cross(c - a)).normalized()
			for point in [a, b, c]:
				spray.set_normal(normal)
				spray.add_vertex(point)
	Kit.piece(parent, at, spray.commit(), light)

static func branch(parent: Node3D, start: Vector3, end: Vector3, radius: float, mat: Material) -> void:
	var delta := end - start
	var length := delta.length()
	var mesh := Meshes.profile([Vector3(radius, 0, radius), Vector3(radius * 0.75, length * 0.45, radius * 0.7), Vector3(radius * 0.28, length, radius * 0.25)], 6, 0.1)
	var instance := Kit.piece(parent, start, mesh, mat)
	instance.quaternion = Quaternion(Vector3.UP, delta.normalized())

static func old_tree(parent: Node3D, at: Vector3, size: float, bark: Material, dark: Material, light: Material, seed_value: int) -> void:
	var module := Node3D.new()
	module.name = "OldForestTree"
	parent.add_child(module)
	module.position = at
	var lean := -0.3 if seed_value % 2 else 0.3
	var points := [Vector3.ZERO, Vector3(lean, size * 0.35, 0.05), Vector3(lean * 0.2, size * 0.65, 0.35), Vector3(lean * 2, size * 0.96, 0.2)]
	for i in 3:
		branch(module, points[i], points[i + 1], 0.32 - i * 0.065, bark)
	body_for_trunk(module)
	for i in 5:
		var angle := i * TAU / 5.0 + seed_value
		branch(module, Vector3(0, 0.28, 0), Vector3(cos(angle) * 0.95, 0.025, sin(angle) * 0.95), 0.19, bark)
	for i in 6:
		var angle := i * 2.4 + seed_value * 0.5
		var begin: Vector3 = points[1] if i < 3 else points[2]
		var tip := Vector3(cos(angle) * size * 0.3, size * (0.65 + 0.08 * (i % 3)), sin(angle) * size * 0.23)
		var bend := begin.lerp(tip, 0.6) - Vector3.UP * 0.25
		branch(module, begin, bend, 0.15, bark)
		branch(module, bend, tip, 0.09, bark)
		shrub(module, tip - Vector3.UP * 0.4, size * 0.4, dark, light, i + seed_value)

static func dress(parent: Node3D, earth: Material, stone: Material, pale: Material, bark: Material, dark: Material, leaf: Material, grass: Material, litter: Material) -> void:
	terrain(parent, earth)
	var random := RandomNumberGenerator.new()
	random.seed = 440817
	# Asymmetric islands, not a mirrored row or uniform random field.
	var islands := [Vector3(-4.2, 0, 10.5), Vector3(-7.2, 0, 8.8), Vector3(-4.2, 0, 6.8), Vector3(-5.6, 0, 3.4), Vector3(-6.7, 0, -0.2), Vector3(3.8, 0, 8.5), Vector3(5.8, 0, 5.0), Vector3(4.1, 0, 2.1), Vector3(6.7, 0, -1.5), Vector3(-7.7, 0, -6), Vector3(7.5, 0, -8)]
	for island_index in islands.size():
		var center: Vector3 = islands[island_index]
		for i in 6:
			var at := center + Vector3(random.randf_range(-1.2, 1.2), 0, random.randf_range(-1.35, 1.35))
			at.y = ground_height(at.x, at.z)
			shrub(parent, at, random.randf_range(0.7, 1.25), dark, leaf, i + island_index * 7)
		for i in 18:
			var at := center + Vector3(random.randf_range(-1.75, 1.75), 0, random.randf_range(-1.9, 1.9))
			at.y = ground_height(at.x, at.z) + 0.01
			tuft(parent, at, random.randf_range(0.45, 0.9), grass, i + island_index * 19)
		for i in 4:
			var at := center + Vector3(random.randf_range(-1.2, 1.2), 0, random.randf_range(-1.3, 1.3))
			at.y = ground_height(at.x, at.z) + 0.12
			var rock := Geo.rock(parent, at, Vector3(random.randf_range(0.7, 1.6), random.randf_range(0.65, 1.15), random.randf_range(0.6, 1.25)), stone if i % 2 else pale)
			rock.rotation.y = random.randf_range(0, TAU)
	# Leaf scatter lives in irregular patches; individual shapes are muted and broad.
	for i in 340:
		var center: Vector3 = islands[i % islands.size()]
		var at := center + Vector3(random.randf_range(-2, 2), 0, random.randf_range(-2.2, 2.2))
		if absf(at.x) < 2.25:
			continue
		at.y = ground_height(at.x, at.z) + 0.015
		var leaf_mesh := Meshes.profile([Vector3(0.03, 0, 0.1), Vector3(0.07, 0.015, 0.12), Vector3(0.02, 0.028, 0.08)], 4)
		var fallen := Kit.piece(parent, at, leaf_mesh, litter)
		fallen.rotation.y = random.randf_range(0, TAU)
		fallen.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for pair in [[Vector3(-7.4, 0, 2.5), 6.2], [Vector3(8.7, 0, -0.5), 6.5], [Vector3(-8.3, 0, -8), 6.5]]:
		var at: Vector3 = pair[0]
		at.y = ground_height(at.x, at.z)
		old_tree(parent, at, pair[1], bark, dark, leaf, int(at.z))
	# Fallen log and crumbling masonry anchor vegetation at the entrance.
	branch(parent, Vector3(-4.1, 0.28, 5.5), Vector3(-6.7, 0.45, 7.2), 0.3, bark)
	branch(parent, Vector3(-5.2, 0.38, 6.2), Vector3(-5.4, 0.7, 7.5), 0.1, bark)
	for side in [-1, 1]:
		for i in 7:
			var at := Vector3(side * (3.1 + random.randf_range(0, 1.8)), 0.17, random.randf_range(-0.5, 1.2))
			var chunk := Kit.block(parent, at, Vector3(random.randf_range(0.35, 0.85), random.randf_range(0.22, 0.45), random.randf_range(0.3, 0.7)), stone if i % 2 else pale)
			chunk.rotation = Vector3(0.12 * i, random.randf_range(-1, 1), 0.07 * i)

static func body_for_trunk(parent: Node3D) -> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.55, 2, 0.55)
	shape.shape = box
	shape.position.y = 1.0
	body.add_child(shape)
	parent.add_child(body)
