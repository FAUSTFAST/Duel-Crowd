extends Node3D

signal comparison_changed
const OLD := preload("res://scenes/characters/ashen_knight_visual.tscn")
const NEW := preload("res://scenes/characters/thorn_knight_visual.tscn")
var player: CharacterBody3D
var environment: Environment
var sun: DirectionalLight3D
var fill: DirectionalLight3D
var new_variant := true
var forest_light := false
var detail_enabled := true
var animation_enabled := true
var botanicals: Node3D

func _ready() -> void:
	# Use the existing project's bindings, without changing its input routes.
	var input_source := preload("res://scripts/valley/valley_world.gd").new()
	input_source._setup_input()
	input_source.free()
	_lighting()
	_floor()
	player = preload("res://scripts/atelier/atelier_player.gd").new()
	player.visual_scene = NEW
	player.name = "ComparisonKnight"
	player.spawn_point = Vector3(0, 0.05, 0)
	player.position = player.spawn_point
	add_child(player)
	player.orbit.min_distance = 2.6
	player.orbit.distance = 4.0
	player.orbit.yaw = PI + 0.3
	player.orbit.pitch = -0.2
	_botanical_fixture()

func _lighting() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("26343a")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("b7c5ca")
	environment.ambient_light_energy = 0.35
	environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	environment.fog_enabled = false
	environment.fog_density = 0.014
	environment.fog_light_color = Color("4d6864")
	var node := WorldEnvironment.new()
	node.environment = environment
	add_child(node)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -32, 0)
	sun.light_color = Color("f2e7d3")
	sun.light_energy = 0.9
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 28
	add_child(sun)
	fill = DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-30, 150, 0)
	fill.light_color = Color("91b6cc")
	fill.light_energy = 0.22
	add_child(fill)

func _floor() -> void:
	var floor_mesh := MeshInstance3D.new()
	floor_mesh.name = "NeutralComparisonFloor"
	var plane := PlaneMesh.new()
	plane.size = Vector2(28, 28)
	floor_mesh.mesh = plane
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color("46504b")
	mat.roughness = 0.95
	floor_mesh.material_override = mat
	add_child(floor_mesh)
	var body := StaticBody3D.new()
	body.name = "LabFloorCollision"
	var collision := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(28, 0.4, 28)
	collision.shape = shape
	collision.position.y = -0.2
	body.add_child(collision)
	add_child(body)

func select_variant(use_new: bool) -> void:
	if use_new == new_variant:
		return
	var heading: float = player.visual.rotation.y
	player.visual.free()
	player.visual_scene = NEW if use_new else OLD
	player._build_visual()
	player.visual.rotation.y = heading
	player.visual.previous_yaw = heading
	player.visual.set_animation_enabled(animation_enabled)
	player.study_materials.set_detail(detail_enabled)
	new_variant = use_new
	comparison_changed.emit()

func set_forest_light(enabled: bool) -> void:
	forest_light = enabled
	environment.ambient_light_energy = 0.30 if enabled else 0.35
	environment.ambient_light_color = Color("a3b9c5") if enabled else Color("b7c5ca")
	sun.light_color = Color("f1dec2") if enabled else Color("f2e7d3")
	sun.light_energy = 0.95 if enabled else 0.9
	fill.light_energy = 0.14 if enabled else 0.22
	environment.fog_enabled = enabled
	comparison_changed.emit()

func set_material_detail(enabled: bool) -> void:
	detail_enabled = enabled
	player.study_materials.set_detail(enabled)

func set_art_animation(enabled: bool) -> void:
	animation_enabled = enabled
	player.set_visual_animation_enabled(enabled)

func _unhandled_input(event: InputEvent) -> void:
	if event is not InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_B:
			select_variant(not new_variant)
		KEY_L:
			set_forest_light(not forest_light)
		KEY_0, KEY_1, KEY_2, KEY_3:
			player.preview_speed = {KEY_0: -1.0, KEY_1: 0.0, KEY_2: 3.2, KEY_3: 5.8}[event.keycode]
			comparison_changed.emit()
		_:
			return
	get_viewport().set_input_as_handled()

func _botanical_fixture() -> void:
	# Optional separate cutout specimen. Never adds dressing to either old map.
	botanicals = Node3D.new()
	botanicals.name = "PixelCutoutSpecimen"
	add_child(botanicals)
	var path := "res://assets/characters/thorn_knight/textures/fern_cutout.png"
	if not ResourceLoader.exists(path):
		return
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load(path)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mat.alpha_scissor_threshold = 0.5
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.roughness = 1.0
	for i in 3:
		var card := MeshInstance3D.new()
		var quad := QuadMesh.new()
		quad.size = Vector2(0.65, 0.55)
		card.mesh = quad
		card.material_override = mat
		card.position = Vector3(1.3, 0.275, -0.5)
		card.rotation.y = i * PI / 3.0
		botanicals.add_child(card)
