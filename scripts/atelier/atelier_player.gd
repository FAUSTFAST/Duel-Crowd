extends "res://scripts/valley/valley_knight.gd"

# Inspection belongs to this independent lab, never to production control.
var preview_speed := -1.0

func _animate_visual(delta: float) -> void:
	if preview_speed >= 0:
		visual.update_locomotion(delta, preview_speed)
	else:
		super._animate_visual(delta)
