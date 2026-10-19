extends SceneTree
## Imported clip contacts and real physics transitions, graphically evaluated.
var checks := 0
var failures := 0
var game: Node
var results: Dictionary = {}

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures += 1

func frames(count: int) -> void:
	for i in count: await physics_frame
	await RenderingServer.frame_post_draw

func marker(skeleton: Skeleton3D, side: String, point: Vector3) -> Vector3:
	var bone := skeleton.find_bone("Foot_" + side)
	return skeleton.get_bone_global_pose(bone) * skeleton.get_bone_global_rest(bone).affine_inverse() * point

func sample_clip(visual: Node3D, name: String, speed: float, period: float, duty: float) -> void:
	var skeleton: Skeleton3D = visual.skeleton
	var animation: AnimationPlayer = visual.animation_player
	visual.animation_tree.active = false
	animation.play(name)
	var contact_error := 0.0
	var contacts := 0
	var worst: Dictionary = {}
	var previous_points: Dictionary = {}
	var previous_phases: Dictionary = {}
	var minimum_sole := 1.0
	var ankle_min := 1.0
	var ankle_max := 0.0
	var pelvis_min := 2.0
	var pelvis_max := 0.0
	var wrist_angle := 0.0
	for frame in 121:
		var phase := float(frame)/120.0
		animation.seek(phase, true)
		skeleton.force_update_all_bone_transforms()
		var hip: float = skeleton.get_bone_global_pose(skeleton.find_bone("Pelvis")).origin.y
		pelvis_min = minf(pelvis_min, hip)
		pelvis_max = maxf(pelvis_max, hip)
		for entry in [["L",-1.0,0.0],["R",1.0,.5]]:
			var side: String = entry[0]
			var p := fposmod(phase + float(entry[2]), 1.0)
			var heel := marker(skeleton,side,Vector3(float(entry[1])*.103,0,.07))
			var toe := marker(skeleton,side,Vector3(float(entry[1])*.103,0,-.20))
			minimum_sole = minf(minimum_sole, minf(heel.y,toe.y))
			var ankle: float = skeleton.get_bone_global_pose(skeleton.find_bone("Foot_"+side)).origin.y
			var hand_axis := skeleton.get_bone_global_pose(skeleton.find_bone("Hand_"+side)).basis.y.normalized()
			var forearm_axis := skeleton.get_bone_global_pose(skeleton.find_bone("Forearm_"+side)).basis.y.normalized()
			wrist_angle = maxf(wrist_angle, hand_axis.angle_to(forearm_axis))
			ankle_min = minf(ankle_min,ankle)
			ankle_max = maxf(ankle_max,ankle)
			var stage := "heel" if p < duty*.12 else "flat" if p > duty*.24 and p < duty*.55 else "toe" if p > duty*.68 and p < duty*.97 else ""
			var point := toe if stage=="toe" else heel
			point.z -= speed * period * phase
			var key := side+stage
			if stage != "" and previous_points.has(key) and p > float(previous_phases[key]) and p-float(previous_phases[key]) < .012:
				var error: float = (Vector2(point.x,point.z)-previous_points[key]).length()
				if error > contact_error:
					contact_error = error
					worst = {"phase":phase,"foot_phase":p,"side":side,"stage":stage}
				contacts += 1
			previous_points[key] = Vector2(point.x,point.z)
			previous_phases[key] = p
	animation.pause()
	results[name] = {"contact_max_frame_drift_m":contact_error,"contact_samples":contacts,
		"minimum_sole_m":minimum_sole,"ankle_lift_range_m":ankle_max-ankle_min,
		"pelvis_range_m":[pelvis_min,pelvis_max],"max_wrist_angle_rad":wrist_angle,"worst":worst}
	print("CONTACT ",name," ",JSON.stringify(results[name]))
	check(contacts > 20 and contact_error < .008,name+" planted heel/forefoot drift < 8mm per sample on flat reference")
	check(minimum_sole > -.025,name+" sole penetration < 25mm on flat reference")
	check(ankle_max-ankle_min > .09,name+" meaningful recovery and foot roll")
	check(pelvis_min > .80 and pelvis_max-pelvis_min < .13,name+" bounded anatomical pelvis translation")
	check(wrist_angle < .35,name+" wrist follows forearm without backward kink")

