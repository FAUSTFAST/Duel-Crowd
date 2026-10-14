# 灰誓骑士 — 原创可操作骨骼角色首版

作者来源：本项目脚本在 Blender 4.5.9 LTS 中构建的原创截面/曲面网格、蒙皮骨架及关键帧。色板为冷灰钢、旧黄铜、深酒红织物、暗褐皮革；鸢盾“断日/誓刃”镶线原创。用户提供的游戏截图只用于比例和可读性参考；无第三方模型、动作、贴图或游戏专有资源。

`ashen_knight.glb` 是运行资源；`source/blender/ashen_knight.blend` 可恢复制作源，15张文件贴图全部打包，五个 Action 设置 Fake User 保留。`.gdignore` 仅阻止 Godot 自动调用全局 Blender。`source/build_manifest.json` 记录实际导出骨架、网格预算、动作步频及合并前分件名称。

身高约2m（头盔最高2.015m，待机有轻微屈膝），38骨：Root/Pelvis/Spine/Chest/Neck/Head、两侧大腿/胫骨/脚/趾、锁骨/上臂/前臂/手/五指、三列两节披风骨。腿使用二段长度固定的离线逆解生成支撑与摆腿轨迹；曲面甲片刚性绑定相应骨，内衬/披风有混合权重。五个合并蒙皮网格，**26,765 三角形 / 19,183 GLB 顶点**；切线与局部UV真实导出。合并仅限相同材质，不丢蒙皮权重。

| 动作 | 周期 | 设计移动速度 |
| --- | --- | --- |
| idle | 2.4s | 0 |
| walk | 17/30s | 3.2m/s |
| run | 0.6s | 5.8m/s |
| turn_left / turn_right | 19/30s | 0；低速换向躯干先导 |

全部为原地动作；水平位移由 CharacterBody3D 负责，AnimationTree 以实际速度调整时间倍率，行走/跑步切换同步相位并淡化。转身并非完整原地脚部踏转；快跑转弯保留步态。披风是烘焙骨骼摆动，非实时物理；尚无地形足部IK/手工动作捕捉/高模雕刻或法线烘焙。

五种材料各有 128×128 的 Albedo/Normal/Roughness。`paint_knight_materials.py` 绘制磨损、边线、铆钉、锻造纹、刺绣、缝线与锁子环；Normal 由绘制的浅高度细节计算，**不是高模烘焙**。Godot `knight_materials.gd` 只替换本角色材质，metallic 0.42，最近邻 + 真实mipmap，F3同时关闭本角色多通道细节。UV随身体移动，不投射世界坐标；小零件UV密度仍不完全一致，远镜下细纹自然衰减。

重做（仅本目录生成资源，先保存手工编辑到Git）：

```sh
python3 tools/characters/paint_knight_materials.py
Blender --background --factory-startup --python tools/characters/build_knight.py
Godot --headless --path . --editor --import
python3 tools/characters/configure_imports.py
Godot --headless --path . --editor --import
python3 tests/knight_asset_test.py
Godot --path . --script tests/knight_animation_test.gd
Godot --path . --script tools/characters/capture_knight_review.gd
```

贴图生成需要 Pillow/numpy；Blender 脚本只用 bpy/mathutils 和标准库。以上 CLI 名需换成本机路径，不自动安装软件。初次导入前已有 `.import` 策略可防止导出重复PNG。若手工模型更新顶点权重、UV或动画，请先提交并禁用生成器覆盖，不以旧生成脚本替代手工资产。

可替换外观封装在 `scenes/characters/ashen_knight_visual.tscn`；替换 `Model` GLB 时需提供上述五个动作及兼容骨架，外观组件提供 `materials / update_locomotion / set_animation_enabled`。不带移动、输入、摄像机或装备玩法。

实际对比与动作截图在 `docs/knight`。当前比四节点摆动占位更完整，但肩臂、手部抓握、布料碰撞、陡坡接地与材质分区仍需专业人工精修，不称最终商业成品。
