extends "res://scripts/characters/knight_materials.gd"

const ATLAS_ROOT := "res://assets/characters/thorn_knight/textures/"

func apply(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in node.mesh.get_surface_count():
			var source := node.get_active_material(surface) as StandardMaterial3D
			var kind := source.resource_name.trim_prefix("Thorn_")
			if not cache.has(kind):
				var mat := source.duplicate() as StandardMaterial3D
				# Keep ivory legible under the existing valley daylight, not white.
				mat.albedo_color = Color("b9b09c") if kind == "cloth" else Color.WHITE
				mat.albedo_texture = load(ATLAS_ROOT + "equipment_albedo.png")
				mat.roughness_texture = load(ATLAS_ROOT + "equipment_roughness.png")
				mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
				mat.normal_enabled = false
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
				mat.cull_mode = BaseMaterial3D.CULL_DISABLED if kind == "cloth" else BaseMaterial3D.CULL_BACK
				cache[kind] = mat
				materials.append(mat)
				textures.append(mat.albedo_texture)
				roughness_maps.append(mat.roughness_texture)
			node.set_surface_override_material(surface, cache[kind])
	for child in node.get_children():
		apply(child)

func set_detail(enabled: bool) -> void:
	for i in materials.size():
		materials[i].albedo_texture = textures[i] if enabled else null
		materials[i].roughness_texture = roughness_maps[i] if enabled else null
