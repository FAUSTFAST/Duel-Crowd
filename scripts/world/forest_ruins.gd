extends Node3D

const Geo = preload("res://scripts/world/geometry.gd")
const Knight = preload("res://scripts/characters/knight.gd")
var player: CharacterBody3D
var rng := RandomNumberGenerator.new()

func _ready() -> void:
	rng.seed = 731104
	_setup_input()
	_environment()
	_build_world()
	player = Knight.new()
	player.name = "Knight"
	add_child(player)
	player.position = player.spawn_point
	_ui()

func _setup_input() -> void:
	var bindings := {"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT], "move_forward": [KEY_W, KEY_UP], "move_back": [KEY_S, KEY_DOWN], "sprint": [KEY_SHIFT], "reset": [KEY_R]}
	for action in bindings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for key in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = key
			if not InputMap.action_has_event(action, event):
				InputMap.action_add_event(action, event)

func _environment() -> void:
	var world := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("303f48")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8299a8")
	env.ambient_light_energy = 0.3
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color("53686d")
	env.fog_density = 0.014
	world.environment = env
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -32, 0)
	sun.light_color = Color("bec5b5")
	sun.light_energy = 0.7
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 55
	add_child(sun)

func _build_world() -> void:
	var earth := Geo.material(Color("34463c"))
	var stone := Geo.material(Color("616b6b"))
	var pale := Geo.material(Color("78817b"))
	var road := Geo.material(Color("686459"))
	var bark := Geo.material(Color("40362c"))
	var needles := Geo.material(Color("233c36"))
	var moss := Geo.material(Color("425947"))
	Geo.box(self, Vector3(0, -0.3, 0), Vector3(42, 0.6, 42), earth, true)
	for i in range(18):
		for j in range(3):
			var slab := Geo.box(self, Vector3((j - 1) * 1.15 + rng.randf_range(-0.08, 0.08), 0.035, 13 - i * 1.4), Vector3(1.05, 0.07, 1.27), road)
			slab.rotation.y = rng.randf_range(-0.05, 0.05)
	# Broken chapel side walls and interrupted facade; central entrance remains open.
	for side in [-1, 1]:
		for segment in range(7):
			var levels := rng.randi_range(2, 4)
			for row in range(levels):
				Geo.box(self, Vector3(side * 5.0, 0.4 + row * 0.8, -2 - segment * 1.25), Vector3(0.8, 0.76, 1.2), stone if row % 2 == 0 else pale, true)
		for x in range(3):
			Geo.box(self, Vector3(side * (2.3 + x * 1.05), 1.1, -2), Vector3(1, 2.2, 0.85), stone, true)
		Geo.box(self, Vector3(side * 1.8, 1.9, -2), Vector3(0.6, 3.8, 0.9), pale, true)
	Geo.box(self, Vector3(0, 3.65, -2), Vector3(4.2, 0.5, 0.9), pale, true)
	Geo.box(self, Vector3(0, 0.08, -6), Vector3(9, 0.16, 9), road, true)
	Geo.box(self, Vector3(0, 0.6, -9), Vector3(2.8, 1, 1.3), stone, true)
	Geo.box(self, Vector3(0, 1.15, -9), Vector3(3.1, 0.18, 1.55), pale, true)
	for i in range(46):
		var x := rng.randf_range(-19, 19)
		var z := rng.randf_range(-19, 19)
		if absf(x) < 7 and z < 10:
			continue
		if absf(x) < 3.5:
			continue
		var h := rng.randf_range(3.6, 6.3)
		Geo.box(self, Vector3(x, h * 0.4, z), Vector3(0.45, h * 0.8, 0.45), bark, true)
		for tier in range(3):
			Geo.cone(self, Vector3(x, h * 0.5 + tier * h * 0.19, z), 1.8 - tier * 0.4, h * 0.6, needles if tier % 2 == 0 else moss)
	for i in range(65):
		var at := Vector3(rng.randf_range(-18, 18), 0.13, rng.randf_range(-18, 18))
		if absf(at.x) < 2 or (absf(at.x) < 6 and at.z < -1):
			continue
		var rubble := Geo.box(self, at, Vector3(rng.randf_range(0.25, 0.7), 0.26, rng.randf_range(0.3, 0.8)), moss if i % 3 == 0 else stone)
		rubble.rotation.y = rng.randf_range(0, TAU)
	for at in [Vector3(-2.5, 0, 1), Vector3(2.5, 0, 1), Vector3(-3.7, 0, -7), Vector3(3.7, 0, -7)]:
		_torch(at, bark)
	# Visible perimeter stones plus collision keep the prototype on its finite map.
	for side in [-1, 1]:
		Geo.box(self, Vector3(side * 21, 0.6, 0), Vector3(0.6, 1.2, 42), stone, true)
		Geo.box(self, Vector3(0, 0.6, side * 21), Vector3(42, 1.2, 0.6), stone, true)

func _torch(at: Vector3, bark: Material) -> void:
	Geo.box(self, at + Vector3(0, 0.85, 0), Vector3(0.15, 1.7, 0.15), bark)
	var fire := Geo.material(Color("ffb34d"))
	fire.emission_enabled = true
	fire.emission = Color("ff8e32")
	fire.emission_energy_multiplier = 2.0
	Geo.cone(self, at + Vector3(0, 1.9, 0), 0.18, 0.5, fire)
	var light := OmniLight3D.new()
	light.position = at + Vector3(0, 2, 0)
	light.light_color = Color("ffae61")
	light.light_energy = 0.8
	light.omni_range = 4.5
	light.shadow_enabled = true
	add_child(light)

func _ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := ColorRect.new()
	panel.color = Color(0.04, 0.07, 0.08, 0.82)
	panel.position = Vector2(24, 24)
	panel.size = Vector2(470, 120)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(panel)
	var title := Label.new()
	title.text = "ASHEN OATH  /  THE FORSAKEN CHAPEL"
	title.position = Vector2(38, 35)
	title.add_theme_color_override("font_color", Color("d7cba7"))
	layer.add_child(title)
	var help := Label.new()
	help.text = "WASD / Arrows  Move     Shift  Run\nMouse  Orbit     Wheel  Zoom     R  Reset
Esc  Release mouse     Click  Capture"
	help.position = Vector2(38, 64)
	help.add_theme_font_size_override("font_size", 14)
	layer.add_child(help)
