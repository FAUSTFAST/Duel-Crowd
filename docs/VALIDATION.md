# 阶段 1–2 验证记录
日期：2026-10-13（Asia/Shanghai）。

## 环境
- macOS / Apple M1；Git 可用。
- Godot 4.7.2.stable.official.ed1daf0bf，位于 `/Users/mac/Downloads/Godot.app/Contents/MacOS/Godot`，不在 PATH。
- Blender：PATH、Applications 及 Downloads 检查未找到；本轮不依赖 Blender，全部为原创程序化占位几何。
- gh CLI 可用；FAUSTFAST 现有凭据无效。未更改全局配置或凭据。

## 已执行
1. Godot 编辑器导入成功；首次沙箱运行出现用户缓存/日志目录权限错误。后续获执行权限后运行不再出现这些错误。
2. 主场景 headless 运行 120 帧，退出 0，无脚本错误。
3. `tests/prototype_test.gd` 最终回归退出 0：落地、相机激活、滚轮缩放、相机 yaw 跟随、相机相对移动、跑步速度、墙体阻挡、出生点重置、跌落恢复，9 项通过。
4. `tools/capture_preview.gd` 以图形模式实际运行。Apple M1 OpenGL 4.1 Metal Compatibility，保存截图返回 0。首次截图工具类型推断错误已修复。查看实图后降低火光和日光，拉远镜头，重新运行并查看 `docs/prototype_preview.png`。
5. 实图可见骑士、圣堂入口、森林、石板路、火光、动态阴影与雾。当前不具备正式像素贴图、SubViewport 像素化或骨骼动画。

## 限制
- 未进行 Windows/macOS 导出包验证、长时间性能测试或手工键鼠试玩。自动测试操作 Input action 和相机接口；不等同于完整真人试玩。
- 场景由脚本确定性生成，可编辑的正式 GLB 场景资产尚未制作。
- 火焰为静态发光占位，没有粒子特效。
- Compatibility 优先可运行性；后续需对正式渲染管线、雾与阴影在两平台验证。

## Git 与 GitHub
- 初始化检查点：`30f1d08`（本地提交成功）。
- 阶段 2 稳定提交使用 `git log -1 --oneline` 查看，包含本记录与实际截图。
- `tools/sync_github.sh` 实际执行退出 1：GitHub 授权失效。未关联 origin，未创建私有远程，未推送。没有可报告的已验证 GitHub 项目 URL。
- 用户运行 `gh auth login -h github.com` 恢复授权后，可执行 `tools/sync_github.sh` 创建 `dark-fantasy-rpg` 私有仓库并正常 push；脚本不强推。若同名仓库已存在，创建会安全失败，需先检查再关联。

## 版本提示修复
项目初始 config/features 错标为 4.3，但实际测试引擎为 4.7.2，导致项目管理器提示升级到 4.7。现已修正为 4.7，并移除 README 中未经验证的 4.3+ 兼容声明。重新运行 9 项回归全部通过（退出 0）。未改动视觉或玩法；尚未通过项目管理器 UI 复测弹窗。

## 第三人称摄像机优化
- 修改前检查点 d056f1f 保存用户打开 Godot 后产生的项目格式与导入/UID 元数据；没有回退或覆盖这些变更。
- 启动捕获鼠标，InputEventMouseMotion.screen_relative 直接控制视角；Esc 在 _input 中释放并消费事件，删除世界旧退出逻辑。左/右键点击游戏画面重新捕获，失焦/退出场景释放鼠标。
- 跟随、旋转和缩放使用指数平滑，跟随在角色物理更新后执行；保留 SpringArm 碰撞避让、角色排除、默认 FOV、距离、场景灯光与材质。
- 导出旋转灵敏度、俯仰限制、跟随偏移/速度、旋转速度、距离上下限、滚轮步长和缩放速度。
- 首次 headless 测试的 7 项鼠标相关检查失败：无头显示后端不能捕获鼠标。改用真实图形窗口后 19 项全部通过，退出 0；测试脚本现明确拒绝无头运行，退出 2，不伪报通过。
- 图形测试使用窗口输入事件注入验证鼠标转动、Esc 和点击传播；位置跟随收敛、滚轮/上下限、俯仰限制、原角色移动、跑步、碰撞及重置均通过。不是手工真人试玩；窗口失焦释放已实现，但未单独模拟操作系统焦点切换。
- capture_preview.gd 实际 OpenGL 图形运行退出 0；查看更新截图，默认构图正常，UI 提示已更新。
- GitHub 同步尝试仍因授权失效退出 1；origin 未配置，未创建仓库或远程推送。
- 鼠标事件依据 Godot 官方说明：https://docs.godotengine.org/en/stable/classes/class_inputeventmousemotion.html

