extends "res://scripts/wayfarer/wayfarer_visual.gd"
## Independent reference likeness study. Never replaces the accepted player.
func _ready() -> void:
	super._ready()
	# Resource copies prevent changing the catalog used by the original lab.
	for id in equipment.catalog:
		var item: Resource = equipment.catalog[id].duplicate()
		var basename: String = String(id).trim_prefix("study_")
		item.model = load("res://assets/characters/reference_silhouette/equipment/" + basename + ".glb")
		equipment.catalog[id] = item
