extends "res://scripts/characters/knight.gd"

const Materials = preload("res://scripts/valley/valley_materials.gd")
var study_materials := Materials.new()

func _ready() -> void:
	super._ready()
	# Replace only the visual. Movement, capsule, camera and limb animation remain inherited.
	remove_child(visual)
	visual.free()
	visual = preload("res://assets/valley/models/knight_study.glb").instantiate()
	add_child(visual)
	left_leg = visual.find_child("LeftLeg", true, false)
	right_leg = visual.find_child("RightLeg", true, false)
	left_arm = visual.find_child("LeftArm", true, false)
	right_arm = visual.find_child("RightArm", true, false)
	study_materials.apply(visual)
	detailed_materials = study_materials.materials
	material_textures = study_materials.textures
