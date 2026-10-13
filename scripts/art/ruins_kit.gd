extends RefCounted

const Geo = preload("res://scripts/world/geometry.gd")
const Meshes = preload("res://scripts/art/art_meshes.gd")

static func piece(parent: Node3D, at: Vector3, mesh: Mesh, material: Material) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = material
	parent.add_child(instance)
	instance.position = at
	return instance

static func block(parent: Node3D, at: Vector3, size: Vector3, mat: Material, solid: bool = false) -> MeshInstance3D:
	var result := Geo.box(parent, at, size, mat, solid)
	result.mesh = Meshes.bevel_box(size, 0.055)
	return result

static func portal(parent: Node3D, stone: Material, pale: Material, iron: Material, cloth: Material) -> void:
	var module := Node3D.new()
	module.name = "ChapelPortal"
	parent.add_child(module)
	module.position.z = -2.0
	for side in [-1, 1]:
		block(module, Vector3(side * 1.8, 0.18, 0), Vector3(0.95, 0.36, 1.15), pale)
		block(module, Vector3(side * 1.8, 2.23, 0), Vector3(0.88, 0.26, 1.06), pale)
		block(module, Vector3(side * 1.8, 3.38, 0), Vector3(0.92, 0.2, 1.05), pale)
		# Five wedge-like voussoirs form a pointed original gothic opening.
		var points := [Vector2(side * 1.43, 2.22), Vector2(side * 1.32, 2.56), Vector2(side * 1.12, 2.88), Vector2(side * 0.84, 3.15), Vector2(side * 0.45, 3.4), Vector2(0, 3.65)]
		for i in points.size() - 1:
			var start: Vector2 = points[i]
			var finish: Vector2 = points[i + 1]
			var middle := (start + finish) * 0.5
			var arch := block(module, Vector3(middle.x, middle.y, 0.2), Vector3(start.distance_to(finish) + 0.025, 0.27, 1.02), pale)
			arch.rotation.z = (finish - start).angle()
		# Outside buttresses and caps do not intrude into the walkable doorway.
		for tier in 3:
			block(module, Vector3(side * 4.25, 0.35 + tier * 0.65, 0.25 - tier * 0.08), Vector3(0.9 - tier * 0.15, 0.64, 1.35 - tier * 0.22), stone)
		block(module, Vector3(side * 3.25, 2.17, 0), Vector3(2.5, 0.22, 0.97), pale)
		# Timber bracket and torn burgundy hanging banner.
		Geo.box(module, Vector3(side * 3.1, 2.8, 0.53), Vector3(0.62, 0.07, 0.08), iron)
		piece(module, Vector3(side * 3.1, 1.98, 0.56), Meshes.profile([Vector3(0.17, -0.55, 0.015), Vector3(0.32, -0.3, 0.025), Vector3(0.32, 0.78, 0.025)], 4), cloth)
	block(module, Vector3(0, 3.7, 0.34), Vector3(0.34, 0.55, 1.16), stone)
	var sigil := Geo.box(module, Vector3(0, 3.75, 0.94), Vector3(0.12, 0.23, 0.035), iron)
	sigil.rotation.z = PI / 4
	# Broken upper lancet: an asymmetric silhouette, with sky visible through it.
	for side in [-1, 1]:
		for row in 4:
			block(module, Vector3(3.25 + side * 0.64, 2.48 + row * 0.4, -0.1), Vector3(0.4, 0.38, 0.7), stone if row % 2 else pale)
		var arch_stone := block(module, Vector3(3.25 + side * 0.37, 4.04, -0.1), Vector3(0.83, 0.32, 0.74), pale)
		arch_stone.rotation.z = -side * 0.71
	block(module, Vector3(3.25, 4.34, -0.1), Vector3(0.3, 0.4, 0.76), stone)
	# Shallow layered stone bands, repaired joints and protruding broken cornices.
	for side in [-1, 1]:
		for row in 3:
			block(module, Vector3(side * 3.22, 0.43 + row * 0.57, 0.47), Vector3(2.3, 0.055, 0.07), pale)
		for row in 2:
			for offset in [2.66, 3.7]:
				block(module, Vector3(side * (offset + row * 0.18), 0.71 + row * 0.57, 0.48), Vector3(0.045, 0.51, 0.075), stone)
		for i in 3:
			var fragment := block(module, Vector3(side * (4.4 + i * 0.28), 2.47 - i * 0.08, -0.12), Vector3(0.4, 0.32, 0.87), stone)
			fragment.rotation.z = side * i * 0.055
	# Short ruined pilasters along the inner walls establish repeating modules.
	for side in [-1, 1]:
		for z in [-4.4, -7.2, -9.7]:
			block(parent, Vector3(side * 5.0, 0.15, z), Vector3(1.18, 0.3, 1.1), stone)
			block(parent, Vector3(side * 5.0, 1.15, z), Vector3(0.98, 2, 0.64), pale)
			block(parent, Vector3(side * 5.0, 2.2, z), Vector3(1.1, 0.18, 0.85), stone)

