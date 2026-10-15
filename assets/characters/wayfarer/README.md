# Wayfarer：布衣人物候选 / 装备外观原型

当前状态：可运行、可编辑的原创人物候选，**不是正式人物美术完成**。初始仅布衣、长裤、软鞋，没有金属护甲和手持物。未读取旧骑士网格、未使用Duel Corp或第三方资源，也没有本轮AI图像或高模烘焙。

本次按用户提供的冒险者图修正人体关系，约七头身；加宽头颅/下颌、收拢手臂，重塑连续肩袖/裤裆，缩短旧裙状衣摆并重做腿形/软鞋。未复制参考服饰，仍无初始装备。实测头长0.255m、头宽约0.183m；头顶/髋/膝/腕等设计标记在manifest，实际源审计在source_audit。原生及像素同镜头比较见[比例审阅](../../../docs/proportions/README.md)。

## 资源与职责

- `wayfarer.glb`：32骨、idle/walk/run/turn_left/turn_right五段in-place动作、13个可见性区域。当前96,992三角形/52,883导出顶点（包含默认隐藏的衣内躯干）；三角形数不代表美术达标。
- `equipment/helmet.glb` / `chest.glb`：同骨名/rest的独立蒙皮模型，6,032 / 7,928三角形。
- `equipment/sword.glb` / `shield.glb`：2,724 / 4,348三角形，刚性模型，导出坐标与人物rest空间一致；运行时由手部rest逆矩阵转换到BoneAttachment3D局部空间。
- `textures`：八套128²原创程序绘制像素色板PNG。材质粗糙度/金属度为设计常量，无Normal烘焙。Godot使用外部PNG的真实mipmap与最近邻；Blender源同时打包图。
- `source/blender/wayfarer.blend`：32骨、五个Fake User Action、74个未合并编辑曲面与按遮挡/材质合并的导出网格。源肩袖是共享顶点整体，只在导出时分离遮挡区；裤腰到双腿通过裤裆桥连接。目录`.gdignore`防止Godot自动导入原生文件；游戏仅加载GLB。
- `source/build_manifest.json` / `source_audit.json`：设计参数、分区、骨架rest和独立重开检查。`TailoredUV`为显式局部UV；四肢/小件有意复用，非无重叠烘焙UV。手工细化前应整理真正材质岛和纹素密度。

## 操作与扩展

运行 `scenes/visual_lab/character_equipment_lab.tscn`：默认空装备。1头盔、2胸甲、3剑、4盾，重复卸下；0全卸；P正常/待机/走/跑预览；L灯光。Esc释放后可点击高清界面，点击中央游戏画面重新捕获。原WASD/Shift/鼠标/滚轮不变。

`assets/equipment/*.tres` 使用 `VisualEquipmentItem`，字段包括item_id、slot、PackedScene、mount_type、attachment_bone、hidden_regions和offset。`scripts/equipment/equipment_controller.gd` 提供equip(id)、unequip(slot)、get_equipped(slot)、clear和equipment_changed信号。八个槽位是视觉接口，不包含背包、属性、掉落或攻击。

Godot接口依据：[Skin命名绑定](https://docs.godotengine.org/en/stable/classes/class_skin.html)、[BoneAttachment3D跟随骨骼](https://docs.godotengine.org/en/stable/classes/class_boneattachment3d.html)。本项目额外验证rest兼容并保留源inverse bind，不直接沿用不同GLB的骨骼索引。

添加兼容盔甲：在同一rest骨架上制作并保留蒙皮，单独导出GLB，在数据里指定skin及遮挡区域。运行时逐骨名/rest校验、按命名绑定重建Skin，再移除源骨架；不接受无蒙皮或不同rest。挂点道具使用bone模式；offset是美术坐标微调，先检查动画中的握持与离地余量。基础外观可见性采用全部装备遮挡并集，衣内躯干永久隐藏。卸下不会销毁/重建基础人物。

## 重做与人工接续

先保存手工编辑并创建Git检查点；生成器会覆盖本候选的GLB、PNG、源文件和manifest，默认拒绝覆盖。Blender未安装到系统，当前用已校验官方4.5.9 LTS临时只读运行。`human_surfaces.py`管理人体/衣物曲面，`build_wayfarer.py`管理骨架、动作、装备、导出；调整比例必须同步rest与腿部IK，不能在运行时缩放骨骼。

```sh
Blender --background --factory-startup --python-exit-code 1 --python tools/wayfarer/build_wayfarer.py -- --replace-generated
Blender --background --factory-startup --python-exit-code 1 --python tools/wayfarer/audit_source.py
Godot --headless --path . --editor --import
python3 tools/wayfarer/configure_imports.py
Godot --headless --path . --editor --import
python3 tests/wayfarer_asset_test.py
Godot --path . --script tests/equipment_test.gd
Godot --path . --script tools/wayfarer/capture_equipment.gd
Godot --path . --script tools/wayfarer/capture_proportions.gd
```

configure_imports仅改本候选sidecar，不改旧资源。截图会覆盖docs/wayfarer，本轮稳定图片先保存；图形测试不能headless。测试包括模拟输入，不等于真人长期试玩。

本轮已经以实图迭代发际/头皮、裤腰/衣摆和胸甲/下摆衔接；仍需人工精修面部、耳/手/肩/髋拓扑与服装质感。动作是新骨架上的程序周期，并非精修手工动画或mocap；原地跑姿不代替实际移动，平地测试不证明坡地IK、全姿态无穿插或完整脚指抓握。未来披风只有back槽位，未制作披风模型或布料模拟。应由角色美术师在保留曲面基础上雕刻/重拓扑/绘制，再按640/960/原生与真实动作审核，勿继续堆小装甲片冒充人物质量提升。
