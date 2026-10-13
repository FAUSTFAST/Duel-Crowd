extends SceneTree

const Geo = preload("res://scripts/world/geometry.gd")
const Kit = preload("res://scripts/art/ruins_kit.gd")
const KnightModel = preload("res://scripts/art/knight_model.gd")
const Materials = preload("res://scripts/rendering/pixel_materials.gd")

func _initialize() -> void:
	call_deferred("_bake")

func _material(color: String, kind: String, scale_value: float = 0.7, local: bool = false) -> StandardMaterial3D:
	var mat := Geo.material(Color(color))
	Materials.apply(mat, kind, scale_value)
	mat.uv1_world_triplanar = not local
	if local and kind == "cloth":
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	if kind == "steel":
		mat.metallic = 0.3 if color == "a5afac" else (0.2 if color == "293339" else 0.5)
		if color == "a5afac":
			mat.roughness = 0.7
	return mat

func _save(node: Node3D, path: String) -> void:
	for child in node.find_children("*", "", true, false):
		child.owner = node
	var scene := PackedScene.new()
	var result := scene.pack(node)
	if result == OK:
		result = ResourceSaver.save(scene, path, ResourceSaver.FLAG_COMPRESS)
	print("Library ", path, ": ", result)
	if result != OK:
		quit(1)
	node.free()

func _bake() -> void:
	var portal := Node3D.new()
	portal.name = "ChapelPortalModule"
	root.add_child(portal)
	Kit.portal(portal, _material("626966", "granite"), _material("85867a", "granite"), _material("8e7950", "steel", 1), _material("742f3b", "cloth", 1))
	Kit.batch_static(portal)
	_save(portal, "res://assets/models/chapel_portal.scn")
	var tree := Node3D.new()
	tree.name = "PineModule"
	root.add_child(tree)
	Kit.tree(tree, Vector3.ZERO, 5, _material("504331", "bark", 1), _material("213b30", "leaves", 0.55), _material("3e5640", "leaves", 0.55), 1)
	Kit.batch_static(tree)
	_save(tree, "res://assets/models/pine.scn")
	var knight := Node3D.new()
	knight.name = "KnightVisualModule"
	root.add_child(knight)
	KnightModel.build(knight, _material("a5afac", "steel", 1.5, true), _material("293339", "steel", 1.5, true), _material("792d3e", "cloth", 1.5, true), _material("9d8151", "steel", 1.5, true))
	_save(knight, "res://assets/models/knight_visual.scn")
	quit()
