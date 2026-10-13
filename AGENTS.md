# 项目开发约定
使用中文报告。每次修改先检查 Git 状态并阅读现有实现。只操作本项目，不改全局配置。
当前范围：用户已重新授权独立森林山谷视觉样板，保留旧教堂地图；暂停一般性Low Poly装饰扩充，优先形体、高差、纹理和光影。禁止战斗、敌人AI、装备玩法和开放世界。
视觉优先：需要实际运行截图验证，不以解析成功代替视觉验收。所有内容原创。
保持角色、摄像机、世界构建模块独立。Godot 4.x / GDScript；正式模型使用 Blender 导出的 GLB。
每个稳定阶段测试后提交与推送，重大修改前保留检查点；禁止强推和覆盖历史。
更新 README.md、ART_STYLE_GUIDE.md、DEVELOPMENT_PLAN.md、docs/VALIDATION.md。
明确区分本地提交与远程成功。授权失败不得宣称已同步；不打印或保存 Token。

本机已验证 Godot：`/Users/mac/Downloads/Godot.app/Contents/MacOS/Godot`（4.7.2）。本轮已用官方SHA256校验的Blender4.5.9 LTS临时只读运行制作GLB，未安装全局软件；系统PATH仍无Blender。执行 tests/prototype_test.gd 回归；图形运行 tools/capture_preview.gd 验证截图。只记录实际测试结果。

项目版本标记必须与实际验证的编辑器版本一致；当前为 4.7，未验证 4.3 兼容性。

摄像机输入回归 tests/prototype_test.gd 现在必须在图形窗口运行，不使用 --headless；捕获模式按 Esc 释放，点击重新捕获。

用户指定远程为 https://github.com/FAUSTFAST/Duel-Crowd.git；main 跟踪 origin/main。不要再创建 dark-fantasy-rpg 仓库。沙箱内授权检查可能无法读取钥匙串，网络可能无法连接本地代理；需在获准的网络执行中核实，不可将沙箱限制误报为真实凭据失效。

主场景为 scenes/rendering/pixel_game.tscn。3D 世界在 SubViewport，高清 UI 在根视口；输入仅由 pixel_renderer 显式转发一次，不增加第二条输入路由。screen_relative 保持屏幕位移。图形运行 tests/rendering_test.gd 验收分辨率、像素重复、比例、UI 与输入；截图工具会生成三档、原生及移动对比。

美术源模块在 scripts/art；assets/models/*.scn 是可实例化的生成预览，不含控制器。纹理 PNG 为可编辑源文件，生成器会覆盖它们，执行前保留 Git 检查点。静态合批必须先统一去索引再合并；保留碰撞变换，不能把角色四肢合进静态躯干。运行 tests/art_integrity_test.gd 检查资源/三角形/碰撞；同角度截图使用 tools/capture_art_review.gd，截图工具禁用真实鼠标干扰，不修改生产输入行为。

第四阶段新增 forest_dressing.gd（确定性植被岛、可复用老树/灌木、与碰撞同源的路侧地形）；道路中心和教堂原高度不变。火焰在静态合批完成后创建，Sprite3D 八帧最近邻/透明裁切，运行时保持动画。静止像素测试只暂时冻结美术特效，再单独测试真实动画画面变化；性能采样必须重新启用动画。同角度截图阶段4，火焰连续采样 tools/capture_flame_review.gd。export_environment_textures.gd 覆盖六类环境PNG与火焰图，执行前保留检查点，不覆盖其他纹理。

森林山谷独立场景为 scenes/visual_lab/forest_valley.tscn（编辑器选中F6；F5旧地图不变）。scripts/valley复用原控制与摄像机，pixel_renderer的world_scene可配置，输入路由仍只有一条。assets/valley/source/blender/.gdignore排除原生源自动导入，运行时使用9份GLB与heightfield.tres。原始材质图来自built-in imagegen，工作贴图及估计法线/粗糙度明确标记研究用途，不称高模烘焙或最终美术。

重做前检查Git并保存手工编辑；tools/valley/prepare_materials.py、build_assets.py会覆盖山谷生成资源。configure_imports.py只改山谷sidecar，GLB嵌入模式3、PNG真实mipmap。tests/valley_test.gd必须图形运行，验证实际曲线路径游览、碰撞、GLB权重/切线、输入/渲染与短时性能；tools/valley/capture_valley.gd产生三档/原生/同镜头材质/移动截图。没有参考图时不得声称逐图匹配完成。
