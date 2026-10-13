extends RefCounted

# Original reusable low-poly mesh primitives; metre-based dimensions.
static func bevel_box(size: Vector3, bevel: float = 0.04) -> ArrayMesh:
	var half := size * 0.5
	var inset := minf(bevel, minf(half.x, minf(half.y, half.z)) * 0.45)
	var inner := half - Vector3.ONE * inset
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for axis in 3:
		var u := (axis + 1) % 3
		var v := (axis + 2) % 3
		for sign_value in [-1, 1]:
			var corners: Array[Vector3] = []
			for pair in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
				var point := Vector3.ZERO
				point[axis] = sign_value * half[axis]
				point[u] = pair.x * inner[u]
				point[v] = pair.y * inner[v]
				corners.append(point)
			_quad(surface, corners, Vector3.ZERO)
	# Twelve bevel strips.
	for axis in 3:
		var u := (axis + 1) % 3
		var v := (axis + 2) % 3
		for su in [-1, 1]:
			for sv in [-1, 1]:
				var corners: Array[Vector3] = []
				for pair in [Vector2(-1, 0), Vector2(1, 0), Vector2(1, 1), Vector2(-1, 1)]:
					var point := Vector3.ZERO
					point[axis] = pair.x * inner[axis]
					point[u] = su * (half[u] if pair.y == 0 else inner[u])
					point[v] = sv * (inner[v] if pair.y == 0 else half[v])
					corners.append(point)
				_quad(surface, corners, Vector3.ZERO)
	for sx in [-1, 1]:
		for sy in [-1, 1]:
			for sz in [-1, 1]:
				_triangle(surface, Vector3(sx * half.x, sy * inner.y, sz * inner.z), Vector3(sx * inner.x, sy * half.y, sz * inner.z), Vector3(sx * inner.x, sy * inner.y, sz * half.z), Vector3.ZERO)
	surface.generate_normals()
	return surface.commit()

# Each profile is (x radius, y height, z radius). Flat faces give readable planes.
static func profile(rings: Array[Vector3], sides: int = 8, irregularity: float = 0.0) -> ArrayMesh:
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	var center := Vector3(0, (rings[0].y + rings[-1].y) * 0.5, 0)
	for row in rings.size() - 1:
		for i in sides:
			_quad(surface, [_point(rings[row], i, sides, irregularity), _point(rings[row], i + 1, sides, irregularity), _point(rings[row + 1], i + 1, sides, irregularity), _point(rings[row + 1], i, sides, irregularity)], center)
	for i in sides:
		_triangle(surface, Vector3(0, rings[0].y, 0), _point(rings[0], i, sides, irregularity), _point(rings[0], i + 1, sides, irregularity), center)
		_triangle(surface, Vector3(0, rings[-1].y, 0), _point(rings[-1], i + 1, sides, irregularity), _point(rings[-1], i, sides, irregularity), center)
	surface.generate_normals()
	return surface.commit()

static func _point(ring: Vector3, index: int, sides: int, irregularity: float) -> Vector3:
	var angle := TAU * index / sides + PI / sides
	var scale_value := 1.0 + sin(angle * 3.0 + ring.y * 2.0) * irregularity
	return Vector3(cos(angle) * ring.x * scale_value, ring.y, sin(angle) * ring.z * scale_value)

static func _quad(surface: SurfaceTool, points: Array, center: Vector3) -> void:
	_triangle(surface, points[0], points[1], points[2], center)
	_triangle(surface, points[0], points[2], points[3], center)

static func _triangle(surface: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, center: Vector3) -> void:
	# Godot front faces wind clockwise; orient each convex face away from centre.
	if (b - a).cross(c - a).dot((a + b + c) / 3.0 - center) > 0:
		var swap := b
		b = c
		c = swap
	for point in [a, b, c]:
		surface.add_vertex(point)
