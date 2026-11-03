extends "res://scripts/rendering/pixel_renderer.gd"
## Separate local preview; shared renderer and its single input route are intact.

var model_note: Label

func _build_hud() -> void:
	super._build_hud()
	model_note = Label.new()
	model_note.position = Vector2(24, 150)
	model_note.add_theme_font_size_override("font_size", 14)
	model_note.add_theme_color_override("font_shadow_color", Color.BLACK)
	model_note.add_theme_constant_override("shadow_offset_x", 2)
	model_note.add_theme_constant_override("shadow_offset_y", 2)
	model_note.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(model_note)
	_update_model_note()

func _process(delta: float) -> void:
	super._process(delta)
	_update_model_note()

func _update_model_note() -> void:
	if not is_instance_valid(model_note):
		return
	if not world.load_error.is_empty():
		model_note.text = world.load_error
	else:
		model_note.text = "MUTSUMI  /  LOCAL STATIC PREVIEW\nTab  %s  |  Mouse / Wheel  Inspect\nNo walk/run clips. Materials approximated for Godot." % ("Explore with original knight" if world.inspecting else "Return to model inspection")
