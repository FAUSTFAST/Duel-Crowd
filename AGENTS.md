# 项目开发约定

2026-10-19 动作候选：contact_locomotion.gd + locomotion_profile.gd 仅用于silhouette；旧控制默认profile=null。九段60fps Blender动作（idle/walk/jog/run/start/stop_left/right/turn_left/right）；走跑周期统一1秒相位、实际周期由速度驱动，禁止把GLB重采样回30fps。build_locomotion.py只重做动作，校验网格/UV/rest不变，执行前保存检查点。图形tests/locomotion_test.gd检查实际导入接触、腕部、起停与反向；独立可游玩场景locomotion_valley.tscn。原森林/教堂不替换。录像capture_valley_motion.gd -- --locomotion输出docs/locomotion_review，旧docs/character_motion保留；录制工具需运行到完成标记，不能将quit-after提前退出当通过。

最新方向（2026-10-17）：用户设计图是唯一主要外观参考，禁止自由发挥“类似风格”。先轮廓还原、由用户审核，再细节完善。当前候选 `assets/characters/reference_silhouette`、场景 `scenes/visual_lab/reference_silhouette.tscn`；旧wayfarer/原地图保留，不能自动替换。`reference_surfaces.py`为独立曲面配方；共享生成器用 `--silhouette-study` 选择输出目录，重建覆盖前保留手工编辑。不能因267项工程检查通过称还原通过。
`review_silhouette.py`重新打开新旧.blend并同机位实拍；`capture_silhouette.gd`为Godot三视图/640/游戏距离/动作实拍。新截图在docs/silhouette_review，不覆盖历史。32骨rest矩阵保持完全一致，姿态通过动画调节；新装备Resource使用副本，旧目录不写入。运行`python3 tests/silhouette_asset_test.py`和图形`tests/equipment_test.gd -- --silhouette`。脸、发束、布料与靴面仍需按图精修，停在用户要求的轮廓审核门槛。

当前参考更新：用户提供冒险者多视图并明确要求Blender建模；发型和服饰以本轮图为准，替代上一版露额短发/长袖约定。卷袖、裸露前臂/皮护腕、短分叉布衣、棕红围巾、黄铜腰扣/皮包、折边靴；初始无盔甲/武器/盾牌。traveler_surfaces.py和traveler_textures.py为生成入口，32骨rest保持；不要以骨骼缩放改变比例。
setup_blender_review.py只在游戏GLB导出之后创建原生审阅摄影棚和用户参考图。TEST_EQUIPMENT_optional默认隐藏，衣内躯干默认隐藏；Review四相机、摄影棚地面/灯光和用户图不能进入GLB。150未合并编辑曲面在EDITABLE_SURFACES；用户设定图不是本项目原创，不能当游戏纹理或实际3D渲染成果。
docs/adventurer_reference/before_*是2d69e80稳定图；旧docs/traveler与docs/proportions不覆盖。capture_proportions当前输出docs/adventurer_reference/after_*；render_blender_review输出blender_*。capture_equipment仍覆盖docs/wayfarer，先保留稳定比较。源码重开审计验证原生默认无装备与四相机，GLB测试检查审阅物件未泄漏。
胸甲遮挡torso_cloth/waist_tie/collar，保留袖子与衣摆，卸下恢复。此版本是参考图指导的模型候选，脸/手、布褶和绘制仍需人工精修，不能因测试通过声称美术达标。

当前授权新增：只在 scenes/visual_lab/character_equipment_lab.tscn 开发布衣基础人物与四件装备外观切换原型（头盔/胸甲/剑/盾），八个预留槽位。禁止完整背包、属性、掉落或战斗扩展。Forest Valley、旧教堂、两版旧骑士和原控制不替换。
assets/characters/wayfarer 是新32骨/独立动作/局部UV人物候选，不能称正式精修人物。tools/wayfarer/build_wayfarer.py 默认拒绝覆盖；保存手工编辑后才使用 -- --replace-generated；.blend源在source/blender/.gdignore内，运行使用五份独立GLB。128px像素色板纹理为原创程序绘制，无新AI图或高模烘焙。
scripts/equipment只处理视觉：装备Resource ID/槽位/模型/遮挡/挂点；蒙皮按骨名+rest验证并重绑基础Skeleton3D，剑盾BoneAttachment3D；失败保持原装备，穿卸不得重建人物、动画树或摄像机。身体遮挡取所有穿戴物品mask并集，卸下恢复布衣/头发。输入仍只有pixel_renderer一条转发，高清按钮应消费点击，避免触发重新捕获。
运行 python3 tests/wayfarer_asset_test.py、图形 tests/equipment_test.gd；tools/wayfarer/audit_source.py独立重开源文件；capture_equipment.gd会覆盖docs/wayfarer本轮图，保留稳定对比再使用。实际无装备/穿卸/走跑/相同游戏距离截图与源权重测试分别验收。不能把自动周期、平地短测当作手工动画、坡地IK或全姿态无穿插。

