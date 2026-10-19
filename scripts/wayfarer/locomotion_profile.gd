extends Resource
## Candidate-only, physics-owned in-place locomotion. No input routing here.
@export var walk_speed := 1.8
@export var run_speed := 4.6
@export var acceleration := 7.5
@export var braking := 12.0
@export var reversal_braking := 16.0
@export var turn_degrees_per_second := 340.0
@export var pivot_threshold_degrees := 35.0

func step(current: Vector2, requested: Vector2, delta: float, facing: float) -> Vector2:
	var reversing := current.length() > .6 and requested.length() > .1 and current.normalized().dot(requested.normalized()) < -.25
	# Establish a support step before pushing into a reversed direction.
	if reversing:
		return current.move_toward(Vector2.ZERO, reversal_braking * delta)
	if current.length() < .6 and requested.length() > .1:
		var target := atan2(-requested.x, -requested.y)
		if absf(angle_difference(facing, target)) > deg_to_rad(pivot_threshold_degrees):
			return current.move_toward(Vector2.ZERO, braking * delta)
	var rate := acceleration if requested.length() > current.length() else braking
	return current.move_toward(requested, rate * delta)

func face_velocity(model: Node3D, velocity: Vector2, delta: float, requested: Vector2) -> void:
	var heading := requested if velocity.length() < .6 and requested.length() > .1 else velocity
	if heading.length() < .08:
		return
	var target := atan2(-heading.x, -heading.y)
	var limit := deg_to_rad(turn_degrees_per_second) * delta
	model.rotation.y += clampf(angle_difference(model.rotation.y, target), -limit, limit)
