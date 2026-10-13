# 灰誓 / Ashen Oath
原创暗黑奇幻 3D 动作 RPG，当前仅为阶段 1–2 基础原型。参考复古 3D 像素视觉语言，未使用 Duel Corp 代码或素材。

## 启动
使用 Godot 4.3+ 导入 `project.godot`，按 F6/F5 运行主场景。当前验证引擎版本见 docs/VALIDATION.md。

WASD / 方向键移动；Shift 跑步；按住鼠标右键旋转视角；滚轮缩放；R 返回出生点；Esc 退出。

## 结构
- scenes/：主场景；运行时生成确定性的原创占位环境与骑士
- scripts/world/：场景构建与几何工具
- scripts/characters/：角色移动和程序化占位动画
- scripts/camera/：跟随、碰撞避让与视角控制
- assets/：后续原创 GLB、贴图、材质、音频
- shaders/：阶段 3 像素渲染预留
- tests/：自动场景和移动回归检查
- docs/：验证与环境记录

本轮使用真实 3D、低面数几何、动态阴影和深度雾。尚未实现低分辨率 SubViewport、像素贴图、战斗或正式骨骼动画。UI 独立 CanvasLayer，为后续高清 UI 保留结构。

## GitHub
预期私有仓库 `dark-fantasy-rpg`。仅在 CLI 授权有效时创建和推送；实际状态见验证记录。不要提交凭据。恢复授权：`gh auth login -h github.com`，随后 `tools/sync_github.sh`（会检查私有可见性）。

## 验证与预览
`tests/prototype_test.gd` 可用 Godot `--headless --path . --script tests/prototype_test.gd` 执行。`tools/capture_preview.gd` 必须使用图形渲染运行，保存实际游戏截图至 `docs/prototype_preview.png`。
