# 西式奇幻旅人：历史画面审阅（2026-10-16）

此页记录2d69e80版本；docs/wayfarer链接随后会随当前候选更新。该版正侧/面部after_*留在本目录，新轮次基线与当前结果见[最新参考图建模记录](../adventurer_reference/README.md)。

状态：**可运行美术候选，未达到正式角色验收。** 服饰已经从现代短衫/软鞋转向系带粗布长衫、分叉下摆、领巾、腰带小袋与皮靴；头面改用露额短发和较明确的下颌/鼻部。初始无盔甲、武器、盾牌。工程测试不能代替用户对主角感、人体自然度与画风的审阅。

## 同机位比较

所有图片来自 Godot 4.7.2 / Apple M1 Compatibility 实际渲染，没有绘画替代、滤镜修图或AI合成。`before_*`固定为修改前5ca2f4d提交的真实截图。场景、灯光和镜头配置相同，人物设计及待机姿态有所变化；并非同一骨骼姿态逐像素对照。

| 条件 | 旧版 | 新旅人候选 |
| --- | --- | --- |
| 原生正面，3.8m | [before](before_base_front_native.png) | [after](../wayfarer/base_front_native.png) |
| 640正面，3.8m | [before](before_base_front_640.png) | [after](../wayfarer/base_front_640.png) |
| 640游戏距离，8m | [before](before_base_gameplay_640.png) | [after](../wayfarer/base_gameplay_640.png) |
| 640背面 | [before](before_base_rear_640.png) | [after](../wayfarer/base_rear_640.png) |
| 森林环境 | [before](before_base_forest_context.png) | [after](../wayfarer/base_forest_context.png) |
| 奔跑四帧 | [before](before_base_run.png) | [after](../wayfarer/base_run.png) |
| 正交正面/rest | [before](before_ortho_front.png) | [after](after_ortho_front.png) |
| 面部近景/rest | [before](before_portrait_native.png) | [after](after_portrait_native.png) |

[侧面](after_ortho_side.png)、[三分之四](after_ortho_three_quarter.png)、[行走四帧](../wayfarer/base_walk.png)、[实际森林奔跑](../wayfarer/forest_running.png)、[四件测试装备](../wayfarer/equipped_front_640.png)、[卸下恢复](../wayfarer/unequipped_front_640.png)。正交审阅重置骨骼rest，不能当作待机站姿；游戏镜头保留真实idle/走跑。

## 这次改动与尚存差距

- 重新制作分叉长衫、皮靴、布料领巾、皮带尾与小袋，使用曲面和显式UV；不是给旧布衣追加金属装饰。肩袖/裤裆的连续基础拓扑保留。
- 十套128px原创图，面部增加局部肤色/眼窝/胡茬色差，布料和皮革使用低对比织纹/接缝。没有新外部素材、AI图像、法线烘焙。
- 32骨rest全部不变，五段Action接口、控制器、碰撞与相机保持；待机重心轻微偏移、脚步错位、肘部放松。长衣摆按左右大腿蒙皮，靴筒跟随小腿，胸甲穿戴隐藏领巾/腰带，卸下恢复。
- 第一轮实际截图中的宽肩巾像硬甲、胡茬壳像面罩，因此未保留；最终采用垂挂领巾和面部UV色差。
- **尚未完成高质量人物雕刻。** 近景脸/耳/手仍简化，发际/布料张力褶皱与部分肩颈形体需要人工角色美术继续制作；背部接缝和肩袖凹褶在低分辨率下仍显粗糙。UV密度尚未逐岛统一，无坡地IK/布料模拟；程序周期不等于自然手工动画，不能保证所有混合姿态无穿插。

当前约12万三角形是可编辑研究资产，不能以面数证明精细程度；正式生产还需要拓扑/LOD预算。先审核当前方向，再从 `assets/characters/wayfarer/source/blender/wayfarer.blend` 的 `EDITABLE_SURFACES` 手工精修，另存人工源，避免被生成器覆盖。

## 打开查看

在Godot双击 `scenes/visual_lab/character_equipment_lab.tscn`，点击停止按钮右侧的**运行当前场景（场记板播放）**，或F6 / Fn+F6。普通三角形/F5仍是旧教堂。

WASD移动、Shift跑步、移动鼠标转视角、滚轮缩放、Esc释放。P依次预览待机/走/跑，L切换灯光，F1像素/原生，F2三档分辨率。默认空装备；1–4是原有四件测试装备，0卸下全部。没有新增背包/战斗玩法。

具体执行结果和性能范围见[验证记录](../VALIDATION.md)。
