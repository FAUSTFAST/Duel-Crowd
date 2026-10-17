# 灰誓 / Ashen Oath — Duel-Crowd

## 当前：以设计图为唯一主要参考的轮廓还原实验

独立候选：`scenes/visual_lab/reference_silhouette.tscn`（运行当前场景 / F6）。Blender源文件：`assets/characters/reference_silhouette/source/blender/wayfarer.blend`。原角色、原场景保留。

[三视图对照页](docs/silhouette_review/comparison.html) · [旧版正面](docs/silhouette_review/old_front.png) · [新候选正面](docs/silhouette_review/new_front.png) · [逐项对照及打开说明](docs/silhouette_review/README.md)。当前为**轮廓待审核版**，没有擅自推进到细节完善版。脸部神态、发束和布褶仍未还原到设计图质量。

以下为上一阶段记录。

原创暗黑奇幻 3D 动作 RPG。当前路线：精细 3D 形体 + 装备用途 UV 图集 + 2D 像素元素 + 3D 光照 + 统一像素呈现。旧教堂、Forest Valley 与上一版骑士保留；新角色只在独立美术实验中验证。未使用 Duel Corp 素材；候选资产仍需人工美术精修。

## 新：布衣人物与模块化装备外观实验

本轮根据用户提供的冒险者多视图，在 **Blender 4.5.9 LTS** 制作卷袖布衣、露出前臂与皮护腕、较短开叉衣摆、围巾、黄铜腰扣/皮包和折边靴，头发改为分层发束。默认仍无盔甲、武器、盾牌，32骨rest和装备接口保持。

**Blender源文件：** `assets/characters/wayfarer/source/blender/wayfarer.blend`。打开默认显示基础人物；测试装备放在隐藏的 `TEST_EQUIPMENT_optional` 集合。`EDITABLE_SURFACES` 保留150个可编辑曲面，四个Review相机和参考图用于审阅，不进入游戏GLB。

[Blender实际渲染](docs/adventurer_reference/blender_threequarter.png)、[正面](docs/adventurer_reference/blender_front.png)、[本轮对比与打开说明](docs/adventurer_reference/README.md)。模型和贴图在本项目制作，设定图来自用户，不宣称设定图由本项目原创。当前仍是**参考图指导的美术候选**，脸/手、细腻布褶和绘制质感尚未达到参考图质量。

打开 **`scenes/visual_lab/character_equipment_lab.tscn`**，双击场景后按 **F6 / 运行当前场景的场记板按钮**。普通三角形/F5仍是旧教堂；Forest Valley和Knight Art Atelier完全保留。

初始为粗布长衫、长裤、皮靴的原创成年旅人，没有金属护甲或手持物。兼容既有32骨、idle/walk/run及转向周期；身体、头发和衣物有独立遮挡分区。此角色属于**可编辑美术候选**，人物面部、手型与动作尚需人工精修，不能当作正式高质量角色完成。

| 操作 | 功能 |
| --- | --- |
| 1 / 2 / 3 / 4 | 穿戴/卸下头盔、胸甲、长剑、盾牌 |
| 0 | 卸下全部，恢复布衣和头发 |
| Esc 后点击右侧按钮 | 同样可以实时切换；界面点击不捕获鼠标 |
| 点击游戏中央 | 重新捕获鼠标 |
| P | 正常移动 → 待机 → 原地行走 → 原地跑步预览 |
| L | 中性/森林灯光比较 |

WASD、Shift、移动鼠标、滚轮、R及F1–F4/F6沿用原功能。装备切换不重载人物：盔甲按骨名重绑唯一Skeleton3D，武器/盾牌挂到手部BoneAttachment3D。数据资源在 `assets/equipment`；预留head/body/hands/legs/feet/back/main_hand/off_hand八槽，当前只制作四件。没有背包、属性、掉落或战斗系统。

同镜头Godot实图：[无装备](docs/wayfarer/base_front_640.png)、[穿戴四件](docs/wayfarer/equipped_front_640.png)、[卸下](docs/wayfarer/unequipped_front_640.png)、[旧骑士](docs/wayfarer/previous_knight_front_640.png)。
[默认游戏距离基础人物](docs/wayfarer/base_gameplay_640.png)、[装备后](docs/wayfarer/equipped_gameplay_640.png)、[高清按钮](docs/wayfarer/debug_ui.png)、[基础跑姿](docs/wayfarer/base_run.png)、[山谷临时外观检查](docs/wayfarer/base_forest_context.png)。截图工具只在运行内暂换山谷外观，不保存生产替换。

