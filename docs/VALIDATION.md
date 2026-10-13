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
