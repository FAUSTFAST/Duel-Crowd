extends "res://scripts/characters/knight.gd"

@export var visual_scene: PackedScene = preload("res://scenes/characters/ashen_knight_visual.tscn")
var study_materials: RefCounted

func _build_visual() -> void:
	visual = visual_scene.instantiate()
	add_child(visual)
	study_materials = visual.materials
	detailed_materials = study_materials.materials
	material_textures = study_materials.textures

func _animate_visual(delta: float) -> void:
	visual.update_locomotion(delta, Vector2(velocity.x, velocity.z).length())

func set_visual_animation_enabled(enabled: bool) -> void:
	visual.set_animation_enabled(enabled)
