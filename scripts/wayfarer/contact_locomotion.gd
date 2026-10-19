extends "res://scripts/wayfarer/wayfarer_visual.gd"
## Nine original clips. Shared cycle phase, interrupted starts, support-side stops.
const GAIT_SPEEDS := [1.8, 3.2, 4.6]
const GAIT_PERIODS := [.82, .72, .66]
@export var start_seconds := .28
@export var stop_seconds := .30
@export var blend_seconds := .12
var gait_phase := 0.0
var motion_mode := "idle"
var mode_time := 0.0

func _build_animation_tree() -> void:
	var machine := AnimationNodeStateMachine.new()
	for state in ["idle", "start", "stop_left", "stop_right", "turn_left", "turn_right"]:
		var clip := animation_player.get_animation(state)
		clip.loop_mode = Animation.LOOP_LINEAR if state == "idle" else Animation.LOOP_NONE
		var node := AnimationNodeAnimation.new()
		node.animation = state
		machine.add_node(state, node)
	var move := AnimationNodeBlendSpace1D.new()
	move.min_space = GAIT_SPEEDS[0]
	move.max_space = GAIT_SPEEDS[2]
	move.sync = true
	for i in 3:
		var node := AnimationNodeAnimation.new()
		node.animation = ["walk", "jog", "run"][i]
		animation_player.get_animation(node.animation).loop_mode = Animation.LOOP_LINEAR
		move.add_blend_point(node, GAIT_SPEEDS[i], -1, node.animation)
	machine.add_node("move", move)
	var states := ["idle", "start", "stop_left", "stop_right", "turn_left", "turn_right", "move"]
	for a in states:
		for b in states:
			if a == b: continue
			var transition := AnimationNodeStateMachineTransition.new()
			transition.xfade_time = blend_seconds
			machine.add_transition(a, b, transition)
	var blend := AnimationNodeBlendTree.new()
	blend.add_node("states", machine)
	blend.add_node("speed", AnimationNodeTimeScale.new())
	blend.connect_node("speed", 0, "states")
	blend.connect_node("output", 0, "speed")
	animation_tree = AnimationTree.new()
	animation_tree.name = "ContactLocomotionTree"
	add_child(animation_tree)
	animation_tree.anim_player = animation_tree.get_path_to(animation_player)
	animation_tree.tree_root = blend
	animation_tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	animation_tree.active = true
	playback = animation_tree.get("parameters/states/playback")
	playback.start("idle")
	animation_tree.advance(0)

func _change_mode(next: String) -> void:
	if next == motion_mode: return
	motion_mode = next
	mode_time = 0
	playback.travel(next)
	if next == "move": gait_phase = 0

func update_locomotion(delta: float, horizontal_speed: float) -> void:
	var angular_speed := angle_difference(previous_yaw, rotation.y) / maxf(delta, .001)
	previous_yaw = rotation.y
	if not animation_enabled: return
	mode_time += delta
	if horizontal_speed > .09:
		if motion_mode == "idle" or motion_mode.begins_with("stop"):
			_change_mode("start" if horizontal_speed < 1.0 else "move")
		elif motion_mode == "start" and (mode_time >= start_seconds or horizontal_speed > 2.2):
			_change_mode("move")
		elif motion_mode.begins_with("turn"):
			_change_mode("move")
	elif absf(angular_speed) > .8:
		_change_mode("turn_left" if angular_speed > 0 else "turn_right")
	elif motion_mode == "move" or motion_mode == "start":
		_change_mode("stop_left" if gait_phase < .25 or gait_phase > .75 else "stop_right")
	elif motion_mode.begins_with("stop") and mode_time >= stop_seconds:
		_change_mode("idle")
	elif motion_mode == "idle" and absf(angular_speed) > .8:
		_change_mode("turn_left" if angular_speed > 0 else "turn_right")
	elif motion_mode.begins_with("turn") and mode_time >= .46:
		_change_mode("idle")
	var cadence := 1.0
	if motion_mode == "move":
		var segment := 0 if horizontal_speed <= 3.2 else 1
		var alpha := clampf((horizontal_speed - GAIT_SPEEDS[segment]) / (GAIT_SPEEDS[segment+1] - GAIT_SPEEDS[segment]), 0, 1)
		var period: float = lerpf(GAIT_PERIODS[segment], GAIT_PERIODS[segment+1], alpha)
		cadence = clampf(horizontal_speed / maxf(GAIT_SPEEDS[0], horizontal_speed), .08, 1.3) / period
		gait_phase = fposmod(gait_phase + delta * cadence, 1.0)
		animation_tree.set("parameters/states/move/blend_position", clampf(horizontal_speed, 1.8, 4.6))
	animation_tree.set("parameters/speed/scale", cadence)
	animation_tree.advance(delta)
	current_state = ("run" if horizontal_speed > 3.7 else "walk") if motion_mode == "move" else motion_mode
	# Relaxed empty hands; equipment still owns its compatible grip pose.
	for side in ["R", "L"]:
		var occupied: bool = equipment.get_equipped(&"main_hand" if side == "R" else &"off_hand") != &""
		for i in 4:
			var finger: String = ["Index", "Middle", "Ring", "Little"][i]
			skeleton.set_bone_pose_rotation(skeleton.find_bone(finger+"_"+side), Quaternion(Vector3.RIGHT, -.65 if occupied else -.20-i*.025))

func set_animation_enabled(enabled: bool) -> void:
	animation_enabled = enabled
	if not enabled:
		motion_mode = "idle"
		current_state = "idle"
		mode_time = 0
		gait_phase = 0
		playback.start("idle", true)
		animation_tree.set("parameters/speed/scale", 1.0)
		animation_tree.advance(0)
