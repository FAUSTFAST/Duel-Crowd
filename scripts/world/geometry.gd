extends RefCounted

static func material(color: Color, metallic: float = 0.0) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.albedo_color = color
	result.roughness = 0.9
	result.metallic = metallic
	return result

static func box(parent: Node3D, at: Vector3, size: Vector3, mat: Material, solid: bool = false) -> MeshInstance3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = mat
	parent.add_child(instance)
	instance.position = at
	if solid:
		var body := StaticBody3D.new()
		var shape := CollisionShape3D.new()
		var bounds := BoxShape3D.new()
		bounds.size = size
		shape.shape = bounds
		body.add_child(shape)
		instance.add_child(body)
	return instance

static func cone(parent: Node3D, at: Vector3, radius: float, height: float, mat: Material, top: float = 0.0) -> MeshInstance3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = top
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = 7
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.material_override = mat
	parent.add_child(instance)
	instance.position = at
	return instance

static func rock(parent: Node3D, at: Vector3, size: Vector3, mat: Material) -> MeshInstance3D:
	var corners := [Vector3(-0.5, 0, -0.35), Vector3(0.45, -0.1, -0.5), Vector3(0.5, 0, 0.3), Vector3(-0.35, 0.1, 0.5)]
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in 4:
		for point in [Vector3(0.05, 0.65, -0.05), corners[i], corners[(i + 1) % 4], Vector3(0, -0.45, 0), corners[(i + 1) % 4], corners[i]]:
			surface.add_vertex(point * size)
	surface.generate_normals()
	var instance := MeshInstance3D.new()
	instance.mesh = surface.commit()
	instance.material_override = mat
	parent.add_child(instance)
	instance.position = at
	return instance
