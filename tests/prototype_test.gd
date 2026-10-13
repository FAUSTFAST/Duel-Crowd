extends SceneTree

var world: Node3D
var failures: int = 0

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Mouse capture tests require a graphical window; omit --headless.")
		quit(2)
		return
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	if condition:
		print("PASS: ", message)
	else:
		push_error("FAIL: " + message)
		failures += 1

func frames(count: int) -> void:
	for i in count:
		await physics_frame

func _run() -> void:
	world = load("res://scenes/world/forest_ruins.tscn").instantiate()
	root.add_child(world)
	await frames(30)
	var knight: CharacterBody3D = world.player
	check(knight.is_on_floor(), "knight settles on ground")
	check(knight.orbit.camera.current, "third person camera active")
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "startup captures mouse")
	var motion := InputEventMouseMotion.new()
	motion.screen_relative = Vector2(20, 10)
	var initial_yaw: float = knight.orbit.yaw
	root.push_input(motion)
	check(knight.orbit.yaw < initial_yaw, "mouse rotates without held buttons")
	var escape := InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	root.push_input(escape)
	check(Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "Escape releases mouse without quitting")
	var released_yaw: float = knight.orbit.yaw
	root.push_input(motion)
	check(knight.orbit.yaw == released_yaw, "released cursor does not rotate camera")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	root.push_input(click)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "click recaptures mouse")
	var before_position: Vector3 = knight.orbit.global_position
	knight.position += Vector3(1, 0, 0)
	var desired: Vector3 = knight.global_position + knight.orbit.follow_offset
	await frames(2)
	check(knight.orbit.global_position.distance_to(desired) < before_position.distance_to(desired) and knight.orbit.global_position.distance_to(desired) > 0.01, "follow moves smoothly towards player")
	await frames(60)
	check(knight.orbit.global_position.distance_to(knight.global_position + knight.orbit.follow_offset) < 0.01, "follow converges to player")
	var before_yaw: float = knight.orbit.yaw
	Input.action_release("sprint")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	var before_distance: float = knight.orbit.distance
	knight.orbit._unhandled_input(wheel)
	check(knight.orbit.distance < before_distance, "mouse wheel zoom works")
	knight.orbit.yaw = before_yaw + 0.2
	await frames(30)
	check(absf(knight.orbit.rotation.y - knight.orbit.yaw) < 0.001, "camera follows orbit yaw")
	var oversized := InputEventMouseMotion.new()
	oversized.screen_relative = Vector2(0, 100000)
	root.push_input(oversized)
	check(is_equal_approx(knight.orbit.pitch, knight.orbit.min_pitch), "pitch limit prevents flipping")
	knight.orbit.pitch = -0.65
	for i in 60:
		knight.orbit._unhandled_input(wheel)
	check(is_equal_approx(knight.orbit.distance, knight.orbit.min_distance), "zoom respects minimum")
	wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
	for i in 60:
		knight.orbit._unhandled_input(wheel)
	check(is_equal_approx(knight.orbit.distance, knight.orbit.max_distance), "zoom respects maximum")
	knight.orbit.distance = 12
	knight.orbit.yaw = before_yaw
	var start := knight.position
	Input.action_press("move_forward")
	await frames(60)
	Input.action_release("move_forward")
	check(knight.position.distance_to(start) > 2.0, "camera relative walking works")
	var walk_velocity := Vector2(knight.velocity.x, knight.velocity.z).length()
	Input.action_press("move_forward")
	Input.action_press("sprint")
	await frames(20)
	check(Vector2(knight.velocity.x, knight.velocity.z).length() > walk_velocity + 1, "sprint faster than walk")
	Input.action_release("move_forward")
	Input.action_release("sprint")
	knight.position = Vector3(4.0, 0.2, -5)
	knight.orbit.yaw = 0
	Input.action_press("move_right")
	await frames(60)
	Input.action_release("move_right")
	check(knight.position.x < 4.4, "chapel wall blocks movement")
	Input.action_press("reset")
	await frames(1)
	Input.action_release("reset")
	await frames(2)
	check(knight.position.distance_to(knight.spawn_point) < 0.2, "reset restores spawn")
	knight.position.y = -10
	await frames(3)
	check(knight.position.y >= 0, "fall recovery works")
	print("RESULT: ", failures, " failures")
	quit(1 if failures else 0)
