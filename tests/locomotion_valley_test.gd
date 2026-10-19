extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void:
	call_deferred("run")
func frames(n: int) -> void:
	for i in n: await physics_frame
	await RenderingServer.frame_post_draw
func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ",label)
	if not ok: failures += 1
func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)
func run() -> void:
	root.size = Vector2i(1280,720)
	var game: Node = load("res://scenes/visual_lab/locomotion_valley.tscn").instantiate()
	root.add_child(game)
	await frames(40)
	var player: CharacterBody3D = game.world.player
	var visual: Node3D = player.visual
	var equipment: Node = visual.equipment
	check(equipment.equipped.is_empty(),"new forest scene starts without armor or held items")
	check(player.locomotion_profile != null and player.is_on_floor(),"candidate profile and original terrain collision work")
	var skeleton_id: int = visual.skeleton.get_instance_id()
	for code in [KEY_1,KEY_2,KEY_3,KEY_4]:
		key(code)
		await frames(2)
	check(equipment.equipped.size()==4,"single input route equips four patterned items in forest")
	check(visual.materials.materials.any(func(m):return m.resource_name.begins_with("Way_pattern_chest")),"actual patterned armor materials loaded")
	key(KEY_2)
	await frames(2)
	check(equipment.get_equipped(&"body")==&"" and equipment.regions[&"torso_cloth"][0].visible,"same key unequips and restores tunic")
	key(KEY_0)
	await frames(2)
	check(equipment.equipped.is_empty() and visual.skeleton.get_instance_id()==skeleton_id,"clear restores base without replacing skeleton")
	key(KEY_ESCAPE)
	check(Input.mouse_mode==Input.MOUSE_MODE_VISIBLE,"Esc still releases forest mouse")
	print("LOCOMOTION_VALLEY RESULT ",checks," checks, ",failures," failures")
	quit(1 if failures else 0)
