extends SceneTree

var failures := 0
var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	print("PASS: " if ok else "FAIL: ", label)
	if not ok:
		failures += 1

func frames(count: int) -> void:
	for i in count:
		await physics_frame

func sample_pose(model: Node3D, clip: String, seconds: float, bone: String) -> Vector3:
	model.animation_player.stop()
	model.animation_player.play(clip)
	model.animation_player.advance(0)
	model.animation_player.advance(seconds)
	model.skeleton.force_update_all_bone_transforms()
	return model.skeleton.get_bone_global_pose(model.skeleton.find_bone(bone)).origin

func run() -> void:
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	await frames(120)
	var player: CharacterBody3D = game.world.player
	var model: Node3D = player.visual
	player.orbit.set_process_input(false)
	player.orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	check(model.skeleton.get_bone_count() == 38, "38-bone imported humanoid skeleton")
	check(model.materials.materials.size() == 5, "five reusable skinned materials")
	var capsule: CapsuleShape3D = player.get_child(0).shape
	check(is_equal_approx(capsule.radius, 0.3) and is_equal_approx(capsule.height, 1.8), "original collision capsule unchanged")
	model.animation_enabled = false
	model.animation_tree.active = false
	model.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for clip in ["idle", "walk", "run", "turn_left", "turn_right"]:
		check(model.animation_player.has_animation(clip), "imports clip " + clip)
	var idle_a := sample_pose(model, "idle", 0.1, "Chest")
	var idle_b := sample_pose(model, "idle", 0.7, "Chest")
	check(idle_a.distance_to(idle_b) > 0.001, "idle breathes through the skeleton")
	for info in [["walk", 3.2, 0.10, 0.20], ["run", 5.8, 0.025, 0.11]]:
		var a := sample_pose(model, info[0], info[2], "Foot_L")
		var b := sample_pose(model, info[0], info[3], "Foot_L")
		var residual := absf((b.z-a.z) - info[1]*(info[3]-info[2]))
		print("STANCE ", info[0], " a=", a, " b=", b, " world-slip=", residual)
		check(residual < 0.035, info[0] + " planted heel tracks authored movement within 3.5cm")
		check(absf(a.y-0.13)<0.035 and absf(b.y-0.13)<0.035, info[0] + " heel stays at ground reference height")
	var cape_a := sample_pose(model, "run", .1, "Cape_1_B")
	var cape_b := sample_pose(model, "run", .3, "Cape_1_B")
	print("CAPE ", cape_a, " ", cape_b)
	check(cape_a.distance_to(cape_b)>0.01, "cape bones deform during locomotion")
	sample_pose(model, "turn_left", .3, "Head")
	var turn_l: Quaternion = model.skeleton.get_bone_global_pose(model.skeleton.find_bone("Head")).basis.get_rotation_quaternion()
	sample_pose(model, "turn_right", .3, "Head")
	var turn_r: Quaternion = model.skeleton.get_bone_global_pose(model.skeleton.find_bone("Head")).basis.get_rotation_quaternion()
	check(turn_l.angle_to(turn_r) > 0.03, "left and right turn clips have different orientations")
	model.animation_player.stop()
	model.animation_tree.active = true
	model.animation_enabled = true
	model.playback.start("idle", true)
	player.orbit.yaw = 0
	Input.action_press("move_forward")
	await frames(30)
	check(model.current_state == "walk", "controller chooses walking")
	check(absf(float(model.animation_tree.get("parameters/speed/scale"))-1)<.05, "walking cadence follows actual velocity")
	model.set_animation_enabled(false)
	await frames(2)
	model.set_animation_enabled(true)
	await frames(20)
	check(model.current_state == "walk" and model.playback.get_current_node() == "walk", "resuming animation restores the actual locomotion state")
	Input.action_press("sprint")
	await frames(30)
	check(model.current_state == "run", "Shift selects running animation")
	Input.action_release("move_forward")
	Input.action_release("sprint")
	await frames(30)
	check(model.current_state == "idle", "deceleration returns to idle")
	Input.action_press("move_back")
	await frames(2)
	check(model.current_state in ["turn_left", "turn_right"], "heading reversal selects a turn lead-in")
	Input.action_release("move_back")
	await frames(30)
	check(player.is_on_floor(), "animated player retains terrain contact")
	game.world.set_art_animation(false)
	await frames(120)
	await RenderingServer.frame_post_draw
	var still_a: Image = game.viewport.get_texture().get_image()
	await frames(20)
	await RenderingServer.frame_post_draw
	var still_b: Image = game.viewport.get_texture().get_image()
	check(still_a.get_data() == still_b.get_data(), "test-only animation freeze yields stable pixels")
	game.world.set_art_animation(true)
	print("KNIGHT_ANIMATION_FAILURES ", failures)
	quit(1 if failures else 0)
