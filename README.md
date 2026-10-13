# 灰誓 / Ashen Oath — Duel-Crowd
原创暗黑奇幻 3D 动作 RPG。第四阶段完成核心路侧地形、成簇植被、老树、废墟轮廓、骑士与像素火焰精修；所有代码、几何和纹理均原创，未使用 Duel Corp 素材。

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

纹理通过世界空间三平面投射保持环境像素密度；骑士使用局部空间投射，随模型移动。摄像机平滑与物理插值减少高帧率下的物理步进感，mipmap 减少远处纹理闪烁；透视旋转下仍有正常的像素边缘跳变，并非完全消除走样。

摄像机导出参数在 `scripts/camera/orbit_camera.gd`；渲染默认开关、分辨率索引与整数缩放可在主场景 Inspector 调整。调试调整仅作用于当前运行，不写入项目文件。

## 验证与截图
控制与渲染测试需要真实图形窗口；美术完整性测试可无头执行：
```
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

仍使用原创 Godot 网格与原生 .scn 预览；Blender 尚未找到，未制作正式 GLB 或骨骼动画。外围仍较稀疏，尚未达到目标商业美术质量。没有新增战斗、敌人或装备玩法。Windows 导出、Retina 多种缩放和长时压力未验证。

## GitHub
用户指定仓库：https://github.com/FAUSTFAST/Duel-Crowd 。`main` 跟踪 `origin/main`。使用 `git push origin main` 同步，不强推，不创建新仓库，不改变仓库可见性。最新实际推送结果以验证记录和 Git 日志为准。

第三阶段同角度对比：docs/stage3_before_overview.png 与 stage3_after_overview.png；角色近景为 stage3_before_knight.png 与 stage3_after_knight.png。前图从稳定提交 8b6bedc 独立渲染，后图来自当前项目，两者内部 640×360、HUD 隐藏、摄像机与出生点一致。截图期间请让游戏窗口保持可见；等待渲染帧在不可绘制的窗口环境中可能延迟。新造型未改变控制键位或像素调试方式。

第四阶段同角度对比：`docs/stage4_before_overview.png` / `stage4_after_overview.png`，骑士为 `stage4_before_knight.png` / `stage4_after_knight.png`。before 在稳定版本 8ba2e2a 改动前实际捕获；after 保持相同摄像机与出生点，冻结火焰至帧3只用于比较。`stage4_flame_motion.png` 则是实际动画连续采样，不冻结。

美术可调项：`forest_dressing.gd` 的 ground_height / islands / 老树位置，`forest_ruins.gd` 的色板及环境光、火炬、雾参数，`torch_flame.gd` 的帧率、像素尺寸、光强变化幅度。控制与渲染管线继续独立，按键不变。纹理重生成会覆盖文件：先提交手工编辑，再运行 `tools/export_environment_textures.gd`（仅六类环境纹理与火焰图）。
