extends Node3D

const Art = preload("res://scripts/art/ruins_kit.gd")
const Meshes = preload("res://scripts/art/art_meshes.gd")
const Geo = preload("res://scripts/world/geometry.gd")
const PixelMaterials = preload("res://scripts/rendering/pixel_materials.gd")
const Dressing = preload("res://scripts/art/forest_dressing.gd")
const Flame = preload("res://scripts/art/torch_flame.gd")
var flame_locations: Array[Vector3] = []
var torch_lights: Array[OmniLight3D] = []
var torch_iron: StandardMaterial3D

const Knight = preload("res://scripts/characters/knight.gd")
var player: CharacterBody3D
var environment: Environment
var sun: DirectionalLight3D
var detailed_materials: Array[StandardMaterial3D] = []
var material_textures: Array[Texture2D] = []
var rng := RandomNumberGenerator.new()

func _ready() -> void:
	rng.seed = 731104
	_setup_input()
	_environment()
	_build_world()
	Art.batch_static(self)
	for i in flame_locations.size():
		var flame := Flame.new()
		flame.position = flame_locations[i] + Vector3(0, 1.7, 0)
		flame.light = torch_lights[i]
		flame.phase_offset = i * 3
		add_child(flame)
	player = Knight.new()
	player.name = "Knight"
	player.position = player.spawn_point
	add_child(player)

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
	environment = env
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("263740")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("7f91a3")
	env.ambient_light_energy = 0.32
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color("354751")
	env.fog_density = 0.0075
	world.environment = env
	add_child(world)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42, -40, 0)
	sun.light_color = Color("c4c7bd")
	sun.light_energy = 1.05
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 55
	add_child(sun)

func _build_world() -> void:
	var earth := _surface(Color("4b4939"), "earth", 0.45)
	var stone := _surface(Color("626966"), "granite")
	var pale := _surface(Color("85867a"), "granite")
	var road := _surface(Color("85806e"), "flagstone", 0.65)
	var bark := _surface(Color("504331"), "bark", 1.0)
	var needles := _surface(Color("213b30"), "leaves", 0.55)
	var moss := _surface(Color("3e5640"), "leaves", 0.55)
	Geo.box(self, Vector3(0, -0.3, 0), Vector3(42, 0.6, 42), earth, true)
	for i in range(18):
		for j in range(3):
			var slab := Art.block(self, Vector3((j - 1) * 1.15 + rng.randf_range(-0.03, 0.03), 0.035, 13 - i * 1.4), Vector3(0.96 + 0.025 * sin(i * 2.3 + j), 0.07, 1.2 + 0.075 * sin(i + j * 1.7)), road)
			slab.mesh = Meshes.worn_slab(slab.mesh.get_aabb().size, i * 7 + j)
			slab.rotation.y = rng.randf_range(-0.035, 0.035) + 0.02 * sin(i * 3.0 + j)
	# Broken chapel side walls and interrupted facade; central entrance remains open.
	for side in [-1, 1]:
		for segment in range(7):
			var levels := rng.randi_range(2, 4)
			for row in range(levels):
				Art.block(self, Vector3(side * 5.0, 0.4 + row * 0.8, -2 - segment * 1.25), Vector3(0.8, 0.76, 1.2), stone if row % 2 == 0 else pale, true)
		for x in range(3):
			Art.block(self, Vector3(side * (2.3 + x * 1.05), 1.1, -2), Vector3(1, 2.2, 0.85), stone, true)
		Art.block(self, Vector3(side * 1.8, 1.9, -2), Vector3(0.6, 3.8, 0.9), pale, true)
	Art.block(self, Vector3(0, 3.65, -2), Vector3(4.2, 0.5, 0.9), pale, true)
	Geo.box(self, Vector3(0, 0.08, -6), Vector3(9, 0.16, 9), road, true)
	Art.block(self, Vector3(0, 0.6, -9), Vector3(2.8, 1, 1.3), stone, true)
	Art.block(self, Vector3(0, 1.15, -9), Vector3(3.1, 0.18, 1.55), pale, true)
	for i in range(46):
		var x := rng.randf_range(-19, 19)
		var z := rng.randf_range(-19, 19)
		if absf(x) < 7 and z < 10:
			continue
		if absf(x) < 3.5:
			continue
		var h := rng.randf_range(3.6, 6.3)
		Art.tree(self, Vector3(x, 0, z), h, bark, needles, moss, i)
	for i in range(65):
		var at := Vector3(rng.randf_range(-18, 18), 0.13, rng.randf_range(-18, 18))
		if absf(at.x) < 2 or (absf(at.x) < 6 and at.z < -1):
			continue
		var rubble := Geo.rock(self, at, Vector3(rng.randf_range(0.25, 0.7), 0.26, rng.randf_range(0.3, 0.8)), moss if i % 3 == 0 else stone)
		rubble.rotation.y = rng.randf_range(0, TAU)
	for at in [Vector3(-2.5, 0, 1), Vector3(2.5, 0, 1), Vector3(-3.7, 0, -7), Vector3(3.7, 0, -7)]:
		_torch(at, bark)
	# Visible perimeter stones plus collision keep the prototype on its finite map.
	for side in [-1, 1]:
		_boundary(Vector3(side * 21, 0.6, 0), Vector3(0.6, 1.2, 42), stone)
		_boundary(Vector3(0, 0.6, side * 21), Vector3(42, 1.2, 0.6), stone)

	# Separate seeded decoration pass keeps the existing layout and RNG unchanged.
	var decoration_rng := RandomNumberGenerator.new()
	decoration_rng.seed = 9135
	var grass := _surface(Color("69774d"), "grass", 0.5)
	grass.cull_mode = BaseMaterial3D.CULL_DISABLED
	for i in 50:
		var at := Vector3(decoration_rng.randf_range(-17, 17), 0, decoration_rng.randf_range(-16, 16))
		if absf(at.x) < 2.5 or (absf(at.x) < 6 and at.z < -1):
			continue
		for blade in 3:
			var h := decoration_rng.randf_range(0.18, 0.4)
			Geo.cone(self, at + Vector3(blade * 0.1, h * 0.5, 0), 0.075, h, grass)

	var metal := _surface(Color("8e7950"), "steel", 1.0)
	metal.metallic = 0.5
	var cloth := _surface(Color("742f3b"), "cloth", 1.0)
	Art.portal(self, stone, pale, metal, cloth)
	var wood := _surface(Color("5c4532"), "wood", 0.7)
	for side in [-1, 1]:
		for i in 3:
			var timber := Art.block(self, Vector3(side * (3.4 + i * 0.25), 0.28, -5.5 + i * 0.45), Vector3(0.22, 0.22, 2.0), wood)
			timber.rotation_degrees = Vector3(0, side * (25 + i * 13), 8 + i * 5)
	# Ground contact detail is limited to path verges, never the traversable centre.
	for side in [-1, 1]:
		for i in 14:
			if i % 4 == 2:
				continue
			var chunk := Art.block(self, Vector3(side * (1.85 + 0.18 * sin(i)), 0.09, 11.0 - i * 1.15), Vector3(0.42, 0.18, 0.72), stone)
			chunk.rotation.y = side * 0.45 * sin(i * 1.6)

	var shrub_dark := _surface(Color("2e4532"), "leaves", 0.65)
	var shrub_light := _surface(Color("657247"), "leaves", 0.65)
	shrub_light.cull_mode = BaseMaterial3D.CULL_DISABLED
	var litter := _surface(Color("806446"), "wood", 0.7)
	Dressing.dress(self, earth, stone, pale, bark, shrub_dark, shrub_light, grass, litter)

