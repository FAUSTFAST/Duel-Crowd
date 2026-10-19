extends Node3D

const Materials = preload("res://scripts/characters/knight_materials.gd")
@export var walk_reference_speed: float = 3.2
@export var run_reference_speed: float = 5.8
@export var transition_seconds: float = 0.16
var materials := Materials.new()
var skeleton: Skeleton3D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var playback: AnimationNodeStateMachinePlayback
var animation_enabled := true
var previous_yaw: float = 0.0
var turn_hold: float = 0.0
var current_state := "idle"
var last_turn_state := "turn_left"

func _ready() -> void:
	materials.apply(self)
	skeleton = find_child("Skeleton3D", true, false)
	animation_player = find_child("AnimationPlayer", true, false)
	_build_animation_tree()

func _build_animation_tree() -> void:
	var machine := AnimationNodeStateMachine.new()
	for state in ["idle", "walk", "run", "turn_left", "turn_right"]:
		var clip := animation_player.get_animation(state)
		clip.loop_mode = Animation.LOOP_LINEAR
		var node := AnimationNodeAnimation.new()
		node.animation = state
		machine.add_node(state, node)
	for from_state in ["idle", "walk", "run", "turn_left", "turn_right"]:
		for to_state in ["idle", "walk", "run", "turn_left", "turn_right"]:
			if from_state == to_state:
				continue
			var transition := AnimationNodeStateMachineTransition.new()
			transition.xfade_time = transition_seconds
			transition.switch_mode = AnimationNodeStateMachineTransition.SWITCH_MODE_SYNC if from_state in ["walk", "run"] and to_state in ["walk", "run"] else AnimationNodeStateMachineTransition.SWITCH_MODE_IMMEDIATE
			machine.add_transition(from_state, to_state, transition)
	var blend := AnimationNodeBlendTree.new()
	blend.add_node("states", machine)
	blend.add_node("speed", AnimationNodeTimeScale.new())
	blend.connect_node("speed", 0, "states")
	blend.connect_node("output", 0, "speed")
	animation_tree = AnimationTree.new()
	animation_tree.name = "LocomotionTree"
	add_child(animation_tree)
	animation_tree.anim_player = animation_tree.get_path_to(animation_player)
	animation_tree.tree_root = blend
	animation_tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	animation_tree.active = true
	playback = animation_tree.get("parameters/states/playback")
	playback.start("idle")
	animation_tree.advance(0.0)

func update_locomotion(delta: float, horizontal_speed: float) -> void:
	var angular_speed := angle_difference(previous_yaw, rotation.y) / maxf(delta, 0.001)
	previous_yaw = rotation.y
	if not animation_enabled:
		return
	turn_hold = maxf(0, turn_hold - delta)
	var desired := "idle"
	if horizontal_speed > 0.12:
		desired = "run" if horizontal_speed > (3.7 if current_state == "run" else 4.2) else "walk"
	# Turn clips pivot the torso/head; preserve locomotion during fast turns.
	# Low-speed heading changes briefly lead with the upper body.
	if absf(angular_speed) > 3.5 and horizontal_speed > 0.12 and horizontal_speed < 2.0:
		last_turn_state = "turn_left" if angular_speed > 0 else "turn_right"
		turn_hold = 0.12
	if turn_hold > 0 and horizontal_speed < 2.0:
		desired = last_turn_state
	if desired != current_state:
		playback.travel(desired)
		current_state = desired
	var scale_factor := 1.0
	if desired == "walk":
		scale_factor = clampf(horizontal_speed / walk_reference_speed, 0.15, 1.4)
	elif desired == "run":
		scale_factor = clampf(horizontal_speed / run_reference_speed, 0.5, 1.4)
	animation_tree.set("parameters/speed/scale", scale_factor)
	animation_tree.advance(delta)

func set_animation_enabled(enabled: bool) -> void:
	animation_enabled = enabled
	if not enabled:
		current_state = "idle"
		turn_hold = 0.0
		playback.start("idle", true)
		animation_tree.advance(0.0)