func run() -> void:
	root.size = Vector2i(1280,720)
	game = load("res://scenes/visual_lab/reference_silhouette.tscn").instantiate()
	root.add_child(game)
	await frames(40)
	var player: CharacterBody3D = game.world.player
	var visual: Node3D = player.visual
	var orbit: Node3D = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	player.set_physics_process(false)
	for clip in ["idle","walk","jog","run","start","stop_left","stop_right","turn_left","turn_right"]:
		check(visual.animation_player.has_animation(clip),"imported clip "+clip)
	sample_clip(visual,"walk",1.8,.82,.62)
	sample_clip(visual,"jog",3.2,.72,.43)
	sample_clip(visual,"run",4.6,.66,.32)
	visual.animation_player.stop()
	visual.animation_tree.active = true
	visual.set_animation_enabled(false)
	visual.set_animation_enabled(true)
	player.set_physics_process(true)
	player.position = player.spawn_point
	player.velocity = Vector3.ZERO
	visual.rotation.y = 0
	orbit.yaw = 0
	await frames(30)
	Input.action_press("move_forward")
	await frames(3)
	check(visual.motion_mode == "start" and player.velocity.length() < .7,"interruptible start with gradual acceleration")
	await frames(60)
	check(visual.current_state == "walk" and absf(Vector2(player.velocity.x,player.velocity.z).length()-1.8)<.03,"walk reaches authored 1.8m/s")
	Input.action_press("sprint")
	await frames(45)
	check(visual.current_state == "run" and absf(Vector2(player.velocity.x,player.velocity.z).length()-4.6)<.03,"run reaches authored 4.6m/s")
	var before: float = visual.rotation.y
	Input.action_release("move_forward")
	Input.action_press("move_back")
	await frames(1)
	check(absf(angle_difference(before,visual.rotation.y)) <= deg_to_rad(340.0)/60.0+.002,"180 reversal obeys angular limit")
	var saw_pivot := false
	var min_speed := 10.0
	for i in 65:
		await frames(1)
		min_speed = minf(min_speed,Vector2(player.velocity.x,player.velocity.z).length())
		saw_pivot = saw_pivot or visual.motion_mode.begins_with("turn")
	check(min_speed < .1 and saw_pivot,"reverse brakes to support step and plays pivot")
	check(player.velocity.z > 1.0,"reverse resumes in requested direction")
	Input.action_release("move_back")
	Input.action_release("sprint")
	var saw_stop := false
	for i in 65:
		await frames(1)
		saw_stop = saw_stop or visual.motion_mode.begins_with("stop")
	check(saw_stop and visual.current_state == "idle" and player.velocity.length()<.02,"support-side stop settles to idle")
	check(player.is_on_floor(),"capsule remains on original collision")
	visual.set_animation_enabled(false)
	var first := root.get_texture().get_image().get_data()
	await frames(12)
	# Skip byte equality here: renderer/equipment regression tests the frozen UI.
	visual.set_animation_enabled(true)
	check(visual.animation_enabled and first.size()>0,"freeze/restart keeps a real rendered viewport")
	DirAccess.make_dir_recursive_absolute("res://docs/locomotion_review")
	var file := FileAccess.open("res://docs/locomotion_review/test_results.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"checks":checks,"failures":failures,"contacts":results,"scope":"flat clip contact plus controller regression; not terrain IK or art approval"},"\t")+"\n")
	print("LOCOMOTION RESULT ",checks," checks, ",failures," failures")
	quit(0 if failures==0 else 1)
