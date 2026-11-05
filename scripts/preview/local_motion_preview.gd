extends "res://scripts/preview/local_model_preview.gd"

var _pixel_presentation: Material

func _layout() -> void:
	super._layout()
	if not is_instance_valid(display):
		return
	if _pixel_presentation == null and display.material != null:
		_pixel_presentation = display.material
	# Only this experiment defaults to native output; shared pixel scenes stay intact.
	display.material = _pixel_presentation if pixel_enabled else null
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if pixel_enabled else CanvasItem.TEXTURE_FILTER_LINEAR
	viewport.msaa_3d = Viewport.MSAA_DISABLED if pixel_enabled else Viewport.MSAA_4X

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
		model_note.text = "MUTSUMI  /  LOCAL MOTION STUDY  /  %s\nWASD  Walk  |  Shift  Jog  |  Tab  %s\nNative 3D by default. Materials are a simplified source approximation." % [state.to_upper(), "Play Mutsumi" if world.inspecting else "Inspect"]
