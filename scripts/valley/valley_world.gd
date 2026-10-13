extends Node3D

const Materials = preload("res://scripts/valley/valley_materials.gd")
const Knight = preload("res://scripts/valley/valley_knight.gd")
const Flame = preload("res://scripts/art/torch_flame.gd")
const MODEL_ROOT := "res://assets/valley/models/"
var player: CharacterBody3D
var environment: Environment
var sun: DirectionalLight3D
var terrain: MeshInstance3D
var terrain_material: ShaderMaterial
var detailed_materials: Array[StandardMaterial3D] = []
var material_textures: Array[Texture2D] = []
var surface_library := Materials.new()
var field: Resource
var trail: Array[Vector3] = []
var rng := RandomNumberGenerator.new()
var trees: Array[Node3D] = []
var rocks: Array[Node3D] = []
var flames: Array[Node3D] = []

func _ready() -> void:
	rng.seed = 8102026
	field = preload("res://assets/valley/source/heightfield.tres")
	for point in field.path:
		trail.append(Vector3(point[0], point[1], point[2]))
	_setup_input()
	_lighting()
	_build_terrain()
	_build_rocks()
	_build_trees()
	_build_shrubs()
	_build_ground_cover()
	_brazier()
	player = Knight.new()
	player.name = "ValleyKnight"
	player.spawn_point = Vector3(path_x(8), height_at(path_x(8), 8) + 0.08, 8)
	player.position = player.spawn_point
	add_child(player)
	player.orbit.yaw = 0.16
	player.orbit.pitch = -0.48
	player.orbit.distance = 10.0
	detailed_materials = surface_library.materials
	material_textures = surface_library.textures

func _setup_input() -> void:
	# Match the original map's actions; no additional event route or gameplay.
	var bindings := {"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT], "move_forward": [KEY_W, KEY_UP], "move_back": [KEY_S, KEY_DOWN], "sprint": [KEY_SHIFT], "reset": [KEY_R]}
	for action in bindings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for code in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = code
			if not InputMap.action_has_event(action, event):
				InputMap.action_add_event(action, event)

func path_x(z: float) -> float:
	return sin(z * 0.22) * 1.25 - 0.3

func height_at(x: float, z: float) -> float:
	var width := int(field.width)
	var depth := int(field.depth)
	var u := clampf((x - float(field.min_x)) / float(field.step), 0, width - 1.001)
	var v := clampf((z - float(field.min_z)) / float(field.step), 0, depth - 1.001)
	var ix := int(u)
	var iz := int(v)
	var heights: PackedFloat32Array = field.heights
	return lerpf(lerpf(heights[iz * width + ix], heights[iz * width + ix + 1], u - ix), lerpf(heights[(iz + 1) * width + ix], heights[(iz + 1) * width + ix + 1], u - ix), v - iz)

func _lighting() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("344a52")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("a3b9c5")
	environment.ambient_light_energy = 0.30
	environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	environment.fog_enabled = true
	environment.fog_density = 0.010
	environment.fog_light_color = Color("4d6864")
	var world := WorldEnvironment.new()
	world.environment = environment
	add_child(world)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -32, 0)
	sun.light_color = Color("f1dec2")
	sun.light_energy = 0.95
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 65
	add_child(sun)

func _asset(name: String, parent: Node = self) -> Node3D:
	var node := (load(MODEL_ROOT + name + ".glb") as PackedScene).instantiate() as Node3D
	parent.add_child(node)
	surface_library.apply(node)
	return node

func _build_terrain() -> void:
	var asset := _asset("valley_terrain")
	terrain = asset.find_child("TerrainSurface", true, false)
	terrain_material = ShaderMaterial.new()
	terrain_material.shader = preload("res://shaders/valley_terrain.gdshader")
	for kind in ["soil", "moss", "slate"]:
		for channel in ["albedo", "normal", "roughness"]:
			terrain_material.set_shader_parameter(kind + "_" + channel, load(Materials.ROOT + kind + "_" + channel + ".png"))
	terrain.material_override = terrain_material
	_mesh_collision(terrain, "TerrainCollision")

func _mesh_collision(mesh: MeshInstance3D, label: String) -> void:
	var body := StaticBody3D.new()
	body.name = label
	mesh.add_child(body)
	var shape := CollisionShape3D.new()
	shape.shape = mesh.mesh.create_trimesh_shape()
	body.add_child(shape)

func _build_rocks() -> void:
	# Layered outcrops embedded into the banks, away from the traversable trail.
	for side in [-1.0, 1.0]:
		for i in 11:
			var z := -16.0 + i * 2.65 + rng.randf_range(-0.5, 0.5)
			var x: float = path_x(z) + float(side) * rng.randf_range(4.1, 6.2)
			var node := _asset("slate_a" if i % 2 == 0 else "slate_b")
			node.position = Vector3(x, height_at(x, z) - 1.0, z)
			node.scale = Vector3(rng.randf_range(1.5, 2.1), rng.randf_range(1.4, 2.0), rng.randf_range(1.0, 1.4))
			node.rotation.y = rng.randf_range(-0.6, 0.6)
			var mesh := node.find_child("SlateErosion*", true, false) as MeshInstance3D
			_mesh_collision(mesh, "CliffCollision")
			rocks.append(node)
	# Small erosional fragments: the same authored rock, no cubes or spheres.
	for i in 20:
		var z := rng.randf_range(-15, 12)
		var x := path_x(z) + (1 if i % 2 else -1) * rng.randf_range(1.8, 3.2)
		var node := _asset("slate_b")
		node.position = Vector3(x, height_at(x, z) - 0.08, z)
		node.scale = Vector3.ONE * rng.randf_range(0.12, 0.32)
		node.rotation.y = rng.randf_range(-PI, PI)
		rocks.append(node)

