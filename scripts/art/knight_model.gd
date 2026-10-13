extends RefCounted

const Geo = preload("res://scripts/world/geometry.gd")
const Kit = preload("res://scripts/art/ruins_kit.gd")
const Meshes = preload("res://scripts/art/art_meshes.gd")

# Art-only hierarchy. Limb pivots keep the existing movement animation contract.
static func build(visual: Node3D, steel: Material, dark: Material, cloth: Material, trim: Material) -> Dictionary:
	var torso := Node3D.new()
	torso.name = "ArmourAndCape"
	visual.add_child(torso)
	Kit.piece(torso, Vector3.ZERO, Meshes.profile([Vector3(0.22, 0.88, 0.16), Vector3(0.29, 1.1, 0.21), Vector3(0.32, 1.35, 0.23), Vector3(0.24, 1.49, 0.18)], 8), steel)
	Kit.piece(torso, Vector3.ZERO, Meshes.profile([Vector3(0.31, 0.79, 0.2), Vector3(0.26, 1.04, 0.16)], 8), dark)
	Kit.block(torso, Vector3(0, 0.98, -0.185), Vector3(0.43, 0.07, 0.08), trim)
	for side in [-1, 1]:
		var tasset := Kit.block(torso, Vector3(side * 0.2, 0.86, -0.16), Vector3(0.2, 0.28, 0.055), steel)
		tasset.rotation.z = side * 0.13
		Kit.block(torso, Vector3(side * 0.2, 1.33, -0.19), Vector3(0.035, 0.055, 0.035), trim)
	Kit.piece(torso, Vector3.ZERO, Meshes.profile([Vector3(0.18, 1.43, 0.15), Vector3(0.18, 1.59, 0.15)], 8), dark)
	Kit.piece(torso, Vector3.ZERO, Meshes.profile([Vector3(0.18, 1.57, 0.17), Vector3(0.23, 1.72, 0.22), Vector3(0.21, 1.86, 0.19), Vector3(0.12, 1.93, 0.12)], 8), steel)
	Kit.block(torso, Vector3(0, 1.73, -0.204), Vector3(0.32, 0.045, 0.022), dark)
	Kit.block(torso, Vector3(0, 1.73, -0.222), Vector3(0.025, 0.16, 0.035), trim)
	for side in [-1, 1]:
		Kit.block(torso, Vector3(side * 0.09, 1.62, -0.185), Vector3(0.055, 0.065, 0.025), dark)
	Kit.piece(torso, Vector3(0, 1.92, 0.02), Meshes.profile([Vector3(0.035, 0, 0.13), Vector3(0.025, 0.17, 0.1), Vector3(0.01, 0.24, 0.02)], 6), cloth)
	# Folded cloak with an uneven hem: three dimensional folds remain legible at 640p.
	var cloak := SurfaceTool.new()
	cloak.begin(Mesh.PRIMITIVE_TRIANGLES)
	var xs := [-0.3, -0.13, 0.06, 0.3]
	for i in 3:
		var a := Vector3(xs[i] * 0.75, 1.48, 0.24 + (i % 2) * 0.06)
		var b := Vector3(xs[i + 1] * 0.75, 1.48, 0.24 + ((i + 1) % 2) * 0.06)
		var c := Vector3(xs[i + 1], 0.46 + ((i + 1) % 2) * 0.09, 0.4 + ((i + 1) % 2) * 0.08)
		var d := Vector3(xs[i], 0.46 + (i % 2) * 0.09, 0.4 + (i % 2) * 0.08)
		for point in [a, c, b, a, d, c]:
			cloak.add_vertex(point)
	cloak.generate_normals()
	Kit.piece(torso, Vector3.ZERO, cloak.commit(), cloth)
	var limbs: Dictionary = {}
	for side in [-1, 1]:
		var leg := _pivot(visual, Vector3(side * 0.16, 0.83, 0), "LeftLeg" if side == -1 else "RightLeg")
		Kit.piece(leg, Vector3.ZERO, Meshes.profile([Vector3(0.09, -0.65, 0.11), Vector3(0.11, -0.3, 0.13), Vector3(0.12, 0, 0.12)], 6), dark)
		Kit.block(leg, Vector3(0, -0.33, -0.105), Vector3(0.22, 0.18, 0.1), steel)
		Kit.block(leg, Vector3(0, -0.52, -0.07), Vector3(0.16, 0.23, 0.1), steel)
		Kit.block(leg, Vector3(0, -0.72, -0.075), Vector3(0.22, 0.16, 0.34), dark)
		var arm := _pivot(visual, Vector3(side * 0.39, 1.43, 0), "LeftArm" if side == -1 else "RightArm")
		Kit.piece(arm, Vector3.ZERO, Meshes.profile([Vector3(0.1, -0.52, 0.1), Vector3(0.12, -0.1, 0.13), Vector3(0.19, 0.03, 0.2), Vector3(0.16, 0.13, 0.17)], 7), steel)
		Kit.block(arm, Vector3(0, -0.4, 0), Vector3(0.23, 0.08, 0.24), trim)
		Kit.block(arm, Vector3(0, -0.51, -0.015), Vector3(0.2, 0.15, 0.21), dark)
		limbs["left_leg" if side == -1 else "right_leg"] = leg
		limbs["left_arm" if side == -1 else "right_arm"] = arm
	var shield: Node3D = limbs.left_arm
	Kit.piece(shield, Vector3(-0.07, -0.3, -0.16), Meshes.profile([Vector3(0.018, -0.5, 0.035), Vector3(0.25, -0.1, 0.05), Vector3(0.28, 0.35, 0.05), Vector3(0.2, 0.42, 0.04)], 4), trim)
	Kit.piece(shield, Vector3(-0.07, -0.3, -0.215), Meshes.profile([Vector3(0.014, -0.42, 0.012), Vector3(0.21, -0.1, 0.014), Vector3(0.235, 0.31, 0.014)], 4), cloth)
	var crest := Kit.block(shield, Vector3(-0.07, -0.24, -0.24), Vector3(0.1, 0.19, 0.022), steel)
	crest.rotation.z = PI / 4
	var sword: Node3D = limbs.right_arm
	Kit.piece(sword, Vector3(0, 0, -0.12), Meshes.profile([Vector3(0.005, -1.02, 0.005), Vector3(0.046, -0.84, 0.018), Vector3(0.046, -0.36, 0.018)], 4), steel)
	Kit.block(sword, Vector3(0, -0.35, -0.12), Vector3(0.28, 0.055, 0.08), trim)
	Kit.block(sword, Vector3(0, -0.24, -0.12), Vector3(0.06, 0.15, 0.055), dark)
	Kit.block(sword, Vector3(0, -0.14, -0.12), Vector3(0.09, 0.06, 0.08), trim)
	Kit.batch_static(torso)
	for limb in limbs.values():
		Kit.batch_static(limb)
	return limbs

static func _pivot(parent: Node3D, at: Vector3, title: String) -> Node3D:
	var node := Node3D.new()
	node.name = title
	parent.add_child(node)
	node.position = at
	return node