制作源、资源状态、扩展约定和重做流程见 [Wayfarer说明](assets/characters/wayfarer/README.md)，实际测试见 [验证记录](docs/VALIDATION.md)。

## 保留：独立骑士美术对比实验
打开 `scenes/visual_lab/knight_atelier.tscn`，双击进入场景后按 **F6 / 运行当前场景的场记板按钮**。F5 仍运行旧教堂；运行游戏后 F6 的含义是切换整数缩放。

```sh
Godot --path . scenes/visual_lab/knight_atelier.tscn
```

B 在原 Ashen Knight 与新 Thorn Warden 候选之间切换，位置、摄像机、碰撞和灯光不变；L 比较中性/森林灯光，0 返回正常可移动状态，1/2/3 预览待机/原地行走/原地奔跑。原有 WASD、Shift、鼠标、滚轮、Esc、R 及 F1–F4 继续有效。

新资产使用独立 Blender 曲面源文件、装甲/盾徽/刺绣专用 UV 图集与粗糙度图；复用本项目原有38骨/五段原创动作，不冒称新动作捕捉。另有透明裁切蕨叶贴图平面。**这是新路线的可运行美术候选，尚未达到正式角色验收标准，也没有替换山谷角色。**

| 同镜头实际运行图 | 原角色 | 新候选 |
| --- | --- | --- |
| 640×360 近景 | [old](docs/atelier/old_front_640.png) | [new](docs/atelier/new_front_640.png) |
| 原生近景 | [old](docs/atelier/old_front_native.png) | [new](docs/atelier/new_front_native.png) |
| 山谷环境 | [old](docs/atelier/old_forest_context.png) | [new](docs/atelier/new_forest_context.png) |

[动作采样](docs/atelier/new_run_poses.png)、[山谷实际奔跑](docs/atelier/new_forest_running.png)、[实验 UI](docs/atelier/lab_ui.png)。所有对比图来自 Godot；imagegen 输出仅用作材质草案和蕨叶素材。[制作/人工精修流程与资源状态](assets/characters/thorn_knight/README.md)，[实际测试记录](docs/VALIDATION.md)。

## 运行与操作
使用 **Godot 4.7.2** 导入 `project.godot`，按 F5 运行 `scenes/rendering/pixel_game.tscn`。WASD / 方向键移动，Shift 跑步，移动鼠标旋转摄像机，滚轮缩放，R 返回出生点。启动自动捕获鼠标；Esc 释放，点击游戏画面重新捕获；失焦释放，关闭窗口退出。

| 调试键 | 功能 |
| --- | --- |
| F1 | 像素渲染 / 原生分辨率对比 |
| F2 | 640×360 → 960×540 → 480×270 循环 |
| F3 | 开关原创纹理细节（保留当前光照） |
| F4 | 开关环境雾 |
| F6 | 整数倍 / 适应窗口缩放 |
| - / =（+ 所在键） | 环境光能量，每次增减 0.05 |

默认内部 **640×360**。在 1280×720 窗口中为精确 2 倍最近邻放大。480 档显示 960×540；960 档显示 960×540，余下空间留边。F6 可填满窗口中最大的 16:9 区域；非整数缩放会出现像素宽度不完全均匀的取舍。窗口小于内部分辨率时会等比缩小，无法保证每个内部像素都可见。UI 使用窗口分辨率，保持清晰。16:9 之外的窗口会留边，不拉伸 3D 画面。

## 独立森林山谷样板
在 Godot 打开 `scenes/visual_lab/forest_valley.tscn`，按 **F6 运行当前场景**；运行游戏后 F6 是整数/适应缩放开关。F5 仍启动旧教堂地图。也可以执行：
```sh
Godot --path . scenes/visual_lab/forest_valley.tscn
```
所有移动、鼠标、缩放和调试键位沿用上表。山谷内 F3 比较 Albedo / Normal / Roughness 与平色，透明叶片保留形状。默认 640×360，建议同时查看 960 档和 F1 原生图，以确认模型细节并非仅来自像素滤镜。

新世界、美术材料库和继承式骑士位于 `scripts/valley`；原运动逻辑与摄像机保留，角色增加可替换外观扩展点。`pixel_renderer.gd` 提供可配置的世界场景与标题，保留唯一输入路由。原9份 Blender研究GLB与源文件详见 [山谷资产说明](assets/valley/README.md)，本轮独立骑士资源见下文。

