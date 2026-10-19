extends "res://scripts/wayfarer/contact_locomotion.gd"
## Independent reference likeness study. Never replaces the accepted player.
func _ready() -> void:
	super._ready()
	var controller := get_parent()
	if "locomotion_profile" in controller:
		controller.locomotion_profile = preload("res://scripts/wayfarer/locomotion_profile.gd").new()
		controller.walk_speed = controller.locomotion_profile.walk_speed
		controller.run_speed = controller.locomotion_profile.run_speed
	# Resource copies prevent changing the catalog used by the original lab.
	for id in equipment.catalog:
		var item: Resource = equipment.catalog[id].duplicate()
		var basename: String = String(id).trim_prefix("study_")
		item.model = load("res://assets/characters/reference_silhouette/equipment/" + basename + ".glb")
		equipment.catalog[id] = item
