extends "res://scripts/valley/valley_world.gd"
## Independent playable motion review. Forest Valley's original scene stays intact.
func _ready() -> void:
	super._ready()
	player.visual.free()
	player.visual_scene = preload("res://scenes/characters/silhouette_visual.tscn")
	player._build_visual()
	player.orbit.distance = 5.2
	player.orbit.pitch = -.32