static func tree(parent: Node3D, at: Vector3, height: float, bark: Material, dark_leaf: Material, light_leaf: Material, index: int) -> void:
	var module := Node3D.new()
	module.name = "Pine_%02d" % index
	parent.add_child(module)
	module.position = at
	# Original collision footprint is retained; trunk silhouette tapers above it.
	var trunk := Geo.box(module, Vector3(0, height * 0.4, 0), Vector3(0.45, height * 0.8, 0.45), bark, true)
	trunk.mesh = Meshes.profile([Vector3(0.32, -height * 0.4, 0.29), Vector3(0.2, height * 0.1, 0.19), Vector3(0.07, height * 0.4, 0.07)], 7)
	for root_index in 4:
		var root_piece := block(module, Vector3(0, 0.08, 0), Vector3(0.8, 0.16, 0.15), bark)
		root_piece.rotation.y = root_index * PI / 2.0 + index * 0.2
	for tier in 5:
		var radius := (1.68 - tier * 0.26) * (0.9 + (index % 3) * 0.05)
		var h := height * 0.42
		var profile: Array[Vector3] = [Vector3(radius * 0.82, 0, radius * 0.78), Vector3(radius, h * 0.13, radius * 0.94), Vector3(radius * 0.42, h * 0.57, radius * 0.38), Vector3(0.025, h, 0.025)]
		var crown := piece(module, Vector3(0.12 * sin(tier + index), height * 0.36 + tier * height * 0.13, 0), Meshes.profile(profile, 9, 0.18), dark_leaf if tier % 2 == 0 else light_leaf)
		crown.rotation.y = tier * 0.65 + index * 0.29

static func fern(parent: Node3D, at: Vector3, scale_value: float, mat: Material) -> void:
	var module := Node3D.new()
	parent.add_child(module)
	module.position = at
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 7:
		var angle := i * TAU / 7.0
		var rotation := Basis(Vector3.UP, angle)
		for leaf in 5:
			var t := float(leaf + 1) / 6.0
			var stem := Vector3(0, sin(t * PI) * 0.4, t * 0.62)
			var width := sin(t * PI) * 0.18
			for side in [-1, 1]:
				var a := stem + Vector3(0, 0, -0.07)
				var b := stem + Vector3(side * width, 0.02, -0.08)
				var c := stem + Vector3(side * width * 0.35, 0.04, 0.065)
				if (b - a).cross(c - a).y > 0:
					var swap := b
					b = c
					c = swap
				var normal := -((b - a).cross(c - a)).normalized()
				for point in [a, b, c]:
					surface.set_normal(rotation * normal)
					surface.add_vertex(rotation * point * scale_value)
	var fronds := piece(module, Vector3.ZERO, surface.commit(), mat)
	fronds.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

# Merge only non-moving environment geometry by material and shadow policy.
# Collision bodies are reparented with transforms preserved before source cleanup.
static func batch_static(parent: Node3D) -> void:
	var groups: Dictionary = {}
	var meshes := parent.find_children("*", "MeshInstance3D", true, false)
	for item in meshes:
		var instance := item as MeshInstance3D
		if instance.mesh == null:
			continue
		var key := "%s:%d" % [instance.material_override.get_instance_id(), instance.cast_shadow]
		if not groups.has(key):
			var surface := SurfaceTool.new()
			surface.begin(Mesh.PRIMITIVE_TRIANGLES)
			groups[key] = [surface, instance.material_override, instance.cast_shadow]
		for index in instance.mesh.get_surface_count():
			# Never mix indexed and non-indexed input in one SurfaceTool.
			var source := SurfaceTool.new()
			source.create_from(instance.mesh, index)
			source.deindex()
			groups[key][0].append_from(source.commit(), 0, parent.global_transform.affine_inverse() * instance.global_transform)
		for child in instance.get_children():
			child.reparent(parent, true)
		instance.free()
	for key in groups:
		var instance := MeshInstance3D.new()
		instance.name = "StaticArtBatch"
		groups[key][0].index()
		instance.mesh = groups[key][0].commit()
		instance.material_override = groups[key][1]
		instance.cast_shadow = groups[key][2]
		parent.add_child(instance)
