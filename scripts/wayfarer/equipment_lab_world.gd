extends "res://scripts/atelier/atelier_world.gd"

## Independent fixture only. Old maps and both old knight candidates stay intact.
signal pose_changed
var equipment: Node
var pose_index := 0
@export var character_visual: PackedScene = preload("res://scenes/characters/wayfarer_visual.tscn")

func _ready() -> void:
	var input_source := preload("res://scripts/valley/valley_world.gd").new()
	input_source._setup_input()
	input_source.free()
	_lighting()
	_floor()
	player = preload("res://scripts/atelier/atelier_player.gd").new()
	player.name = "ClothedWayfarer"
	player.visual_scene = character_visual
	player.spawn_point = Vector3(0, 0.05, 0)
	player.position = player.spawn_point
	add_child(player)
	equipment = player.visual.equipment
	player.orbit.min_distance = 2.6
	player.orbit.distance = 4.0
	player.orbit.yaw = PI + 0.3
	player.orbit.pitch = -0.20

func toggle_item(id: StringName) -> void:
	var item: Resource = equipment.catalog[id]
	if equipment.get_equipped(item.slot) == id:
		equipment.unequip(item.slot)
	else:
		equipment.equip(id)

func cycle_pose() -> void:
	pose_index = (pose_index + 1) % 4
	player.preview_speed = [-1.0, 0.0, 3.2, 5.8][pose_index]
	pose_changed.emit()

func _unhandled_input(event: InputEvent) -> void:
	if event is not InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_1: toggle_item(&"study_helmet")
		KEY_2: toggle_item(&"study_chest")
		KEY_3: toggle_item(&"study_sword")
		KEY_4: toggle_item(&"study_shield")
		KEY_0: equipment.clear()
		KEY_P: cycle_pose()
		KEY_L: set_forest_light(not forest_light)
		_: return
	get_viewport().set_input_as_handled()
