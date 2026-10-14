extends RefCounted

const ROOT := "res://assets/characters/ashen_knight/textures/"
var materials: Array[StandardMaterial3D] = []
var textures: Array[Texture2D] = []
var normal_maps: Array[Texture2D] = []
var roughness_maps: Array[Texture2D] = []
var cache: Dictionary = {}

func apply(node: Node) -> void:
	if node is MeshInstance3D:
		for i in node.mesh.get_surface_count():
			var source: StandardMaterial3D = node.get_active_material(i)
			var kind := source.resource_name.trim_prefix("Oath_")
			if not cache.has(kind):
				var mat := source.duplicate() as StandardMaterial3D
				mat.albedo_color = Color.WHITE
				mat.albedo_texture = load(ROOT + kind + "_albedo.png")
				mat.normal_texture = load(ROOT + kind + "_normal.png")
				mat.roughness_texture = load(ROOT + kind + "_roughness.png")
				mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
				mat.normal_enabled = true
				mat.normal_scale = 0.3
				mat.metallic = 0.42 if kind in ["steel", "bronze", "mail"] else 0.0
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
				mat.cull_mode = BaseMaterial3D.CULL_DISABLED if kind == "cloth" else BaseMaterial3D.CULL_BACK
				cache[kind] = mat
				materials.append(mat)
				textures.append(mat.albedo_texture)
				normal_maps.append(mat.normal_texture)
				roughness_maps.append(mat.roughness_texture)
			node.set_surface_override_material(i, cache[kind])
	for child in node.get_children():
		apply(child)

func set_detail(enabled: bool) -> void:
	for i in materials.size():
		materials[i].albedo_texture = textures[i] if enabled else null
		materials[i].normal_enabled = enabled
		materials[i].normal_texture = normal_maps[i] if enabled else null
		materials[i].roughness_texture = roughness_maps[i] if enabled else null
