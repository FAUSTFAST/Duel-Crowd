extends CharacterBody3D

const Geo = preload("res://scripts/world/geometry.gd")
const PixelMaterials = preload("res://scripts/rendering/pixel_materials.gd")
const Orbit = preload("res://scripts/camera/orbit_camera.gd")
@export var walk_speed: float = 3.2
@export var run_speed: float = 5.8
var visual: Node3D
var left_leg: Node3D
var right_leg: Node3D
var left_arm: Node3D
var right_arm: Node3D
var orbit: Node3D
var detailed_materials: Array[StandardMaterial3D] = []
var material_textures: Array[Texture2D] = []
var phase: float = 0.0
var spawn_point := Vector3(0, 0.1, 5)

func _ready() -> void:
	floor_snap_length = 0.3
	var collider := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.3
	capsule.height = 1.8
	collider.shape = capsule
	collider.position.y = 0.9
	add_child(collider)
	visual = Node3D.new()
	add_child(visual)
	var steel := Geo.material(Color("8c9da5"), 0.55)
	var dark := Geo.material(Color("293339"), 0.2)
	var red := Geo.material(Color("6e2632"))
	for item in [[steel, "steel"], [dark, "steel"], [red, "cloth"]]:
		PixelMaterials.apply(item[0], item[1], 1.5)
		item[0].uv1_world_triplanar = false
		detailed_materials.append(item[0])
		material_textures.append(item[0].albedo_texture)
	Geo.box(visual, Vector3(0, 1.2, 0), Vector3(0.57, 0.6, 0.32), steel)
	Geo.box(visual, Vector3(0, 1.68, 0), Vector3(0.4, 0.4, 0.37), steel)
	Geo.box(visual, Vector3(0, 1.69, -0.192), Vector3(0.31, 0.055, 0.02), dark)
	Geo.box(visual, Vector3(0, 1.33, 0.23), Vector3(0.51, 0.7, 0.06), red)
	Geo.box(visual, Vector3(0, 0.89, 0), Vector3(0.49, 0.17, 0.34), dark)
	left_leg = _limb(Vector3(-0.17, 0.83, 0), Vector3(0.2, 0.65, 0.24), dark)
	right_leg = _limb(Vector3(0.17, 0.83, 0), Vector3(0.2, 0.65, 0.24), dark)
	left_arm = _limb(Vector3(-0.4, 1.43, 0), Vector3(0.22, 0.5, 0.24), steel)
	right_arm = _limb(Vector3(0.4, 1.43, 0), Vector3(0.22, 0.5, 0.24), steel)
	Geo.box(left_arm, Vector3(-0.07, -0.32, -0.12), Vector3(0.13, 0.62, 0.45), red)
	Geo.box(right_arm, Vector3(0, -0.65, -0.13), Vector3(0.07, 0.65, 0.06), steel)
	Geo.box(right_arm, Vector3(0, -0.35, -0.13), Vector3(0.3, 0.05, 0.09), dark)
	orbit = Orbit.new()
	orbit.target = self
	add_child(orbit)

func _limb(at: Vector3, size: Vector3, mat: Material) -> Node3D:
	var pivot := Node3D.new()
	visual.add_child(pivot)
	pivot.position = at
	Geo.box(pivot, Vector3(0, -size.y / 2.0, 0), size, mat)
	return pivot

func _physics_process(delta: float) -> void:
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction: Vector3 = Basis(Vector3.UP, orbit.yaw) * Vector3(input.x, 0, input.y)
	var speed := run_speed if Input.is_action_pressed("sprint") else walk_speed
	velocity.x = move_toward(velocity.x, direction.x * speed, delta * 22.0)
	velocity.z = move_toward(velocity.z, direction.z * speed, delta * 22.0)
	if not is_on_floor():
		velocity.y -= 22.0 * delta
	else:
		velocity.y = 0
	move_and_slide()
	if direction.length_squared() > 0.01:
		visual.rotation.y = lerp_angle(visual.rotation.y, atan2(-direction.x, -direction.z), 12 * delta)
	phase += delta * velocity.length() * 3.0
	var swing := sin(phase) * minf(Vector2(velocity.x, velocity.z).length() / 6.0, 0.7)
	left_leg.rotation.x = swing
	right_leg.rotation.x = -swing
	left_arm.rotation.x = -swing * 0.6
	right_arm.rotation.x = swing * 0.6
	if position.y < -8 or Input.is_action_just_pressed("reset"):
		position = spawn_point
		velocity = Vector3.ZERO
		reset_physics_interpolation()
