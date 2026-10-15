extends SceneTree

var game: Node

func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		quit(2)
		return
	call_deferred("capture")

func settle(count: int = 45) -> void:
	for i in count:
		await physics_frame
	await RenderingServer.frame_post_draw

func save(label: String) -> void:
	assert(root.get_texture().get_image().save_png("res://docs/wayfarer/" + label + ".png") == OK)
	print("CAPTURE ", label)

func capture() -> void:
	DirAccess.make_dir_recursive_absolute("res://docs/wayfarer")
	root.size = Vector2i(1280, 720)
	game = load("res://scenes/visual_lab/character_equipment_lab.tscn").instantiate()
	root.add_child(game)
	await settle(60)
	var player: CharacterBody3D = game.world.player
	var initial_position := player.position
	var visual: Node3D = player.visual
	var orbit: Node3D = player.orbit
	var equipment: Node = visual.equipment
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	player.set_physics_process(false)
	game.hud.visible = false
	game.world.set_art_animation(false)
	for state in ["base", "equipped", "unequipped"]:
		if state == "equipped":
			for item in equipment.ITEMS:
				assert(equipment.equip(item.item_id) == OK)
		else:
			equipment.clear()
		for view in [["front", PI+0.3, -0.20, 3.8], ["rear", 0.3, -0.20, 3.8], ["gameplay", 0.16, -0.48, 8.0]]:
			orbit.yaw = view[1]
			orbit.pitch = view[2]
			orbit.distance = view[3]
			game.set_pixel_enabled(true)
			game.set_resolution(1)
			await settle(75)
			save(state + "_" + view[0] + "_640")
			if view[0] == "front":
				game.set_pixel_enabled(false)
				await settle()
				save(state + "_front_native")
				game.set_pixel_enabled(true)
				if state != "unequipped":
					for res in [0,2]:
						game.set_resolution(res)
						await settle()
						save(state + "_front_" + ["480","640","960"][res])
					game.set_resolution(1)
	# Individual equipment and actual imported poses.
	orbit.yaw = PI+0.3
	orbit.pitch = -0.2
	orbit.distance = 3.8
	for item in equipment.ITEMS:
		equipment.clear()
		equipment.equip(item.item_id)
		await settle()
		save(item.item_id)
	equipment.clear()
	for state in ["base", "equipped"]:
		if state == "equipped":
			for item in equipment.ITEMS: equipment.equip(item.item_id)
		visual.animation_tree.active = false
		visual.animation_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		for clip in ["walk", "run"]:
			var sheet := Image.create_empty(1280, 720, false, Image.FORMAT_RGBA8)
			for i in 4:
				visual.animation_player.stop()
				visual.animation_player.play(clip)
				visual.animation_player.advance(0)
				visual.animation_player.advance(0.025 + i*.145)
				await settle(3)
				var frame: Image = game.viewport.get_texture().get_image()
				frame.convert(Image.FORMAT_RGBA8)
				sheet.blit_rect(frame, Rect2i(0,0,640,360), Vector2i(i%2*640,int(i/2)*360))
			assert(sheet.save_png("res://docs/wayfarer/"+state+"_"+clip+".png") == OK)
		visual.animation_player.stop()
		visual.animation_tree.active = true
	# Restore real animation and input-driven movement, then capture HD interface.
	game.world.set_art_animation(true)
	player.set_physics_process(true)
	game.hud.visible = true
	await settle()
	save("debug_ui")
	game.hud.visible = false
	orbit.yaw = 0.16
	orbit.pitch = -0.48
	orbit.distance = 8.0
	Input.action_press("move_forward")
	Input.action_press("sprint")
	await settle(30)
	save("actual_running")
	print("RUNNING on_floor=",player.is_on_floor()," state=",visual.current_state)
	Input.action_release("sprint")
	Input.action_release("move_forward")
	# Preserve old knight: compare it in this exact fixture without saving scenes.
	player.set_physics_process(false)
	player.position = initial_position
	player.reset_physics_interpolation()
	visual.visible = false
	var old: Node3D = load("res://scenes/characters/thorn_knight_visual.tscn").instantiate()
	player.add_child(old)
	old.set_animation_enabled(false)
	for view in [["front",PI+.3,-.2,3.8],["gameplay",.16,-.48,8.0]]:
		orbit.yaw = view[1]
		orbit.pitch = view[2]
		orbit.distance = view[3]
		await settle(75)
		save("previous_knight_"+view[0]+"_640")
	old.free()
	game.free()
	# Temporary runtime appearance in the retained actual valley. No scene edits.
	game = load("res://scenes/visual_lab/forest_valley.tscn").instantiate()
	root.add_child(game)
	player = game.world.player
	player.visual.free()
	player.visual_scene = load("res://scenes/characters/wayfarer_visual.tscn")
	player._build_visual()
	visual = player.visual
	equipment = visual.equipment
	orbit = player.orbit
	orbit.set_process_input(false)
	orbit.set_process_unhandled_input(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	game.hud.visible = false
	game.world.set_art_animation(false)
	orbit.yaw = .16
	orbit.pitch = -.48
	orbit.distance = 7.0
	await settle(90)
	for state in ["base","equipped"]:
		if state == "equipped":
			for item in equipment.ITEMS: equipment.equip(item.item_id)
		await settle()
		save(state+"_forest_context")
	game.world.set_art_animation(true)
	Input.action_press("move_forward")
	Input.action_press("sprint")
	await settle(35)
	save("forest_running")
	print("FOREST RUN on_floor=",player.is_on_floor()," state=",visual.current_state)
	Input.action_release("sprint")
	Input.action_release("move_forward")
	quit()
