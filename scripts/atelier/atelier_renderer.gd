extends "res://scripts/rendering/pixel_renderer.gd"

var comparison_label: Label

func _ready() -> void:
	super._ready()
	var panel := ColorRect.new()
	panel.color = Color(0.03, 0.05, 0.07, 0.9)
	panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	panel.offset_left = 24
	panel.offset_right = -24
	panel.offset_top = -140
	panel.offset_bottom = -74
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(panel)
	comparison_label = Label.new()
	comparison_label.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	comparison_label.offset_left = 36
	comparison_label.offset_right = -36
	comparison_label.offset_top = -132
	comparison_label.offset_bottom = -82
	comparison_label.clip_text = true
	comparison_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	comparison_label.add_theme_font_size_override("font_size", 16)
	hud.add_child(comparison_label)
	world.comparison_changed.connect(_refresh_comparison)
	_refresh_comparison()

func _refresh_comparison() -> void:
	comparison_label.text = "%s  |  %s  |  ART CANDIDATE\nB Compare  L Light  0 Playable  1 Idle  2 Walk preview  3 Run preview" % ["NEW: THORN WARDEN" if world.new_variant else "PREVIOUS: ASHEN KNIGHT", "Forest light" if world.forest_light else "Neutral light"]
