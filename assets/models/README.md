# 原创 Godot 模型库

chapel_portal.scn、pine.scn、knight_visual.scn、old_tree.scn、shrub.scn 是源美术模块的可实例化预览资源，可在 Godot 打开检查。圣堂模块原点使用测试地图坐标，入口位于 z=-2；树木在原点；骑士朝 -Z，四肢节点可独立旋转。

来源：scripts/art/art_meshes.gd、ruins_kit.gd、forest_dressing.gd、knight_model.gd。游戏运行时使用相同源模块构建与合批；预览资源不是控制器，不包含骨骼、战斗或移动逻辑。运行 tools/bake_art_library.gd 可重新烘焙模型库，会覆盖这些生成预览资源，先保留 Git 检查点。

当前采用 Godot 原生网格和材质，不是 Blender GLB。世界空间三平面投射属于 Godot 材质行为，后续导出 GLB 必须增加明确 UV 或烘焙，不能假定 glTF 会保留该效果。Blender 尚未安装，本轮没有宣称 Blender 或 GLB 工作流已完成。
