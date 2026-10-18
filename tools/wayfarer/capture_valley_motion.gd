extends SceneTree
## Real controller-driven tour. Only the runtime fixture swaps the visual.
## Run graphically with --fixed-fps 30. PNG frames remain outside the repo.
const OUTPUT := "res://docs/character_motion/"
const FRAME_DIR := "/private/tmp/duel-crowd-motion-20261018"
const FPS := 30
var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
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
	DirAccess.make_dir_recursive_absolute(OUTPUT)
	DirAccess.make_dir_recursive_absolute(FRAME_DIR)
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	var player: CharacterBody3D = game.world.player
	player.visual.free()
	player.visual_scene = load("res://scenes/characters/silhouette_visual.tscn")
	player._build_visual()
	game.world.set_art_animation(true)
	game.set_resolution(1)
	game.hud.visible = false
	var orbit: Node3D = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.yaw = PI + .30
	orbit.pitch = -.32
	orbit.distance = 5.2
	for i in 45: await process_frame
	await RenderingServer.frame_post_draw
	var route: Array[Vector3] = []
	for point in game.world.trail.slice(2, 12): route.append(point)
	for i in range(10, 0, -1): route.append(game.world.trail[i])
	var target := 0
	var distance := 0.0
	var previous: Vector3 = player.position
	var walk_peak := 0.0
	var run_peak := 0.0
	var grounded_frames := 0
	var samples: Array = []
	for frame in 360:
		var seconds := float(frame) / FPS
		# Face/three-quarter walk, then orbit behind while running through the
		# valley. The physical player follows the trail, including its return.
		orbit.yaw = lerpf(PI+.30, .20, smoothstep(3.0, 5.5, seconds))
		if seconds > 9.0: orbit.yaw = lerpf(.20, -.65, smoothstep(9.0, 11.0, seconds))
		var moving := seconds >= .7 and seconds < 11.0
		var sprint := seconds >= 3.7 and seconds < 9.5
		if moving and target < route.size():
			var delta: Vector3 = route[target] - player.position
			delta.y = 0
			if delta.length() < .28 and target + 1 < route.size():
				target += 1
				delta = route[target] - player.position
				delta.y = 0
			drive(delta.normalized(), orbit.yaw, sprint)
		else: release_actions()
		await process_frame
		await RenderingServer.frame_post_draw
		var step := player.position - previous
		distance += Vector2(step.x, step.z).length()
		previous = player.position
		if player.is_on_floor(): grounded_frames += 1
		var speed := Vector2(player.velocity.x, player.velocity.z).length()
		if sprint: run_peak = maxf(run_peak, speed)
		elif moving: walk_peak = maxf(walk_peak, speed)
		var image: Image = game.viewport.get_texture().get_image()
		assert(image.save_png(FRAME_DIR + "/frame_%04d.png" % frame) == OK)
		if frame in [65, 180, 290]:
			var label: String = {65:"walking",180:"running",290:"turning"}[frame]
			assert(root.get_texture().get_image().save_png(OUTPUT + label + ".png") == OK)
		if frame % 30 == 0:
			samples.append({"second":seconds,"position":[player.position.x,player.position.y,player.position.z],"speed":speed,"state":player.visual.current_state,"on_floor":player.is_on_floor()})
	release_actions()
	var report := {"date":"2026-10-18", "engine":Engine.get_version_info().string,
		"map":"forest_valley.tscn", "visual":"reference_silhouette", "frames":360,
		"fps":FPS,"internal_resolution":[640,360],"distance_m":distance,
		"walk_peak_m_s":walk_peak,"run_peak_m_s":run_peak,
		"grounded_frames":grounded_frames,"trail_targets_reached":target,
		"movement":"original controller via input actions; no per-frame teleportation",
		"samples":samples}
	var file := FileAccess.open(OUTPUT + "recording.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t")+"\n")
	print("MOTION_RECORD ",JSON.stringify(report))
	quit(0 if distance > 15 and walk_peak > 3 and run_peak > 5 and target > 5 else 1)
