extends "res://scripts/valley/valley_world.gd"
## Independent playable motion review. Forest Valley's original scene stays intact.
func _ready() -> void:
	super._ready()
	player.visual.free()
	player.visual_scene = preload("res://scenes/characters/silhouette_visual.tscn")
	player._build_visual()
	player.orbit.distance = 5.2
	player.orbit.pitch = -.32

func _unhandled_input(event: InputEvent) -> void:
	if event is not InputEventKey or not event.pressed or event.echo: return
	var equipment: Node = player.visual.equipment
	if event.keycode == KEY_0:
		equipment.clear()
	elif event.keycode in [KEY_1,KEY_2,KEY_3,KEY_4]:
		var id: StringName = [&"study_helmet",&"study_chest",&"study_sword",&"study_shield"][event.keycode-KEY_1]
		var item: Resource = equipment.catalog[id]
		if equipment.get_equipped(item.slot)==id: equipment.unequip(item.slot)
		else: equipment.equip(id)
	else: return
	get_viewport().set_input_as_handled()
