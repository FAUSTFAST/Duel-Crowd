extends "res://scripts/preview/local_model_world.gd"
## New local experiment. Original static preview/map/controller resources stay intact.
const Motion = preload("res://scripts/preview/local_motion.gd")
const Profile = preload("res://scripts/wayfarer/locomotion_profile.gd")
var motion: Node

func _ready() -> void:
	super._ready()
	if not load_error.is_empty():
		return
	motion = Motion.new()
	# Keep the mixer and the imported rig in one subtree when switching modes.
	local_model.add_child(motion)
	if not motion.setup(local_model):
		load_error = motion.error
		return
	var profile := Profile.new()
	profile.walk_speed = Motion.WALK_SPEED
	profile.run_speed = Motion.RUN_SPEED
	profile.acceleration = 4.5
	profile.braking = 7.0
	profile.reversal_braking = 9.0
	profile.turn_degrees_per_second = 260.0
	player.locomotion_profile = profile
	player.walk_speed = Motion.WALK_SPEED
	player.run_speed = Motion.RUN_SPEED
	player.orbit.distance = 5.0
	player.orbit.pitch = -0.32
	player.spawn_point = display_root.global_position
	# Evaluate after the existing player's physics; camera follows at priority 10.
	process_physics_priority = 5
	set_inspecting(false)
	print("LOCAL_MOTION_READY: idle/walk/run; local animation study")

func set_inspecting(value: bool) -> void:
	if not load_error.is_empty():
		return
	if motion == null:
		super.set_inspecting(value)
		return
	inspecting = value
	player.velocity = Vector3.ZERO
	player.set_physics_process(not value)
	player.visual.visible = false
	if value:
		display_root.reparent(self, true)
	else:
		player.global_position = display_root.global_position
		player.reset_physics_interpolation()
		display_root.reparent(player, false)
		display_root.position = Vector3.ZERO
		display_root.rotation = Vector3(0, player.visual.rotation.y + PI, 0)
	player.orbit.target = display_root if value else player
	player.orbit.follow_offset = Vector3(0, 0.95, 0)
	player.orbit.reset_physics_interpolation()

func _physics_process(delta: float) -> void:
	if motion == null or not load_error.is_empty():
		return
	if not inspecting:
		# Imported model faces +Z, the existing controller's visual faces -Z.
		display_root.rotation.y = player.visual.rotation.y + PI
	var real_velocity: Vector3 = player.get_real_velocity()
	var speed := 0.0 if inspecting else Vector2(real_velocity.x, real_velocity.z).length()
	motion.update_motion(delta, speed)

func set_art_animation(value: bool) -> void:
	super.set_art_animation(value)
	if motion != null:
		motion.set_enabled(value)
