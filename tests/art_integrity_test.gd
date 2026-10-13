extends SceneTree

const Kit = preload("res://scripts/art/ruins_kit.gd")
const Meshes = preload("res://scripts/art/art_meshes.gd")
const Geo = preload("res://scripts/world/geometry.gd")
const Dressing = preload("res://scripts/art/forest_dressing.gd")
var failures: int = 0

func _initialize() -> void:
	call_deferred("_run")

func check(condition: bool, message: String) -> void:
	print("PASS: " if condition else "FAIL: ", message)
	if not condition:
		failures += 1

func triangles(mesh: Mesh) -> int:
	var count := 0
	for i in mesh.get_surface_count():
		var arrays := mesh.surface_get_arrays(i)
		var indices: Variant = arrays[Mesh.ARRAY_INDEX]
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		count += indices.size() / 3 if indices != null and not indices.is_empty() else vertices.size() / 3
	return count

func _run() -> void:
	var fixture := Node3D.new()
	root.add_child(fixture)
	var material := Geo.material(Color.WHITE)
	var non_indexed := Kit.block(fixture, Vector3(-3, 1, 0), Vector3(2, 2, 2), material, true)
	var nested := Node3D.new()
	fixture.add_child(nested)
	nested.position = Vector3(3, 1, 0)
	nested.rotation.y = 0.3
	var indexed := Geo.box(nested, Vector3(0, 1, 0), Vector3(1, 2, 1), material, true)
	var collider: StaticBody3D = indexed.get_child(0)
	var before_transform := collider.global_transform
	var expected := triangles(non_indexed.mesh) + triangles(indexed.mesh)
	Kit.batch_static(fixture)
	var combined := fixture.find_children("*", "MeshInstance3D", true, false)
	check(combined.size() == 1, "same material collapses to one mesh")
	check(triangles(combined[0].mesh) == expected, "mixed indexed/non-indexed triangles all preserved")
	check(collider.global_transform.is_equal_approx(before_transform), "nested collision transform preserved")
	check(fixture.find_children("*", "StaticBody3D", true, false).size() == 2, "all original colliders retained")
	fixture.free()
	var game: Node = load("res://scenes/rendering/pixel_game.tscn").instantiate()
	root.add_child(game)
	for i in 30:
		await physics_frame
	var world: Node3D = game.world
	check(world.player.is_on_floor(), "character still rests on original ground")
	check(world.player.left_leg.get_parent() == world.player.visual and world.player.right_arm.get_parent() == world.player.visual, "limb animation pivots remain separate from static torso")
	var parameters := PhysicsRayQueryParameters3D.create(Vector3(5, 2, -5), Vector3(5, -1, -5))
	check(not world.get_world_3d().direct_space_state.intersect_ray(parameters).is_empty(), "side wall collision survives world batching")
	parameters = PhysicsRayQueryParameters3D.create(Vector3(0, 1.5, 1), Vector3(0, 1.5, -3))
	check(world.get_world_3d().direct_space_state.intersect_ray(parameters).is_empty(), "main doorway remains traversable")
	parameters = PhysicsRayQueryParameters3D.create(Vector3(6, 2, 4), Vector3(6, -1, 4))
	var terrain_hit := world.get_world_3d().direct_space_state.intersect_ray(parameters)
	check(not terrain_hit.is_empty() and absf(terrain_hit.position.y - Dressing.ground_height(6, 4) - 0.003) < 0.02, "verge collision matches visible terrain height")
	world.player.position = Vector3(6, 1, 4)
	world.player.velocity = Vector3.ZERO
	world.player.reset_physics_interpolation()
	for i in 90:
		await physics_frame
	check(world.player.is_on_floor() and absf(world.player.position.y - Dressing.ground_height(6, 4) - 0.003) < 0.05, "character physically settles on raised verge without falling through")
	world.player.position = world.player.spawn_point
	world.player.reset_physics_interpolation()
	check(is_zero_approx(Dressing.ground_height(0, 5)) and is_zero_approx(Dressing.ground_height(0, -6)), "road and chapel retain original flat traversable height")
	parameters = PhysicsRayQueryParameters3D.create(Vector3(19, 1, 0), Vector3(22, 1, 0))
	check(not world.get_world_3d().direct_space_state.intersect_ray(parameters).is_empty(), "lower perimeter visuals retain the original 1.2m safety collision")
	var flames := get_nodes_in_group("art_flames")
	check(flames.size() == 4 and flames[0].sprite.hframes == 8 and flames[0].sprite.alpha_cut == SpriteBase3D.ALPHA_CUT_DISCARD, "pixel flame atlas is independent and uses sharp alpha cutout")
	world.set_art_animation(false)
	check(flames[0].sprite.frame == 3 and not flames[0].animation_enabled, "capture freeze keeps a deterministic flame frame")
	var environmental_meshes := world.find_children("*", "MeshInstance3D", true, false)
	check(environmental_meshes.size() < 50, "static draw mesh budget remains bounded")
	var normals_ok := true
	for instance in environmental_meshes:
		for surface in instance.mesh.get_surface_count():
			var normals: PackedVector3Array = instance.mesh.surface_get_arrays(surface)[Mesh.ARRAY_NORMAL]
			for normal in normals:
				normals_ok = normals_ok and normal.length_squared() > 0.5 and normal.length_squared() < 1.5
	check(normals_ok, "all art faces retain valid nonzero unit normals")
	var formats_ok := true
	for kind in ["granite", "wood", "earth", "grass", "steel"]:
		var texture: Texture2D = load("res://assets/textures/%s.png" % kind)
		formats_ok = formats_ok and texture.get_size() == Vector2(64, 64)
	check(formats_ok, "required source textures are loadable 64x64 resources")
	for name in ["chapel_portal", "pine", "knight_visual", "old_tree", "shrub"]:
		var asset: PackedScene = load("res://assets/models/%s.scn" % name)
		var instance := asset.instantiate()
		check(not instance.find_children("*", "MeshInstance3D", true, false).is_empty(), "saved module %s instantiates with meshes" % name)
		instance.free()
	print("RESULT: ", failures, " failures")
	quit(1 if failures else 0)
