extends "res://scripts/characters/knight_materials.gd"

var detail_enabled := true

func apply(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in node.mesh.get_surface_count():
			var source := node.get_active_material(surface) as StandardMaterial3D
			var key := String(source.resource_name)
			if not cache.has(key):
				var mat := source.duplicate() as StandardMaterial3D
				var texture_path := "res://assets/characters/wayfarer/textures/" + key.trim_prefix("Way_") + "_albedo.png"
				if ResourceLoader.exists(texture_path):
					mat.albedo_texture = load(texture_path)
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
				mat.roughness = 0.63 if key == "Way_steel" else (0.84 if key == "Way_leather" else 0.92)
				mat.metallic = 0.38 if key == "Way_steel" else 0.0
				cache[key] = mat
				materials.append(mat)
				textures.append(mat.albedo_texture)
				normal_maps.append(null)
				roughness_maps.append(null)
			node.set_surface_override_material(surface, cache[key])
	for child in node.get_children():
		apply(child)
	set_detail(detail_enabled)

func set_detail(enabled: bool) -> void:
	detail_enabled = enabled
	for i in materials.size():
		materials[i].albedo_texture = textures[i] if enabled else null
