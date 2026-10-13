extends Node3D

@export_range(6.0, 24.0) var frames_per_second: float = 12.0
@export var flame_pixel_size: float = 0.025
@export_range(0.0, 0.2) var light_variation: float = 0.055
var animation_enabled: bool = true
var sprite: Sprite3D
var light: OmniLight3D
var elapsed: float = 0.0
var phase_offset: int = 0
var current_step: int = -1

func _ready() -> void:
	add_to_group("art_flames")
	sprite = Sprite3D.new()
	sprite.texture = load("res://assets/textures/torch_flame.png")
	sprite.hframes = 8
	sprite.pixel_size = flame_pixel_size
	sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	sprite.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	sprite.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	sprite.position.y = 0.34
	add_child(sprite)
	_apply_frame(3)

func _process(delta: float) -> void:
	if not animation_enabled:
		return
	elapsed += delta
	var step := int(elapsed * frames_per_second)
	if step != current_step:
		current_step = step
		_apply_frame((step + phase_offset) % 8)

func _apply_frame(frame: int) -> void:
	sprite.frame = frame
	if light != null:
		light.light_energy = 1.55 * (1.0 + light_variation * sin(frame * TAU / 8.0))

# For deterministic captures and static stability checks only; gameplay stays animated.
func set_animation_enabled(enabled: bool) -> void:
	animation_enabled = enabled
	if not enabled:
		_apply_frame(3)
