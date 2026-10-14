extends CharacterBody3D

const KnightModel = preload("res://scripts/art/knight_model.gd")
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
	_build_visual()
	orbit = Orbit.new()
	orbit.target = self
	add_child(orbit)

func _build_visual() -> void:
	visual = Node3D.new()
	add_child(visual)
	var steel := Geo.material(Color("b6c1b9"), 0.3)
	steel.roughness = 0.7
	var dark := Geo.material(Color("293339"), 0.2)
	var red := Geo.material(Color("91394b"))
	red.cull_mode = BaseMaterial3D.CULL_DISABLED
	var trim := Geo.material(Color("b1945e"), 0.5)
	for item in [[steel, "steel"], [dark, "steel"], [red, "cloth"], [trim, "steel"]]:
		PixelMaterials.apply(item[0], item[1], 1.5)
		item[0].uv1_world_triplanar = false
		detailed_materials.append(item[0])
		material_textures.append(item[0].albedo_texture)
	var limbs := KnightModel.build(visual, steel, dark, red, trim)
	left_leg = limbs.left_leg
	right_leg = limbs.right_leg
	left_arm = limbs.left_arm
	right_arm = limbs.right_arm

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
	_animate_visual(delta)
	if position.y < -8 or Input.is_action_just_pressed("reset"):
		position = spawn_point
		velocity = Vector3.ZERO
		reset_physics_interpolation()

func _animate_visual(delta: float) -> void:
	phase += delta * velocity.length() * 3.0
	var swing := sin(phase) * minf(Vector2(velocity.x, velocity.z).length() / 6.0, 0.7)
	left_leg.rotation.x = swing
	right_leg.rotation.x = -swing
	left_arm.rotation.x = -swing * 0.6
	right_arm.rotation.x = swing * 0.6
