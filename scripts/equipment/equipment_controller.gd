extends Node

## Hot-swappable visual equipment. One shared skeleton; no actor rebuild.
signal equipment_changed(slot: StringName, item_id: StringName)
const SLOTS: Array[StringName] = [&"head", &"body", &"hands", &"legs", &"feet", &"back", &"main_hand", &"off_hand"]
const ITEMS: Array[Resource] = [
	preload("res://assets/equipment/study_helmet.tres"),
	preload("res://assets/equipment/study_chest.tres"),
	preload("res://assets/equipment/study_sword.tres"),
	preload("res://assets/equipment/study_shield.tres")]
var catalog: Dictionary = {}
var equipped: Dictionary = {}
var instances: Dictionary = {}
var regions: Dictionary = {}
var skeleton: Skeleton3D
var visual: Node3D

func initialize(owner_visual: Node3D, shared_skeleton: Skeleton3D) -> void:
	visual = owner_visual
	skeleton = shared_skeleton
	for item in ITEMS:
		catalog[item.item_id] = item
	for mesh in visual.find_children("*", "MeshInstance3D", true, false):
		var region: StringName = StringName(String(mesh.name).split("__")[0])
		if not regions.has(region):
			regions[region] = []
		regions[region].append(mesh)
	_refresh_visibility()

func get_equipped(slot: StringName) -> StringName:
	return equipped.get(slot, &"")

func equip(item_id: StringName) -> Error:
	var item: Resource = catalog.get(item_id)
	if item == null or item.model == null or not SLOTS.has(StringName(item.slot)):
		return ERR_INVALID_PARAMETER
	var slot := StringName(item.slot)
	if get_equipped(slot) == item_id:
		return OK
	# Validate and construct FIRST. A rejected replacement must keep old gear.
	var instance: Node = item.model.instantiate()
	var source := instance as Node3D
	if source == null:
		instance.free()
		return ERR_INVALID_DATA
	visual.add_child(source)
	source.visible = false
	var mounted: Node3D
	if item.mount_type == "skin":
		mounted = _mount_skin(source)
	elif item.mount_type == "bone":
		var bone_index := skeleton.find_bone(item.attachment_bone)
		if bone_index >= 0:
			var socket := BoneAttachment3D.new()
			socket.name = String(slot) + "Socket"
			socket.bone_name = item.attachment_bone
			skeleton.add_child(socket)
			source.reparent(socket, false)
			# Rigid assets are exported in the SAME model rest space as the body.
			# Convert rest-space grip to bone-local once, then follow animation.
			source.transform = skeleton.get_bone_global_rest(bone_index).affine_inverse() * item.offset
			source.visible = true
			mounted = socket
	if mounted == null:
		source.free()
		return ERR_INVALID_DATA
	if item.mount_type == "skin":
		mounted.transform = item.offset
		source.free()
	if instances.has(slot):
		instances[slot].free()
	instances[slot] = mounted
	equipped[slot] = item_id
	visual.materials.apply(mounted)
	_refresh_visibility()
	equipment_changed.emit(slot, item_id)
	return OK

func unequip(slot: StringName) -> Error:
	if not SLOTS.has(slot):
		return ERR_INVALID_PARAMETER
	if not equipped.has(slot):
		return OK
	instances[slot].free()
	instances.erase(slot)
	equipped.erase(slot)
	_refresh_visibility()
	equipment_changed.emit(slot, &"")
	return OK

func clear() -> void:
	for slot in equipped.keys():
		unequip(slot)

func _refresh_visibility() -> void:
	# Union of coverage masks: taking off one item must not reveal a region
	# still covered by another. Under-cloth anatomical torso is always hidden.
	var hidden: Array[StringName] = [&"body_under_cloth"]
	for id in equipped.values():
		for region in catalog[id].hidden_regions:
			if not hidden.has(region):
				hidden.append(region)
	for region in regions:
		for mesh in regions[region]:
			mesh.visible = not hidden.has(region)

func _mount_skin(source: Node3D) -> Node3D:
	var source_skeleton := source.find_child("Skeleton3D", true, false) as Skeleton3D
	if source_skeleton == null:
		return null
	if not source_skeleton.global_transform.is_equal_approx(skeleton.global_transform):
		return null
	# Validate skeleton compatibility by NAME + global rest, never by index.
	for i in source_skeleton.get_bone_count():
		var target := skeleton.find_bone(source_skeleton.get_bone_name(i))
		if target < 0 or not source_skeleton.get_bone_global_rest(i).is_equal_approx(skeleton.get_bone_global_rest(target)):
			return null
	var meshes := source.find_children("*", "MeshInstance3D", true, false)
	if meshes.is_empty():
		return null
	# Validate all binds before allocating a mount or changing current gear.
	for mesh in meshes:
		if mesh.skin == null:
			return null
		for i in mesh.skin.get_bind_count():
			var name: StringName = mesh.skin.get_bind_name(i)
			if name == &"":
				var index: int = mesh.skin.get_bind_bone(i)
				if index < 0 or index >= source_skeleton.get_bone_count():
					return null
				name = source_skeleton.get_bone_name(index)
			if skeleton.find_bone(name) < 0:
				return null
	var mount := Node3D.new()
	mount.name = "SkinnedEquipment"
	skeleton.add_child(mount)
	for original in meshes:
		var skin := Skin.new()
		for i in original.skin.get_bind_count():
			var name: StringName = original.skin.get_bind_name(i)
			if name == &"":
				name = source_skeleton.get_bone_name(original.skin.get_bind_bone(i))
			skin.add_named_bind(name, original.skin.get_bind_pose(i))
		var mesh := MeshInstance3D.new()
		mesh.name = original.name
		mesh.mesh = original.mesh
		mesh.skin = skin
		mount.add_child(mesh)
		mesh.global_transform = original.global_transform
		mesh.skeleton = mesh.get_path_to(skeleton)
	return mount
