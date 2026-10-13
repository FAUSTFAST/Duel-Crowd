# 项目开发约定
使用中文报告。每次修改先检查 Git 状态并阅读现有实现。只操作本项目，不改全局配置。
本轮范围：初始化与基础 3D 原型；阶段 3 及战斗必须在后续任务推进。
视觉优先：需要实际运行截图验证，不以解析成功代替视觉验收。所有内容原创。
保持角色、摄像机、世界构建模块独立。Godot 4.x / GDScript；正式模型使用 Blender 导出的 GLB。
每个稳定阶段测试后提交与推送，重大修改前保留检查点；禁止强推和覆盖历史。
更新 README.md、ART_STYLE_GUIDE.md、DEVELOPMENT_PLAN.md、docs/VALIDATION.md。
明确区分本地提交与远程成功。授权失败不得宣称已同步；不打印或保存 Token。

本机已验证 Godot：`/Users/mac/Downloads/Godot.app/Contents/MacOS/Godot`（4.7.2）。Blender 未找到。执行 tests/prototype_test.gd 回归；图形运行 tools/capture_preview.gd 验证截图。只记录实际测试结果。

项目版本标记必须与实际验证的编辑器版本一致；当前为 4.7，未验证 4.3 兼容性。

摄像机输入回归 tests/prototype_test.gd 现在必须在图形窗口运行，不使用 --headless；捕获模式按 Esc 释放，点击重新捕获。

用户指定远程为 https://github.com/FAUSTFAST/Duel-Crowd.git；main 跟踪 origin/main。不要再创建 dark-fantasy-rpg 仓库。沙箱内授权检查可能无法读取钥匙串，网络可能无法连接本地代理；需在获准的网络执行中核实，不可将沙箱限制误报为真实凭据失效。