实际截图：
- [640 默认](docs/valley/valley_640.png)、[960](docs/valley/valley_960.png)、[原生](docs/valley/valley_native.png)。
- [相同镜头平色材质](docs/valley/valley_flat_same_camera.png)、[路径](docs/valley/valley_path.png)、[骑士](docs/valley/valley_knight.png)、[移动采样](docs/valley/valley_motion.png)。
- 旧地图与新山谷是不同场景，不能当作同角度前后对比。以上截图记录山谷初版；当前骑士重制对比见下文。

## 骑士重制：山谷可操作角色
山谷已接入原创 **38 骨蒙皮 GLB**，约 2m，分区胸甲、曲面肩甲/活动甲片、开口面甲、手甲、护膝/胫甲、折褶披风、曲面鸢盾及斜持佩剑。五套 128px 金属/黄铜/布料/皮革/锁子甲 Albedo、浅细节 Normal、Roughness 使用局部 UV 和最近邻 mipmap；不是高模烘焙或第三方素材。约 26,765 三角形，87+ 分件合并为五个蒙皮材质表面。

`idle / walk / run / turn_left / turn_right` 五段 Blender 动作经 GLB 导入，AnimationTree 淡入淡出并按实际横向速度调整步频。低速换向有躯干/头部先导；移动由原控制器负责，无水平根运动。披风为六骨烘焙摆动，非实时布料。当前尚无坡地脚部 IK，坡面/任意转向的脚步和穿插仍需真人精修验收。

**打开 `scenes/visual_lab/forest_valley.tscn`，点击右上角“运行当前场景”的场记板播放图标（停止 ■ 右侧），或按 F6 / Mac 的 Fn+F6。普通三角形 ▶ / F5 仍运行旧教堂。** 键位不变。基础角色只增加外观构建/动画扩展点，运动、胶囊、摄像机与输入路由不变；教堂仍使用旧外观。

可替换资源：`scenes/characters/ashen_knight_visual.tscn`，在 `valley_knight.gd` 的 `visual_scene` 指定兼容外观组件。动画步频、混合时间在 `rigged_knight_visual.gd` 导出参数；制作源、约定与重做命令见 [骑士资产说明](assets/characters/ashen_knight/README.md)。重生成会覆盖本角色资源，先提交手工编辑。

真实同镜头对比：

| 镜头 | 旧骑士 | 新骑士 |
| --- | --- | --- |
| 正面近景 | [before_front](docs/knight/before_front.png) | [after_front](docs/knight/after_front.png) |
| 后方近景 | [before_rear](docs/knight/before_rear.png) | [after_rear](docs/knight/after_rear.png) |
| 默认游戏镜头 | [before_gameplay](docs/knight/before_gameplay.png) | [after_gameplay](docs/knight/after_gameplay.png) |

[960近景](docs/knight/after_front_960.png)、[原生近景](docs/knight/after_front_native.png)、[行走姿态](docs/knight/walk_poses.png)、[奔跑姿态](docs/knight/run_poses.png)、[真实移动奔跑](docs/knight/run_in_game.png)。参考用户本轮提供的 Duel Corp 实图研究肩腰比例、铠甲分层和像素可读性，未复制其设计、模型、贴图或 UI。新模型是可操作骨骼角色首版，尚不宣称达到商业手工角色质量。

## 模块
- `scenes/rendering/pixel_game.tscn` / `scripts/rendering/pixel_renderer.gd`：SubViewport、呈现比例、输入路由、高清 UI 与调试，独立于角色逻辑。
- `shaders/pixel_present.gdshader`：只采样纹素中心，无模糊、抖动或额外调色叠加。
- `scripts/rendering/pixel_materials.gd`：缓存原创确定性 64px 纹理，石材、路面、土壤、树皮、树冠、钢和布料；最近邻与 mipmap。
- `scenes/world/forest_ruins.tscn` / `scripts/world/`：保留原有布局的废墟、环境与几何工具。
- `scripts/characters/`、`scripts/camera/`：骑士控制与 SpringArm 摄像机。
- `scripts/art/`：倒角/棱面几何、尖拱圣堂、老树/灌木、起伏地形、骑士造型与静态合批；torch_flame.gd 独立管理火光动画。
- `assets/models/*.scn`：可直接打开的原创 Godot 模型库预览；游戏使用相同源模块构建。
- `assets/textures/*.png`：可编辑 64px 原创像素细节纹理与 256×32 火焰帧图；模型与纹理各自 README 说明生成流程。
- `tests/`、`tools/`、`docs/`：回归、截图工具与验收记录。

