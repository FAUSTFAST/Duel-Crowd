extends "res://scripts/preview/local_model_preview.gd"

func _ready() -> void:
	super._ready()
	get_window().title = "Mutsumi Motion Study - Local Preview"

func _update_model_note() -> void:
	if not is_instance_valid(model_note):
		return
	if not world.load_error.is_empty():
		model_note.text = world.load_error
	else:
		var state: String = world.motion.current_state if world.motion != null else "loading"
		model_note.text = "MUTSUMI  /  LOCAL MOTION STUDY  /  %s\nWASD  Walk  |  Shift  Jog  |  Tab  %s\nOriginal test animations. No slope foot IK or cloth physics." % [state.to_upper(), "Play Mutsumi" if world.inspecting else "Inspect"]
