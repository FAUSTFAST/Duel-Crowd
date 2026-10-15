extends Resource
class_name VisualEquipmentItem

## Visual data only. No inventory, stats, combat or ownership rules here.
@export var item_id: StringName
@export var display_name: String
@export_enum("head", "body", "hands", "legs", "feet", "back", "main_hand", "off_hand") var slot: String = "head"
@export var model: PackedScene
@export_enum("skin", "bone") var mount_type: String = "skin"
@export var attachment_bone: StringName
@export var hidden_regions: Array[StringName] = []
@export var offset: Transform3D = Transform3D.IDENTITY
