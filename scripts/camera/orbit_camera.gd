extends Node3D

@export var target: Node3D
@export_group("Orbit")
@export_range(0.0001, 0.02, 0.0001) var mouse_sensitivity: float = 0.004
@export var yaw: float = 0.55
@export var pitch: float = -0.65
@export var min_pitch: float = -1.1
@export var max_pitch: float = -0.25
@export_group("Follow")
@export var follow_offset := Vector3(0, 1.2, 0)
@export_range(0.1, 40.0) var follow_speed: float = 12.0
@export_range(0.1, 40.0) var rotation_speed: float = 18.0
@export_group("Zoom")
@export var distance: float = 12.0
@export var min_distance: float = 4.0
@export var max_distance: float = 13.0
@export var zoom_step: float = 0.5
@export_range(0.1, 40.0) var zoom_speed: float = 12.0
var arm: SpringArm3D
var camera: Camera3D

func _ready() -> void:
	top_level = true
	# Process after the character so follow uses this tick's final position.
	process_physics_priority = 10
	arm = SpringArm3D.new()
	arm.spring_length = clampf(distance, min_distance, max_distance)
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
	if is_instance_valid(target):
		global_position = target.global_position + follow_offset
	rotation = Vector3(pitch, yaw, 0)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
	# Handle Escape before GUI/unhandled input; it releases, never quits.
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		get_viewport().set_input_as_handled()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
			if event.button_index == MOUSE_BUTTON_LEFT or event.button_index == MOUSE_BUTTON_RIGHT:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
				get_viewport().set_input_as_handled()
			return
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = maxf(min_distance, distance - zoom_step)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = minf(max_distance, distance + zoom_step)
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		# Unscaled screen delta keeps sensitivity stable across window stretch.
		yaw = wrapf(yaw - event.screen_relative.x * mouse_sensitivity, -PI, PI)
		pitch = clampf(pitch - event.screen_relative.y * mouse_sensitivity, min_pitch, max_pitch)

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _exit_tree() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _physics_process(delta: float) -> void:
	if is_instance_valid(target):
		var desired := target.global_position + follow_offset
		global_position = global_position.lerp(desired, 1.0 - exp(-follow_speed * delta))
	var blend := 1.0 - exp(-rotation_speed * delta)
	rotation.x = lerp_angle(rotation.x, pitch, blend)
	rotation.y = lerp_angle(rotation.y, yaw, blend)
	arm.spring_length = lerpf(arm.spring_length, clampf(distance, min_distance, max_distance), 1.0 - exp(-zoom_speed * delta))
