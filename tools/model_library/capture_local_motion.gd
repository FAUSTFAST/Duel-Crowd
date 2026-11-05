extends SceneTree
## Records actual controller-driven movement. Run graphically with --fixed-fps 30.
var game: Node
var output := "res://local_assets/bang_dream/previews/mutsumi_motion_v5/take1/"

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--take="):
			output = "res://local_assets/bang_dream/previews/mutsumi_motion_v5/take%d/" % maxi(1, int(arg.trim_prefix("--take=")))
	call_deferred("record")

func release_actions() -> void:
	for action in ["move_left", "move_right", "move_forward", "move_back", "sprint"]:
		Input.action_release(action)

func drive(direction: Vector3, yaw: float, sprint: bool) -> void:
	var local := Basis(Vector3.UP, -yaw) * direction
	Input.action_press("move_left", maxf(-local.x, 0))
	Input.action_press("move_right", maxf(local.x, 0))
	Input.action_press("move_forward", maxf(-local.z, 0))
	Input.action_press("move_back", maxf(local.z, 0))
	if sprint: Input.action_press("sprint")
	else: Input.action_release("sprint")

func record() -> void:
	if DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(output)):
		push_error("Refusing to overwrite a take. Pass -- --take=2 for a new recording.")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output + "frames"))
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/local_model_motion.tscn").instantiate()
	root.add_child(game)
	if not game.world.load_error.is_empty():
		push_error(game.world.load_error)
		quit(1)
		return
	var player: CharacterBody3D = game.world.player
	var orbit: Node3D = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.distance = 4.4
	orbit.yaw = PI + .25
	orbit.pitch = -.30
	for i in 90: await process_frame
	game.hud.visible = false
	var route: Array[Vector3] = []
	for z in range(5, -16, -2):
		var x: float = game.world.path_x(z)
		route.append(Vector3(x, game.world.height_at(x, z), z))
	var target := 0
	var distance := 0.0
	var previous: Vector3 = player.position
	var grounded := 0
	var states := {}
	var samples := []
	for frame in 360:
		var seconds := frame / 30.0
		orbit.yaw = lerpf(PI + .25, .30, smoothstep(4, 7, seconds))
		var moving := seconds >= 1.0 and seconds < 10.5
		var sprint := seconds >= 3.5 and seconds < 9.0
		if moving and target < route.size():
			var delta: Vector3 = route[target] - player.position
			delta.y = 0
			if delta.length() < .25:
				target += 1
				if target < route.size():
					delta = route[target] - player.position
					delta.y = 0
			if target < route.size(): drive(delta.normalized(), orbit.yaw, sprint)
			else: release_actions()
		else: release_actions()
		await process_frame
		await RenderingServer.frame_post_draw
		distance += Vector2(player.position.x - previous.x, player.position.z - previous.z).length()
		previous = player.position
		if player.is_on_floor(): grounded += 1
		var state: String = game.world.motion.current_state
		states[state] = int(states.get(state, 0)) + 1
		var image: Image = game.viewport.get_texture().get_image()
		assert(image.save_png(output + "frames/frame_%04d.png" % frame) == OK)
		if frame in [15, 75, 150, 255]:
			assert(root.get_texture().get_image().save_png(output + "pose_%03d.png" % frame) == OK)
		if frame % 30 == 0:
			samples.append({"second": seconds, "state": state, "speed": Vector2(player.get_real_velocity().x, player.get_real_velocity().z).length(), "grounded": player.is_on_floor()})
	release_actions()
	var report := {"engine": Engine.get_version_info().string, "frames": 360, "fps": 30, "internal_resolution": [game.viewport.size.x, game.viewport.size.y], "distance_m": distance, "grounded_frames": grounded, "states": states, "route_targets": target, "samples": samples, "kind": "actual physics/controller/rendered frames; no synthesized motion", "limitations": "original prototype clips; no slope foot IK or cloth/hair physics"}
	FileAccess.open(output + "recording.json", FileAccess.WRITE).store_string(JSON.stringify(report, "\t") + "\n")
	print("LOCAL_MOTION_RECORD_COMPLETE ", JSON.stringify(report))
	quit(0 if distance > 12 and states.has("walk") and states.has("run") and states.has("idle") else 1)
