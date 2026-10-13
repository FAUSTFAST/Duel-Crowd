# 灰誓 / Ashen Oath
原创暗黑奇幻 3D 动作 RPG，当前仅为阶段 1–2 基础原型。参考复古 3D 像素视觉语言，未使用 Duel Corp 代码或素材。

## 启动
使用 Godot 4.7.2 导入 `project.godot`，按 F6/F5 运行主场景。当前验证引擎版本见 docs/VALIDATION.md。

WASD / 方向键移动；Shift 跑步；启动自动捕获鼠标，直接移动鼠标旋转视角；滚轮缩放；R 返回出生点；Esc 释放鼠标；左/右键点击游戏画面重新捕获。失去窗口焦点也会释放鼠标。关闭窗口退出。

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
已关联用户指定仓库：https://github.com/FAUSTFAST/Duel-Crowd ，`main` 跟踪 `origin/main`。稳定摄像机版本 `e7ac7db` 已成功推送并核对远程提交。后续使用 `git push origin main` 同步；不要提交凭据或强制推送。

## 验证与预览
`tests/prototype_test.gd` 可用 Godot `--path . --script tests/prototype_test.gd`（包含鼠标捕获测试，必须使用图形窗口） 执行。`tools/capture_preview.gd` 必须使用图形渲染运行，保存实际游戏截图至 `docs/prototype_preview.png`。

摄像机参数在 `scripts/camera/orbit_camera.gd` 的导出变量中调整：mouse_sensitivity、俯仰上下限、follow_offset、follow_speed、rotation_speed、min/max_distance、zoom_step、zoom_speed。当前摄像机由 Knight 脚本创建；可改导出默认值，或在创建时赋值。
