# 角色与装备图集接入

[布衣同机位对照](comparison_base.png) · [装备同机位对照](comparison_equipped.png) · [基础人物](after_base_front_640.png) · [纹章装备](after_equipped_threequarter_640.png) · [地图运动视频](../locomotion_review/forest_movement.mp4)

两张源图均为用户本轮明确提供、授权用于项目的此前生成图。原文件和SHA256在`assets/characters/reference_silhouette/source/art/`；没有新增外部素材，也没有把设计图当成运行截图。

| 原图区域 | 实际用途 |
| --- | --- |
| 米色布料及红色织边 | 上衣、卷袖与分开的衣摆材质，花边只在下摆 |
| 暗红布料 | 围巾及垂布 |
| 棕色皮革与缝线 | 腰带、腰包、护腕、靴子和剑柄 |
| 蓝钢胸甲正面/背面 | 胸甲前后独立UV区，正面居中金色纹章 |
| 头盔、普通钢面、金色金属 | 头盔、盾边、护颈、腰扣 |
| 青蓝木板与金色纹章 | 盾面；原浅色条带也使用连续平面投影，避免盖住徽记 |
| 拉丝刃面 | 长剑金属部分 |

像素版本提取11个用途图块，各128×128；较细版本提供低对比粗糙度变化，共22张PNG。没有新增法线图；这些粗糙度是绘制图像的值域研究，不是测量PBR或高模烘焙。最近邻+mipmap与原像素管线统一，不平铺整张图集。

Blender只修改材质与UV，脚本核对顶点位置摘要、32骨rest和九段动作不变。原UV保存在`PrePatternUV`，当前用途映射在`TailoredUV`；未合并编辑源和原生四相机保留，原生初始无装备。新图案以基础人物及四件分离GLB接入；游戏运行穿卸不重建角色、骨骼或动画树。

12张before和12张after均为相同灯光、正面/3/4/背面、像素640与原生条件下的真实Godot截图。对照拼图仅裁相同屏幕区域并加标签，没有重绘角色。模型造型、皮肤/头发及人工动画润色仍未完成正式美术验收；图案成功贴上不代表主角模型质量达标。

制作入口：`prepare_equipment_patterns.py`生成工作贴图；`apply_equipment_patterns.py`在Blender保存源并导出五份GLB；`configure_imports.py --silhouette-study`仅配置本候选导入。所有覆盖前保存检查点。`tests/pattern_asset_test.py`检查来源摘要、实际GLB材质、UV边距和mipmap；图形equipment、locomotion及locomotion_valley测试检查热切换、F3、控制与动作。
