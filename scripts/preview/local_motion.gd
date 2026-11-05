extends Node
## Local study only. Three original, in-place clips; no input or root translation.
const WALK_SPEED := 1.25
const RUN_SPEED := 2.8
const WALK_STRIDE := 1.25
const RUN_STRIDE := 1.8
var animation_player: AnimationPlayer
var skeleton: Skeleton3D
var tree: AnimationTree
var current_state := "idle"
var move_weight := 0.0
var run_weight := 0.0
var enabled := true
var error := ""

func setup(model: Node3D) -> bool:
	for node in model.find_children("*", "AnimationPlayer", true, false):
		animation_player = node
		break
	for node in model.find_children("*", "Skeleton3D", true, false):
		skeleton = node
		break
	if animation_player == null or skeleton == null:
		error = "Local motion model needs a skeleton and animation player."
		return false
	var blend := AnimationNodeBlendTree.new()
	for clip in ["idle", "walk", "run"]:
		if not animation_player.has_animation(clip):
			error = "Missing motion clip: " + clip
			return false
		animation_player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		var node := AnimationNodeAnimation.new()
		node.animation = clip
		blend.add_node(clip, node)
	var gait := AnimationNodeBlend2.new()
	gait.sync = true
	blend.add_node("gait", gait)
	blend.connect_node("gait", 0, "walk")
	blend.connect_node("gait", 1, "run")
	var cadence := AnimationNodeTimeScale.new()
	blend.add_node("cadence", cadence)
	blend.connect_node("cadence", 0, "gait")
	var movement := AnimationNodeBlend2.new()
	blend.add_node("movement", movement)
	blend.connect_node("movement", 0, "idle")
	blend.connect_node("movement", 1, "cadence")
	blend.connect_node("output", 0, "movement")
	animation_player.stop()
	tree = AnimationTree.new()
	tree.name = "LocalLocomotionTree"
	add_child(tree)
	tree.anim_player = tree.get_path_to(animation_player)
	tree.root_node = tree.get_path_to(animation_player.get_node(animation_player.root_node))
	tree.tree_root = blend
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	tree.active = true
	update_motion(0.0, 0.0)
	return true

func update_motion(delta: float, speed: float) -> void:
	if tree == null or not enabled:
		return
	current_state = "idle" if speed < 0.08 else ("run" if speed > 1.9 else "walk")
	var smoothing := 1.0 - exp(-delta * 16.0)
	move_weight = lerpf(move_weight, smoothstep(0.03, 0.45, speed), smoothing)
	run_weight = lerpf(run_weight, smoothstep(1.4, 2.65, speed), smoothing)
	# Both gait clips use one-second phase. Their support distances differ.
	var stride := lerpf(WALK_STRIDE, RUN_STRIDE, run_weight)
	tree.set("parameters/gait/blend_amount", run_weight)
	tree.set("parameters/movement/blend_amount", move_weight)
	tree.set("parameters/cadence/scale", clampf(speed / stride, 0.05, 2.0))
	tree.advance(delta)

func set_enabled(value: bool) -> void:
	enabled = value
