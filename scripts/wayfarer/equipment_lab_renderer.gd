extends "res://scripts/rendering/pixel_renderer.gd"

var item_buttons: Dictionary = {}
var pose_button: Button
var summary: Label
var panel: PanelContainer

func _ready() -> void:
	super._ready()
	panel = PanelContainer.new()
	panel.name = "EquipmentDebugUI"
	panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	panel.offset_left = -282
	panel.offset_right = -20
	panel.offset_top = 22
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.035, 0.05, 0.065, 0.96)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 14
	style.content_margin_bottom = 14
	panel.add_theme_stylebox_override("panel", style)
	hud.add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 9)
	panel.add_child(box)
	var title := Label.new()
	title.text = "WAYFARER / EQUIPMENT STUDY"
	title.add_theme_font_size_override("font_size", 14)
	box.add_child(title)
	summary = Label.new()
	box.add_child(summary)
	for i in world.equipment.ITEMS.size():
		var item: Resource = world.equipment.ITEMS[i]
		var button := CheckButton.new()
		button.text = "%d  %s" % [i+1, item.display_name]
		button.focus_mode = Control.FOCUS_NONE
		button.toggled.connect(_on_item_toggled.bind(item.item_id))
		box.add_child(button)
		item_buttons[item.item_id] = button
	var clear_button := Button.new()
	clear_button.text = "0  Unequip all"
	clear_button.focus_mode = Control.FOCUS_NONE
	clear_button.pressed.connect(world.equipment.clear)
	box.add_child(clear_button)
	pose_button = Button.new()
	pose_button.focus_mode = Control.FOCUS_NONE
	pose_button.pressed.connect(world.cycle_pose)
	box.add_child(pose_button)
	var help := Label.new()
	help.text = "Esc: cursor / click buttons\nClick game: capture mouse\nL: light   P: preview pose\nWASD / Shift / Wheel unchanged\nART CANDIDATE - not final art"
	help.add_theme_font_size_override("font_size", 13)
	box.add_child(help)
	world.equipment.equipment_changed.connect(func(_slot, _id): _refresh())
	world.pose_changed.connect(_refresh)
	_refresh()

func _on_item_toggled(_enabled: bool, id: StringName) -> void:
	world.toggle_item(id)

func _refresh() -> void:
	for id in item_buttons:
		var item: Resource = world.equipment.catalog[id]
		item_buttons[id].set_pressed_no_signal(world.equipment.get_equipped(item.slot) == id)
	summary.text = "No armor / empty hands" if world.equipment.equipped.is_empty() else "%d / 4 items equipped" % world.equipment.equipped.size()
	pose_button.text = "P  " + ["Playable", "Idle preview", "Walk preview", "Run preview"][world.pose_index]