## 指定仓库同步成功（2026-10-13）
用户指定 https://github.com/FAUSTFAST/Duel-Crowd.git。沙箱内出现授权/代理连接错误；获准网络执行后 gh 确认 FAUSTFAST 授权有效，目标仓库无已有 refs。添加 origin，正常 push main 成功；远程 refs/heads/main 核对为 e7ac7dbce30f57563ad80ae21b05f431dedd299a。此前授权失败记录是当时沙箱检查结果，不能代表当前真实凭据失效。未强推或删除历史。本次仅更新同步文档，不改游戏，未重复运行游戏测试。

## 第二阶段：像素渲染与基础视觉优化（2026-10-13）
开发前稳定提交 37939e6；git fetch 后 main 与 origin/main 一致，工作区没有已有用户修改。先实际渲染并保存 visual_before.png，再开始修改。引擎仍为 Godot 4.7.2 / Apple M1 OpenGL 4.1 Metal Compatibility。

### 实现与修复
- 主场景 pixel_game.tscn，WorldViewport 单独渲染 3D，默认 640×360、可选 480×270 / 960×540；高清 UI 在根窗口 CanvasLayer。
- 最近邻呈现与纹素中心 Shader；默认整数倍居中留边，F6 等比适应；原生对比也保持整像素 16:9。根窗口禁用 canvas_items 拉伸，使 UI 使用窗口分辨率。
- 独立调试模块处理 F1/F2/F3/F4/F6 和环境光 +/-，其他输入只向 SubViewport 转发一次，保留 screen_relative 和已有摄像机/移动逻辑。
- 原创确定性 64px 石材、路面、土壤、树皮、针叶、钢板、布料纹理，缓存且只在初始化生成；三平面映射、最近邻 mipmap。保留布局，增加棱面碎石和少量草簇。
- 实图发现最初地面纹理太密，降低对比与高频细节后重新截图。调节冷色方向光/雾与局部暖光。
- 启用物理插值，传送时 reset_physics_interpolation；修复出生点在摄像机初始化后赋值的顺序。静止测试第一次未通过（相机尚在收敛），修复顺序并充分预热后通过。
- 截图工具的 RGB/RGBA 拼接不一致已修复，重新生成移动采样。测试工具的类型声明错误已修复。

### 最终实际测试
- 编辑器 --headless --editor --import --quit 导入退出 0。
- 图形运行 tests/prototype_test.gd：19 项通过，退出 0，涵盖鼠标捕获/释放/点击、无按键转动、平滑跟随、缩放、WASD/奔跑/碰撞与重置。
- 图形运行 tests/rendering_test.gd：28 项通过，退出 0。确认真实 SubViewport 分辨率、根 UI 与世界视口分离、无屏幕 AA；采样区域每个 2×2 像素块颜色完全一致；预热后的静止世界图像逐字节一致；三档切换/鼠标灵敏度、原生开关、纹理/雾/环境光调试通过。
- 实际调整窗口到 1000×700，验证 640×360 整数显示在 (180,170) 居中；留边点击不捕获，画面内点击捕获。适应缩放保持 1000×562.5 比例；原生模式为 992×558 精确 16:9。640×360 小窗口显示 960 档等比缩小。
- 短时预热采样 180 帧，640×360 平均帧间隔 8.30ms、P95 10.42ms；约 1157 渲染对象计数、1190 draw calls（含阴影重复绘制）。这些是本机短测数据，不是纯 GPU 时间，不代表跨平台帧率保证，扩大地图前需压缩阴影绘制开销。
- tools/capture_preview.gd 实际图形运行退出 0，全部 PNG 保存成功；已人工查看三档、原生与连续移动采样。

### 截图与边界
- visual_before.png：本阶段开发前实际渲染。
- visual_pixel_640.png / prototype_preview.png：最终默认像素渲染。
- visual_native.png：相同新材质与光照的原生渲染，用于单独对比像素效果。
- visual_pixel_480.png、visual_pixel_960.png：整数倍留边；故画面显示面积与默认不同，这是预期取舍。
- visual_motion.png：移动并旋转的四个连续采样画面（内部分辨率，未包含 UI）。

静止无闪烁测试通过，但截图/稀疏采样不能证明所有运动无闪烁；透视旋转、细枝、远处阴影与非整数缩放仍需真人试玩。未进行 Windows 导出、Retina 多种缩放、长时负载或全面手工输入测试。正式 GLB、骨骼骑士、粒子火焰尚未制作；当前不声称达到参考游戏商业美术质量。本轮没有新增战斗/敌人/装备。

渲染依据官方文档：https://docs.godotengine.org/en/stable/classes/class_subviewport.html 、https://docs.godotengine.org/en/stable/classes/class_basematerial3d.html 。最新提交/同步结果以本轮 git log 与远程核对为准，继续使用用户指定 Duel-Crowd 仓库，不改可见性或历史。