旧教堂环境通过世界空间三平面投射保持像素密度；旧骑士使用局部投射，新山谷骑士使用随蒙皮移动的局部UV。摄像机平滑与物理插值减少高帧率下的物理步进感，mipmap 减少远处纹理闪烁；透视旋转下仍有正常的像素边缘跳变，并非完全消除走样。

摄像机导出参数在 `scripts/camera/orbit_camera.gd`；渲染默认开关、分辨率索引与整数缩放可在主场景 Inspector 调整。调试调整仅作用于当前运行，不写入项目文件。

## 验证与截图
控制与渲染测试需要真实图形窗口；美术完整性测试可无头执行：
```
Godot --path . --script tests/valley_test.gd
Godot --path . --script tests/knight_animation_test.gd
python3 tests/knight_asset_test.py
Godot --path . --script tools/characters/capture_knight_review.gd
Godot --path . --script tools/valley/capture_valley.gd
Godot --path . --script tests/prototype_test.gd
Godot --path . --script tests/rendering_test.gd
Godot --headless --path . --script tests/art_integrity_test.gd
Godot --path . --script tools/capture_art_review.gd
Godot --path . --script tools/capture_preview.gd
Godot --path . --script tools/capture_flame_review.gd
```
本机可将 `Godot` 替换为 `/Users/mac/Downloads/Godot.app/Contents/MacOS/Godot`。测试包含输入事件注入，不等同于真人长时间试玩。截图保存在 docs：visual_before（修改前）、visual_pixel_640（默认）、visual_native（相同材质原生对比）、visual_pixel_480/960、visual_motion（移动采样）。详细结果见 `docs/VALIDATION.md`。

## 当前边界
已精修入口尖拱/破损上窗、道路不规则边沿、路侧起伏地形、十一组不对称灌木/草簇/落叶/碎石、三棵分叉老树与倒木，增强骑士肩甲/领甲/头盔/披风和盾徽。火把使用原创 8×32px 帧图、12fps 最近邻动画、透明裁切和轻微暖光变化，没有模糊后处理。地形网格同时生成碰撞，道路中心与教堂高度保持平坦；远处边界视觉降为石沿，但原 1.2m 安全碰撞保留。

旧地图仍使用原创 Godot 网格与原生 .scn 预览。新样板已实际使用临时、校验过的 Blender 4.5.9 LTS 制作 GLB，未安装到系统或改全局设置；环境仍是研究资产，山谷骑士现有真正骨骼与五段动画，尚需手工造型/UV/动作精修。外围仍较稀疏，尚未达到目标商业美术质量。没有新增战斗、敌人或装备玩法。Windows 导出、Retina 多种缩放和长时压力未验证。

## GitHub
用户指定仓库：https://github.com/FAUSTFAST/Duel-Crowd 。`main` 跟踪 `origin/main`。使用 `git push origin main` 同步，不强推，不创建新仓库，不改变仓库可见性。最新实际推送结果以验证记录和 Git 日志为准。

第三阶段同角度对比：docs/stage3_before_overview.png 与 stage3_after_overview.png；角色近景为 stage3_before_knight.png 与 stage3_after_knight.png。前图从稳定提交 8b6bedc 独立渲染，后图来自当前项目，两者内部 640×360、HUD 隐藏、摄像机与出生点一致。截图期间请让游戏窗口保持可见；等待渲染帧在不可绘制的窗口环境中可能延迟。新造型未改变控制键位或像素调试方式。

第四阶段同角度对比：`docs/stage4_before_overview.png` / `stage4_after_overview.png`，骑士为 `stage4_before_knight.png` / `stage4_after_knight.png`。before 在稳定版本 8ba2e2a 改动前实际捕获；after 保持相同摄像机与出生点，冻结火焰至帧3只用于比较。`stage4_flame_motion.png` 则是实际动画连续采样，不冻结。

美术可调项：`forest_dressing.gd` 的 ground_height / islands / 老树位置，`forest_ruins.gd` 的色板及环境光、火炬、雾参数，`torch_flame.gd` 的帧率、像素尺寸、光强变化幅度。控制与渲染管线继续独立，按键不变。纹理重生成会覆盖文件：先提交手工编辑，再运行 `tools/export_environment_textures.gd`（仅六类环境纹理与火焰图）。