混合美术新实验仅在 scenes/visual_lab/knight_atelier.tscn，B切换原Ashen Knight/新Thorn Warden，L灯光，0正常移动、1/2/3动作预览；Forest Valley和旧角色不替换。scripts/atelier 独立继承已有控制/动画/渲染，仍只有pixel_renderer一条输入转发。
assets/characters/thorn_knight 为候选，不能称正式商业美术。保留70编辑曲面、用途UV与原38骨/5Action复用；有意镜像UV不称无重叠烘焙UV。imagegen辅助Albedo/蕨叶提示和实际规格在source/art；没有新高模法线烘焙，不以生成提示当作实际像素尺寸/色数。
tools/atelier/build_thorn_knight.py 默认拒绝覆盖；手工修改先存Git，再考虑 -- --replace-generated。Blender脚本加 --python-exit-code 1；audit_source.py必须重新打开源文件检查动作/打包图/剑尖余量。运行 python3 tests/atelier_asset_test.py 与图形 tests/atelier_test.gd；截图 capture_atelier.gd / capture_forest_context.gd 仅改运行夹具，会覆盖docs/atelier截图，先保留稳定比较。不自动推进到正式场景替换。
使用中文报告。每次修改先检查 Git 状态并阅读现有实现。只操作本项目，不改全局配置。
当前范围：森林山谷视觉样板保留，用户已授权布衣基础人物、材质、骨骼动画与四件装备外观切换原型；保留旧教堂地图和原控制，不扩建环境。暂停一般性Low Poly装饰扩充。禁止战斗、敌人AI、完整装备玩法和开放世界。
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

山谷新骑士：assets/characters/ashen_knight/ashen_knight.glb、打包source/blender/ashen_knight.blend（.gdignore）、五套128px纹理及五段Action。38骨、五个按材质合并的蒙皮表面；骨骼权重不能在合批中丢失，所有Action须Fake User保留。tools/characters两个生成器会覆盖本角色资源，执行前保存手工编辑；configure_imports只作用本角色sidecar。Normal为绘制浅高度细节，不称高模烘焙；美术首版需人工精修，不称参考游戏商业成品。

基础knight.gd仅提供_build_visual/_animate_visual扩展点，原移动/碰撞/摄像机不变；valley_knight导出visual_scene指向scenes/characters/ashen_knight_visual.tscn，rigged_knight_visual管理AnimationTree/速度倍率/低速换向，knight_materials管理局部材质。不能把新骨架塞入旧四肢正弦动画，也不增加第二条输入路由。world.set_art_animation仅作为调试/截图冻结新骑士和火光，生产默认启用；冻结像素测试之后必须恢复动画再做实际游览/性能。

执行python3 tests/knight_asset_test.py与图形tests/knight_animation_test.gd，回归原控制/渲染/valley。同镜头工具tools/characters/capture_knight_review.gd（-- --before仅在改造前执行），截图保存在docs/knight；它会覆盖本轮截图，先保留稳定对比。步态脚滑移测试针对平地参考高度，不代替坡地IK和真人试玩。保留旧教堂角色，F5旧地图；F6或停止按钮右侧“运行当前场景”播放场记板运行forest_valley。

地图移动实录：tools/wayfarer/capture_valley_motion.gd 仅在运行时给原valley玩家换silhouette_visual，不保存地图；图形 --fixed-fps 30，帧留临时目录。encode_motion_gif.py / encode_motion_video.py将真实帧编码，拒绝覆盖已有成片。docs/character_motion为实录，非性能基准或美术验收。