func _build_trees() -> void:
	var positions := [Vector2(-3.9, 5.4), Vector2(4.2, 2), Vector2(-4.3, -2.5), Vector2(3.4, -7), Vector2(-4.8, -11.5), Vector2(4.5, -15), Vector2(-6, -17)]
	for side in [-1.0, 1.0]:
		for i in 8:
			positions.append(Vector2(side * rng.randf_range(8, 11), -16 + i * 4.0))
	for i in positions.size():
		var p: Vector2 = positions[i]
		var node := _asset("oak_a" if i % 2 == 0 else "oak_b")
		node.position = Vector3(p.x, height_at(p.x, p.y) - 0.16, p.y)
		node.scale = Vector3.ONE * rng.randf_range(0.95, 1.35)
		node.rotation.y = rng.randf_range(-PI, PI)
		var body := StaticBody3D.new()
		node.add_child(body)
		var collider := CollisionShape3D.new()
		var shape := CylinderShape3D.new()
		shape.height = 3.6
		shape.radius = 0.37
		collider.shape = shape
		collider.position.y = 1.8
		body.add_child(collider)
		trees.append(node)

func _build_shrubs() -> void:
	for i in 18:
		var z := rng.randf_range(-15, 11)
		var x := path_x(z) + (1 if i % 2 else -1) * rng.randf_range(2.4, 3.9)
		var node := _asset("shrub")
		node.position = Vector3(x, height_at(x, z), z)
		node.scale = Vector3.ONE * rng.randf_range(0.8, 1.3)
		node.rotation.y = rng.randf_range(-PI, PI)

func _build_ground_cover() -> void:
	var grass_positions: Array[Transform3D] = []
	var flower_positions: Array[Transform3D] = []
	for i in 1100:
		var z := rng.randf_range(-17, 13)
		var x := rng.randf_range(-10.8, 10.8)
		var d := absf(x - path_x(z))
		if d < 1.05 or (d > 7 and rng.randf() > 0.35):
			continue
		var scale_factor := rng.randf_range(0.7, 1.15)
		var basis := Basis(Vector3.UP, rng.randf_range(-PI, PI)).scaled(Vector3(scale_factor, scale_factor * 0.65, scale_factor))
		var t := Transform3D(basis, Vector3(x, height_at(x, z) - 0.015, z))
		if d < 3.6 and rng.randf() < 0.11:
			flower_positions.append(t)
		else:
			grass_positions.append(t)
	_cover_batch("grass_patch", grass_positions)
	_cover_batch("flower_patch", flower_positions)

func _cover_batch(asset: String, transforms: Array[Transform3D]) -> void:
	var source := _asset(asset)
	var meshes := source.find_children("*", "MeshInstance3D", true, false)
	for mesh in meshes:
		# Material overrides live on instances, so copy them onto the shared batch mesh.
		var batch_mesh := mesh.mesh.duplicate() as ArrayMesh
		for surface in batch_mesh.get_surface_count():
			batch_mesh.surface_set_material(surface, mesh.get_active_material(surface))
		var multi := MultiMesh.new()
		multi.transform_format = MultiMesh.TRANSFORM_3D
		multi.mesh = batch_mesh
		multi.instance_count = transforms.size()
		for i in transforms.size():
			multi.set_instance_transform(i, transforms[i] * mesh.transform)
		var display := MultiMeshInstance3D.new()
		display.name = asset + "Batch"
		display.multimesh = multi
		# Thin grass doesn't need to populate the shadow map.
		display.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(display)
	source.queue_free()

func _brazier() -> void:
	# Reuse original animated fire; the sculpted rock acts as its stone hearth.
	var x := -1.8
	var z := 4.0
	var stone := _asset("slate_a")
	stone.position = Vector3(x, height_at(x, z) - 0.08, z)
	stone.scale = Vector3(0.3, 0.15, 0.3)
	var light := OmniLight3D.new()
	light.position = Vector3(x, height_at(x, z) + 1.0, z)
	light.light_color = Color("ffb465")
	light.omni_range = 5.5
	light.shadow_enabled = true
	add_child(light)
	var flame := Flame.new()
	flame.position = Vector3(x, height_at(x, z) + 0.25, z)
	flame.light = light
	add_child(flame)
	flames.append(flame)

func set_material_detail(enabled: bool) -> void:
	terrain_material.set_shader_parameter("detail_enabled", enabled)
	surface_library.set_detail(enabled)
	player.study_materials.set_detail(enabled)

func set_art_animation(enabled: bool) -> void:
	for flame in flames:
		flame.set_animation_enabled(enabled)
