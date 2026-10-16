# 按用户多视图制作的 Blender 冒险者

本轮以用户提供的冒险者设定图为参考，使用 Blender 4.5.9 LTS 建模、UV、蒙皮并导出GLB。模型与工作贴图在项目内制作；设定图来自用户，不宣称是项目原创设定。当前仍是**可编辑模型候选**，面部/手部、布褶和绘制细腻程度尚未达到参考图。

## 原生Blender文件

打开 `assets/characters/wayfarer/source/blender/wayfarer.blend`。默认显示无装备人物，已有32骨和idle/walk/run/两段转向Action。

- `EDITABLE_SURFACES`：150个未合并编辑曲面，默认隐藏，手工接续时打开；先隐藏同位置的导出合并网格，避免双层重叠。
- `TEST_EQUIPMENT_optional`：四件原有测试装备，默认关闭，不属于初始外观。
- `REVIEW_STUDIO_not_exported`：灯光、地面和Review_Front / Side / Back / ThreeQuarter相机。
- `USER_REFERENCE_not_exported`：用户参考图，使用相对路径，需保留 `source/reference` 目录。参考图不是渲染结果，也不作为游戏纹理。

摄影棚和参考图在游戏GLB导出后加入，资源检查禁止这些物件进入GLB。手工编辑建议另存源文件并提交检查点；build_wayfarer.py会重新生成本候选，不能覆盖未保存的手工成果。

## 实际渲染

| Blender源文件实际渲染 | |
| --- | --- |
| [正面](blender_front.png) | [侧面](blender_side.png) |
| [背面](blender_back.png) | [三分之四](blender_threequarter.png) |

这些图来自Blender Cycles，不是AI概念图。灯光与游戏不同，不拿它们冒充Godot实际效果。

| 相同Godot机位 | 修改前2d69e80 | 当前候选 |
| --- | --- | --- |
| 原生近景 | [before](before_base_front_native.png) | [after](../wayfarer/base_front_native.png) |
| 640近景 | [before](before_base_front_640.png) | [after](../wayfarer/base_front_640.png) |
| 正常游戏距离 | [before](before_base_gameplay_640.png) | [after](../wayfarer/base_gameplay_640.png) |
| 森林环境 | [before](before_base_forest_context.png) | [after](../wayfarer/base_forest_context.png) |
| 跑步四帧 | [before](before_base_run.png) | [after](../wayfarer/base_run.png) |

[Godot正面rest](after_ortho_front.png)、[侧面rest](after_ortho_side.png)、[面部](after_portrait_native.png)。游戏内打开 `scenes/visual_lab/character_equipment_lab.tscn` 按F6/运行当前场景；F5仍是旧教堂。

## 实际修改及差距

完成卷袖/露出前臂与皮护腕、短开叉衣摆、棕红围巾、腰扣/皮包缝线、宽松裤腿和靴扣/鞋带；连续头皮上增加有厚度的弯曲发束。参考轮廓用于本轮造型，不复刻图中的二维绘制笔触。靴带已改为按实际鞋面曲面定位，鞋底降低以改善接地。

基础角色仍空手无盔甲。32骨rest逐矩阵保持一致；四件原有装备、碰撞、相机、输入与像素架构不变。没有新增玩法或地图内容。

原生资产约138,308三角形，是研究候选，并未完成生产拓扑/LOD。脸、耳、手掌/手指连接、肩袖和自然布褶仍需人工角色美术精修；发型体积和手绘材质与参考图仍有距离。程序步态不是手工精修动作，无坡地IK或布料模拟；不能声明全姿态无穿插或正式人物美术完成。

执行结果见[验证记录](../VALIDATION.md)。
