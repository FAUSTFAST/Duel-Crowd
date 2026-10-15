# 基础人物比例修订 · 实图审阅

用户提供的冒险者插画作为头身、肩腰和四肢关系参考，不复制图中的装备；默认仍穿普通布衣、长裤、软鞋，双手为空。旧版比例基线是Git检查点 `f3165be`。

| 实际Godot镜头 | 修改前布衣人物 | 当前比例候选 |
| --- | --- | --- |
| 原生3.8m近景 | [前](before_base_front_native.png) | [后](../wayfarer/base_front_native.png) |
| 640×360近景 | [前](before_base_front_640.png) | [后](../wayfarer/base_front_640.png) |
| 640×360背面 | [前](before_base_rear_640.png) | [后](../wayfarer/base_rear_640.png) |
| 640×360、8m游戏距离 | [前](before_base_gameplay_640.png) | [后](../wayfarer/base_gameplay_640.png) |
| 同一森林环境 | [前](before_base_forest_context.png) | [后](../wayfarer/base_forest_context.png) |
| 行走/奔跑姿态 | [走](before_base_walk.png) / [跑](before_base_run.png) | [走](../wayfarer/base_walk.png) / [跑](../wayfarer/base_run.png) |

位置、灯光、相机参数和显示条件由同一个capture_equipment工具固定；动画本身随新骨架重做，不声称每个顶点姿态相同。截图是实际Godot图形输出，没有重绘人物或修饰画面。

新增[正面](after_ortho_front.png)、[侧面](after_ortho_side.png)、[四分之三面](after_ortho_three_quarter.png)及[头部](after_portrait_native.png)审阅图；正交相机消除透视缩短，但不能替代原游戏镜头。

重做头颅/下颌与五官贴面、放松肩臂、连续肩袖、完整裤裆和腿部体积；缩短并收紧旧裙状衣摆，调整鞋型，换为低饱和棕/炭灰/近黑配色。头长0.255m、头宽约0.183m，解剖头顶约七头身；数值来自保存源曲面，不是对单张参考图的精确测量。四件独立装备重做rest适配，初始没有任何装备。

本轮修复了实图发现的裤腰穿衣、外张手臂、圆管发束、低垂/上翘肩线；保留74个可编辑曲面与原控制。角色仍是**比例修正版美术候选**：脸部表情、耳/手解剖、衣料绘制和动作节奏尚未达到参考插画的精细度。连续网格、UV、骨架与测试通过不能替代美术审核；坡地IK和任意装备姿态穿插未完成。

制作：临时只读Blender4.5.9 LTS导出；Godot4.7.2 Compatibility实际渲染。`capture_proportions.gd`只改审阅镜头，不动生产相机；截图应先备份稳定基线。测试及性能记录见[VALIDATION](../VALIDATION.md)。
