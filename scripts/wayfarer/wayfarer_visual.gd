extends "res://scripts/characters/rigged_knight_visual.gd"

var equipment: Node

func _ready() -> void:
	materials = _make_materials()
	super._ready()
	equipment = preload("res://scripts/equipment/equipment_controller.gd").new()
	equipment.name = "VisualEquipment"
	add_child(equipment)
	equipment.initialize(self, skeleton)

func _make_materials() -> RefCounted:
	return preload("res://scripts/wayfarer/wayfarer_materials.gd").new()

func update_locomotion(delta: float, horizontal_speed: float) -> void:
	super.update_locomotion(delta, horizontal_speed)
	if not animation_enabled:
		return
	# Small visual-only finger curl. No attack/grip gameplay or new input path.
	for side in ["R", "L"]:
		var occupied: bool = equipment.get_equipped(&"main_hand" if side == "R" else &"off_hand") != &""
		for finger in ["Index", "Middle", "Ring", "Little"]:
			var index := skeleton.find_bone(finger + "_" + side)
			skeleton.set_bone_pose_rotation(index, Quaternion(Vector3.RIGHT, -0.65 if occupied else 0.0))
