extends SceneTree

const Geo = preload("res://scripts/world/geometry.gd")
const Kit = preload("res://scripts/art/ruins_kit.gd")
const Dressing = preload("res://scripts/art/forest_dressing.gd")
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
		mat.metallic = 0.3 if color == "b6c1b9" else (0.2 if color == "293339" else 0.5)
		if color == "b6c1b9":
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
	var old_tree := Node3D.new()
	old_tree.name = "OldTreeModule"
	root.add_child(old_tree)
	var old_leaf := _material("657247", "leaves", 0.65)
	old_leaf.cull_mode = BaseMaterial3D.CULL_DISABLED
	Dressing.old_tree(old_tree, Vector3.ZERO, 6.2, _material("504331", "bark", 1), _material("2e4532", "leaves", 0.65), old_leaf, 2)
	Kit.batch_static(old_tree)
	_save(old_tree, "res://assets/models/old_tree.scn")
	var shrub := Node3D.new()
	shrub.name = "ShrubModule"
	root.add_child(shrub)
	var leaf := _material("657247", "leaves", 0.65)
	leaf.cull_mode = BaseMaterial3D.CULL_DISABLED
	Dressing.shrub(shrub, Vector3.ZERO, 1.1, _material("2e4532", "leaves", 0.65), leaf, 4)
	Kit.batch_static(shrub)
	_save(shrub, "res://assets/models/shrub.scn")
	var knight := Node3D.new()
	knight.name = "KnightVisualModule"
	root.add_child(knight)
	KnightModel.build(knight, _material("b6c1b9", "steel", 1.5, true), _material("293339", "steel", 1.5, true), _material("91394b", "cloth", 1.5, true), _material("b1945e", "steel", 1.5, true))
	_save(knight, "res://assets/models/knight_visual.scn")
	quit()
