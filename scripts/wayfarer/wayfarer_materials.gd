extends "res://scripts/characters/knight_materials.gd"

var detail_enabled := true
var texture_root := "res://assets/characters/wayfarer/textures/"

func apply(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in node.mesh.get_surface_count():
			var source := node.get_active_material(surface) as StandardMaterial3D
			var key := String(source.resource_name)
			if not cache.has(key):
				var mat := source.duplicate() as StandardMaterial3D
				var texture_path := texture_root + key.trim_prefix("Way_") + "_albedo.png"
				if ResourceLoader.exists(texture_path):
					mat.albedo_texture = load(texture_path)
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
				mat.roughness = {"Way_steel": 0.63, "Way_bronze": 0.55, "Way_leather": 0.84}.get(key, source.roughness if key.begins_with("Way_pattern_") else 0.92)
				mat.metallic = {"Way_steel": 0.38, "Way_bronze": 0.65}.get(key, source.metallic if key.begins_with("Way_pattern_") else 0.0)
				var rough_path := texture_root + key.trim_prefix("Way_") + "_roughness.png"
				var rough: Texture2D
				if ResourceLoader.exists(rough_path):
					rough = load(rough_path)
					mat.roughness_texture = rough
					mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
				cache[key] = mat
				materials.append(mat)
				textures.append(mat.albedo_texture)
				normal_maps.append(null)
				roughness_maps.append(rough)
			node.set_surface_override_material(surface, cache[key])
	for child in node.get_children():
		apply(child)
	set_detail(detail_enabled)

func set_detail(enabled: bool) -> void:
	detail_enabled = enabled
	for i in materials.size():
		materials[i].albedo_texture = textures[i] if enabled else null
		materials[i].roughness_texture = roughness_maps[i] if enabled else null
