extends Node

const WORLD_SCENE = preload("res://scenes/world/forest_ruins.tscn")
const RESOLUTIONS := [Vector2i(480, 270), Vector2i(640, 360), Vector2i(960, 540)]
@export var pixel_enabled: bool = true
@export_range(0, 2) var resolution_index: int = 1
@export var integer_scale: bool = true
var viewport: SubViewport
var display: TextureRect
var world: Node3D
var hud: CanvasLayer
var status: Label
var material_detail: bool = true
var presentation_rect := Rect2()
var _elapsed: float = 0.0

func _ready() -> void:
	var background := ColorRect.new()
	background.color = Color("0c1218")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)
	viewport = SubViewport.new()
	viewport.name = "WorldViewport"
	viewport.own_world_3d = true
	viewport.handle_input_locally = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.msaa_3d = Viewport.MSAA_DISABLED
	viewport.screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
	add_child(viewport)
	display = TextureRect.new()
	display.name = "PixelDisplay"
	display.texture = viewport.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var material := ShaderMaterial.new()
	material.shader = preload("res://shaders/pixel_present.gdshader")
	display.material = material
	add_child(display)
	_layout()
	world = WORLD_SCENE.instantiate()
	viewport.add_child(world)
	_build_hud()
	get_viewport().size_changed.connect(_layout)

func _layout() -> void:
	if not is_instance_valid(viewport):
		return
	var window_size := get_viewport().get_visible_rect().size
	presentation_rect = fit_rect(window_size, RESOLUTIONS[resolution_index], pixel_enabled and integer_scale)
	if not pixel_enabled:
		# Native comparison also uses whole physical pixels with exact 16:9.
		var units := floorf(minf(presentation_rect.size.x / 16.0, presentation_rect.size.y / 9.0))
		presentation_rect.size = Vector2(16, 9) * maxf(units, 1.0)
		presentation_rect.position = ((window_size - presentation_rect.size) * 0.5).floor()
	display.position = presentation_rect.position
	display.size = presentation_rect.size
	viewport.size = RESOLUTIONS[resolution_index] if pixel_enabled else Vector2i(presentation_rect.size)
	_refresh_status()

static func fit_rect(window_size: Vector2, render_size: Vector2i, whole_pixels: bool) -> Rect2:
	var ratio := minf(window_size.x / render_size.x, window_size.y / render_size.y)
	if whole_pixels and ratio >= 1.0:
		ratio = floorf(ratio)
	var dimensions := Vector2(render_size) * ratio
	return Rect2(((window_size - dimensions) * 0.5).floor(), dimensions)

func set_pixel_enabled(enabled: bool) -> void:
	pixel_enabled = enabled
	_layout()

func set_resolution(index: int) -> void:
	resolution_index = clampi(index, 0, RESOLUTIONS.size() - 1)
	_layout()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_F1:
				set_pixel_enabled(not pixel_enabled)
			KEY_F2:
				set_resolution((resolution_index + 1) % RESOLUTIONS.size())
			KEY_F3:
				material_detail = not material_detail
				world.set_material_detail(material_detail)
			KEY_F4:
				world.environment.fog_enabled = not world.environment.fog_enabled
			KEY_F6:
				integer_scale = not integer_scale
				_layout()
			KEY_MINUS, KEY_EQUAL:
				var direction := -1.0 if event.keycode == KEY_MINUS else 1.0
				world.environment.ambient_light_energy = clampf(world.environment.ambient_light_energy + direction * 0.05, 0.05, 0.8)
			_:
				_forward_input(event)
				return
		_refresh_status()
		get_viewport().set_input_as_handled()
		return
	_forward_input(event)

func _forward_input(event: InputEvent) -> void:
	# One explicit route: no SubViewportContainer automatic forwarding.
	# screen_relative is preserved, so look sensitivity is resolution-independent.
	if event is InputEventMouseButton and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		if not presentation_rect.has_point(event.position):
			return
	viewport.push_input(event, true)
	get_viewport().set_input_as_handled()

func _build_hud() -> void:
	hud = CanvasLayer.new()
	hud.name = "HD_UI"
	add_child(hud)
	var panel := ColorRect.new()
	panel.color = Color(0.03, 0.05, 0.07, 0.85)
	panel.position = Vector2(24, 24)
	panel.size = Vector2(478, 116)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(panel)
	var title := Label.new()
	title.text = "ASHEN OATH  /  THE FORSAKEN CHAPEL"
	title.position = Vector2(38, 34)
	title.add_theme_color_override("font_color", Color("d7cba7"))
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(title)
	var help := Label.new()
	help.text = "WASD  Move   Shift  Run   Mouse  Orbit   Wheel  Zoom\nEsc  Release mouse   Click  Capture   R  Reset"
	help.position = Vector2(38, 63)
	help.add_theme_font_size_override("font_size", 14)
	help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(help)
	status = Label.new()
	status.position = Vector2(38, 105)
	status.add_theme_font_size_override("font_size", 13)
	status.add_theme_color_override("font_color", Color("a0b6b5"))
	status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(status)
	var debug := Label.new()
	debug.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	debug.offset_left = 24
	debug.offset_right = 650
	debug.offset_top = -62
	debug.offset_bottom = -12
	debug.text = "F1  Pixel on/off    F2  Resolution    F3  Texture detail\nF4  Fog    F6  Integer/fit scale    -/+  Ambient light"
	debug.add_theme_font_size_override("font_size", 14)
	debug.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(debug)
	_refresh_status()

func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed > 0.5:
		_elapsed = 0
		_refresh_status()

func _refresh_status() -> void:
	if not is_instance_valid(status):
		return
	status.text = "%s %d×%d  |  %s  |  %d FPS" % ["PIXEL" if pixel_enabled else "NATIVE", viewport.size.x, viewport.size.y, "INTEGER" if integer_scale and pixel_enabled else "FIT", Engine.get_frames_per_second()]
