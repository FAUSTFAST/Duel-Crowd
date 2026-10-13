extends Node3D

@export var target: Node3D
@export var distance: float = 12.0
var yaw: float = 0.55
var pitch: float = -0.65
var arm: SpringArm3D
var camera: Camera3D

func _ready() -> void:
	top_level = true
	arm = SpringArm3D.new()
	arm.spring_length = distance
	arm.margin = 0.25
	add_child(arm)
	var shape := SphereShape3D.new()
	shape.radius = 0.22
	arm.shape = shape
	if target is PhysicsBody3D:
		arm.add_excluded_object(target.get_rid())
	camera = Camera3D.new()
	camera.fov = 52.0
	camera.current = true
	camera.far = 100.0
	arm.add_child(camera)
	_sync()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		yaw -= event.relative.x * 0.004
		pitch = clampf(pitch - event.relative.y * 0.004, -1.1, -0.25)
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = maxf(4.0, distance - 0.5)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = minf(13.0, distance + 0.5)

func _physics_process(_delta: float) -> void:
	_sync()

func _sync() -> void:
	if is_instance_valid(target):
		global_position = target.global_position + Vector3(0, 1.2, 0)
	rotation = Vector3(pitch, yaw, 0)
	arm.spring_length = distance
