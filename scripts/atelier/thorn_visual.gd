extends "res://scripts/characters/rigged_knight_visual.gd"

func _ready() -> void:
	materials = preload("res://scripts/atelier/atlas_materials.gd").new()
	super._ready()
