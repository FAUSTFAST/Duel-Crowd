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