func _boundary(at: Vector3, size: Vector3, mat: Material) -> void:
	var boundary := Geo.box(self, at, size, mat, true)
	# Keep the original safety collision at 1.2m, reduce only the visible arena wall.
	boundary.position.y = 0.15
	boundary.get_child(0).position.y = 0.45
	boundary.mesh = Meshes.bevel_box(Vector3(size.x, 0.3, size.z))

func _torch(at: Vector3, bark: Material) -> void:
	Art.block(self, at + Vector3(0, 0.1, 0), Vector3(0.55, 0.2, 0.55), bark)
	Geo.cone(self, at + Vector3(0, 0.85, 0), 0.1, 1.5, bark, 0.07)
	if torch_iron == null:
		torch_iron = _surface(Color("343b3c"), "steel", 0.9)
		torch_iron.metallic = 0.3
	var iron := torch_iron
	Art.piece(self, at + Vector3(0, 1.48, 0), Meshes.profile([Vector3(0.11, 0, 0.11), Vector3(0.27, 0.15, 0.27), Vector3(0.3, 0.22, 0.3)], 8), iron)
	for i in 5:
		var angle := i * TAU / 5.0
		var prong := Art.block(self, at + Vector3(cos(angle) * 0.24, 1.75, sin(angle) * 0.24), Vector3(0.055, 0.28, 0.055), iron)
		prong.rotation.z = cos(angle) * -0.2
	var light := OmniLight3D.new()
	light.position = at + Vector3(0, 2, 0)
	light.light_color = Color("ffae61")
	light.light_energy = 1.4
	light.omni_range = 4.5
	light.shadow_enabled = true
	add_child(light)
	flame_locations.append(at)
	torch_lights.append(light)

func set_art_animation(enabled: bool) -> void:
	for flame in get_tree().get_nodes_in_group("art_flames"):
		if is_ancestor_of(flame):
			flame.set_animation_enabled(enabled)

func _surface(color: Color, kind: String, scale: float = 0.7) -> StandardMaterial3D:
	var mat := Geo.material(color)
	PixelMaterials.apply(mat, kind, scale)
	detailed_materials.append(mat)
	material_textures.append(mat.albedo_texture)
	return mat

func set_material_detail(enabled: bool) -> void:
	for i in detailed_materials.size():
		detailed_materials[i].albedo_texture = material_textures[i] if enabled else null
	for i in player.detailed_materials.size():
		player.detailed_materials[i].albedo_texture = player.material_textures[i] if enabled else null
