extends RefCounted

const ROOT := "res://assets/valley/textures/"
const TYPES := {"ValleyBark": "bark", "ValleySlate": "slate", "StudySteel": "steel", "StudyCloth": "cloth", "StudyLeather": "leather", "ValleyLeaf": "leaf_spray"}
var materials: Array[StandardMaterial3D] = []
var textures: Array[Texture2D] = []
var normal_maps: Array[Texture2D] = []
var roughness_maps: Array[Texture2D] = []
var cache: Dictionary = {}

func apply(root: Node) -> void:
	if root is MeshInstance3D:
		for i in root.mesh.get_surface_count():
			var source: Material = root.get_active_material(i)
			if source is StandardMaterial3D:
				root.set_surface_override_material(i, _material(source))
	for child in root.get_children():
		apply(child)

func _material(source: StandardMaterial3D) -> StandardMaterial3D:
	var key := source.resource_name
	if cache.has(key):
		return cache[key]
	var mat := source.duplicate() as StandardMaterial3D
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	mat.uv1_world_triplanar = false
	mat.roughness = 0.88
	if TYPES.has(key):
		var kind: String = TYPES[key]
		var albedo_path := ROOT + kind + (".png" if kind == "leaf_spray" else "_albedo.png")
		mat.albedo_texture = load(albedo_path)
		mat.albedo_color = Color.WHITE
		if ResourceLoader.exists(ROOT + kind + "_normal.png"):
			mat.normal_texture = load(ROOT + kind + "_normal.png")
			mat.normal_enabled = true
			mat.normal_scale = 0.45
			mat.roughness_texture = load(ROOT + kind + "_roughness.png")
			mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
		if kind == "leaf_spray":
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			mat.alpha_scissor_threshold = 0.4
			mat.cull_mode = BaseMaterial3D.CULL_DISABLED
			mat.roughness = 0.95
		elif kind == "cloth":
			mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		elif kind == "steel":
			mat.metallic = 0.35
			mat.roughness = 0.65
			mat.albedo_color = Color("8d9b9c")
	if key == "ValleyGrass" or key == "ValleyFlower":
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		mat.albedo_color = Color("526643") if key == "ValleyGrass" else Color("a58ba6")
	cache[key] = mat
	materials.append(mat)
	textures.append(mat.albedo_texture)
	normal_maps.append(mat.normal_texture)
	roughness_maps.append(mat.roughness_texture)
	return mat

func set_detail(enabled: bool) -> void:
	for i in materials.size():
		# Keep foliage's cutout silhouette: albedo alpha is geometry, not noise.
		var is_leaf := materials[i].transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
		materials[i].albedo_texture = textures[i] if enabled or is_leaf else null
		materials[i].normal_enabled = enabled and normal_maps[i] != null
		materials[i].normal_texture = normal_maps[i] if enabled else null
		materials[i].roughness_texture = roughness_maps[i] if enabled else null
