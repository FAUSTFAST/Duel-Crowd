extends SceneTree

var game: Node
var checks := 0
var failures := 0

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("run")

func check(ok: bool, label: String) -> void:
	checks += 1
	print("PASS: " if ok else "FAIL: ", label)
	if not ok: failures += 1

func frames(count: int = 30) -> void:
	for i in count: await physics_frame
	await RenderingServer.frame_post_draw

func key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	root.push_input(event)

func click(position: Vector2) -> void:
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = position
		root.push_input(event)

func run() -> void:
	root.size = Vector2i(1280, 720)
	var scene_path := "res://scenes/visual_lab/reference_silhouette.tscn" if "--silhouette" in OS.get_cmdline_user_args() else "res://scenes/visual_lab/character_equipment_lab.tscn"
	game = load(scene_path).instantiate()
	root.add_child(game)
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "startup captures mouse")
	await frames(75)
	var world: Node3D = game.world
	var player: CharacterBody3D = world.player
	var visual: Node3D = player.visual
	var equipment: Node = visual.equipment
	var skeleton: Skeleton3D = visual.skeleton
	var orbit: Node3D = player.orbit
	check(equipment.equipped.is_empty() and equipment.instances.is_empty(), "default no equipment or item instances")
	check(equipment.SLOTS.size() == 8 and equipment.catalog.size() == 4, "eight slots and four data resources")
	check(skeleton.get_bone_count() == 32, "new unified 32-bone humanoid")
	check(player.is_on_floor(), "original controller on floor")
	check(visual.find_children("*", "Skeleton3D", true, false).size() == 1, "base has exactly one skeleton")
	check(game.panel.get_viewport() == root and world.get_viewport() == game.viewport, "interactive UI in HD root, 3D in SubViewport")
	check(equipment.regions[&"hair"][0].visible and equipment.regions[&"torso_cloth"][0].visible, "base hair and tunic visible")
	check(not equipment.regions[&"body_under_cloth"][0].visible, "under-cloth body hidden from rendering")
	var real_mips := true
	for texture in visual.materials.textures:
		if texture != null: real_mips = real_mips and texture.get_image().has_mipmaps()
	check(real_mips, "actual working textures contain mipmaps")
	for clip in ["idle", "walk", "run", "turn_left", "turn_right"]:
		check(visual.animation_player.has_animation(clip), "imported fresh clip "+clip)
	var identities := [player.get_instance_id(), visual.get_instance_id(), skeleton.get_instance_id(), visual.animation_tree.get_instance_id(), orbit.get_instance_id()]
	var location := player.position
	check(equipment.equip(&"not_an_item") == ERR_INVALID_PARAMETER and equipment.equipped.is_empty(), "unknown ID rejected without state change")
	check(equipment.unequip(&"not_a_slot") == ERR_INVALID_PARAMETER, "unknown slot rejected")
	key(KEY_1)
	check(equipment.get_equipped(&"head") == &"study_helmet" and not equipment.regions[&"hair"][0].visible, "helmet equips and hides hair")
	key(KEY_2)
	check(equipment.get_equipped(&"body") == &"study_chest" and not equipment.regions[&"torso_cloth"][0].visible, "chest hides covered upper garment")
	check(equipment.regions[&"collar"].all(func(mesh): return not mesh.visible) and equipment.regions[&"waist_tie"].all(func(mesh): return not mesh.visible), "chest also hides folded neck cloth and leather belt attachments")
	check(equipment.regions[&"sleeves"][0].visible and equipment.regions[&"tunic_hem"][0].visible, "chest preserves uncovered sleeves and lower garment")
	key(KEY_3)
	key(KEY_4)
	check(equipment.equipped.size() == 4, "all four IDs equip immediately by single input route")
	check(visual.find_children("*", "Skeleton3D", true, false).size() == 1, "armor source skeletons removed; one live skeleton")
	var bindings_ok := true
	for slot in [&"head", &"body"]:
		for mesh in equipment.instances[slot].find_children("*", "MeshInstance3D", true, false):
			bindings_ok = bindings_ok and mesh.get_node(mesh.skeleton) == skeleton
			for i in mesh.skin.get_bind_count():
				bindings_ok = bindings_ok and skeleton.find_bone(mesh.skin.get_bind_name(i)) >= 0
	check(bindings_ok, "all armor skin binds resolve by name to base skeleton")
	var main_socket: BoneAttachment3D = equipment.instances[&"main_hand"]
	var off_socket: BoneAttachment3D = equipment.instances[&"off_hand"]
	check(main_socket.bone_name == "Hand_R" and off_socket.bone_name == "Hand_L" and not main_socket.override_pose, "sword and shield use non-overriding hand bone attachments")
	var count_before := visual.find_children("*", "MeshInstance3D", true, false).size()
	equipment.equip(&"study_sword")
	check(count_before == visual.find_children("*", "MeshInstance3D", true, false).size(), "equipping same ID is idempotent")
	# Validate atomic rejection with an intentionally wrong bind skeleton.
	var original_item: Resource = equipment.catalog[&"study_helmet"]
	var bad: Resource = original_item.duplicate()
	bad.item_id = &"bad_rig"
	bad.model = load("res://assets/characters/ashen_knight/ashen_knight.glb")
	equipment.catalog[bad.item_id] = bad
	check(equipment.equip(&"bad_rig") == ERR_INVALID_DATA and equipment.get_equipped(&"head") == &"study_helmet", "incompatible armor rejected atomically, existing helmet retained")
	equipment.catalog.erase(bad.item_id)
	var material_count: int = visual.materials.materials.size()
	for i in 40:
		for item in equipment.ITEMS: equipment.equip(item.item_id)
		equipment.clear()
	check(equipment.instances.is_empty() and visual.find_children("*", "Skeleton3D", true, false).size() == 1, "40 full equip/clear cycles leave no mounts or extra skeletons")
	check(visual.materials.materials.size() == material_count, "repeated swaps reuse bounded material cache")
	check(identities == [player.get_instance_id(), visual.get_instance_id(), skeleton.get_instance_id(), visual.animation_tree.get_instance_id(), orbit.get_instance_id()] and player.position == location, "equip never reloads actor, skeleton, animation tree or camera")
	check(equipment.regions[&"hair"][0].visible and equipment.regions[&"torso_cloth"][0].visible and not equipment.regions[&"body_under_cloth"][0].visible, "clear restores exact base visibility")
	check(equipment.regions[&"collar"].all(func(mesh): return mesh.visible) and equipment.regions[&"waist_tie"].all(func(mesh): return mesh.visible), "clear restores all traveler collar and belt surfaces")
	# Actual root GUI click after releasing cursor. Buttons must not recapture.
	key(KEY_ESCAPE)
	await frames(2)
	var button: CheckButton = game.item_buttons[&"study_helmet"]
	click(button.get_global_rect().get_center())
	check(equipment.get_equipped(&"head") == &"study_helmet" and Input.mouse_mode == Input.MOUSE_MODE_VISIBLE, "HD GUI click equips without forwarding click to mouse capture")
	click(button.get_global_rect().get_center())
	check(equipment.get_equipped(&"head") == &"", "GUI click unequips immediately")
	click(Vector2(640, 360))
	check(Input.mouse_mode == Input.MOUSE_MODE_CAPTURED, "click game recaptures mouse")
	for res in [0,1,2]:
		game.set_resolution(res)
		var yaw: float = orbit.yaw
		var motion := InputEventMouseMotion.new()
		motion.screen_relative = Vector2(10,0)
		root.push_input(motion)
		check(is_equal_approx(angle_difference(yaw, orbit.yaw),-.04), "one relative mouse route at resolution "+str(res))
	game.set_resolution(1)
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	var distance: float = orbit.distance
	root.push_input(wheel)
	check(orbit.distance < distance, "wheel zoom preserved")
	key(KEY_F3)
	equipment.equip(&"study_chest")
	check(player.study_materials.materials.all(func(m): return m.albedo_texture == null), "newly equipped material respects F3 disabled state")
	key(KEY_F3)
	check(player.study_materials.materials.any(func(m): return m.albedo_texture != null), "F3 restores original maps")
	key(KEY_L)
	check(world.forest_light and world.environment.fog_enabled, "lighting comparison works")
	key(KEY_L)
	for item in equipment.ITEMS: equipment.equip(item.item_id)
	main_socket = equipment.instances[&"main_hand"]
	orbit.yaw = 0
	Input.action_press("move_forward")
	await frames(30)
	check(visual.current_state == "walk" and player.position.distance_to(location)>1 and player.is_on_floor(), "equipped WASD walking and original collision")
	var hand_before := main_socket.global_transform
	Input.action_press("sprint")
	await frames(30)
	check(visual.current_state == "run" and Vector2(player.velocity.x,player.velocity.z).length()>5.5, "equipped Shift run state")
	check(not main_socket.global_transform.is_equal_approx(hand_before), "rigid sword moves with actual animation")
	check(main_socket.transform.is_equal_approx(skeleton.get_bone_global_pose(skeleton.find_bone("Hand_R"))), "socket matches animated hand pose")
	equipment.clear()
	await frames(12)
	check(visual.current_state == "run" and equipment.equipped.is_empty(), "unequip while running retains animation")
	Input.action_release("sprint")
	Input.action_release("move_forward")
	await frames(35)
	check(visual.current_state == "idle", "base decelerates to idle")
	# push_input delivers callbacks but does not mutate Input's action state.
	# Match the original controller regression for physics-polled reset.
	Input.action_press("reset")
	await frames(2)
	Input.action_release("reset")
	await frames(50)
	check(player.position.distance_to(player.spawn_point)<.1, "reset remains functional")
	# Animation-disabled byte equality, then restore real animation for performance.
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	orbit.yaw = PI + 0.3
	orbit.pitch = -0.20
	orbit.distance = 3.8
	world.set_art_animation(false)
	await frames(150)
	var still: PackedByteArray = game.viewport.get_texture().get_image().get_data()
	await frames(20)
	check(still == game.viewport.get_texture().get_image().get_data(), "frozen base actual pixels stable")
	world.set_art_animation(true)
	await frames(20)
	check(still != game.viewport.get_texture().get_image().get_data(), "real skeletal idle changes image")
	for equipped in [false,true]:
		if equipped:
			for item in equipment.ITEMS: equipment.equip(item.item_id)
		await frames(45)
		var samples: Array[float] = []
		var last := Time.get_ticks_usec()
		for i in 180:
			await process_frame
			var now := Time.get_ticks_usec()
			samples.append((now-last)/1000.0)
			last = now
		samples.sort()
		var total := 0.0
		for sample in samples: total += sample
		print("PERF equipped=",equipped," mean_ms=",total/samples.size()," p95_ms=",samples[int(samples.size()*.95)]," draw_calls=",Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	check(world.animation_enabled, "real animations enabled during performance sampling")
	print("EQUIPMENT RESULT ",checks," checks, ",failures," failures")
	quit(1 if failures else 0)
