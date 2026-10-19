# 2026-10-19：动作与表面图案实录

[新版12秒MP4](forest_movement.mp4) · [10秒GIF预览](forest_movement.gif) · [旧版运动实录](../character_motion/forest_movement.mp4) · [图案同镜头对照](../material_patterns/comparison_equipped.png)

Godot 4.7.2 / Apple M1 Compatibility 实际运行，640×360内部渲染，高清截图1280×720。360帧/30fps；角色通过真实输入动作和物理胶囊沿森林小路移动30.64m，360帧控制器均接地，没有逐帧改写玩家位置。6.5秒通过调试接口穿戴四件测试装备，11.5秒卸下；出生状态始终空装备。旧片保留，速度和路径进度不同，不声称两片每帧都处于相同位置。

新场景：`scenes/visual_lab/locomotion_valley.tscn`，编辑器双击后按F6。WASD步行、Shift奔跑、鼠标旋转、滚轮缩放、Esc释放/点击捕获、R复位；1/2/3/4切换头盔/胸甲/剑/盾，0恢复布衣空手。原Forest Valley和旧教堂不替换。

## 动作体系

空手待机、步行、慢跑、奔跑、起步、左右支撑脚收步、左右迈步转身，共九段原创Blender Action。保持原32骨rest和装备接口。动作设计借鉴魂类作品的重量、明确落脚和方向承诺；这是本项目的设计解释，不是对某工作室内部实现的复刻。

步态包含脚跟触地、全掌支撑、前掌蹬离、屈膝回收，对侧摆臂、自然手腕和相对稳定的头部。走跑片段统一周期相位，AnimationTree的BlendSpace1D按实际速度混合，60fps导入保留短接触姿态。参考实现依据[Godot AnimationTree文档](https://docs.godotengine.org/en/stable/tutorials/animation/animation_tree.html)；物理控制器负责位移，没有动画根位移。

调参入口：`scripts/wayfarer/locomotion_profile.gd` 的步速1.8m/s、跑速4.6m/s、加速度7.5m/s²、刹停12m/s²、反向刹停16m/s²、转速340°/s、启动转身阈值35°。`contact_locomotion.gd` 管理起停时长和混合；Blender源的步幅/接触曲线由`build_locomotion.py`维护。只给候选装配此profile，旧控制默认路径保留。

## 实际检查与限制

33项动作图形检查通过；平地片段接触点相邻采样最大漂移约0.144/0.352/0.448mm，最大腕部折角约3.9°，参考鞋底下穿约2.12mm。这里测的是导入片段的支撑窗口，不包括所有动画混合、斜坡和鞋面顶点；控制器接地也不等于每只鞋都贴地。没有坡地足部IK、布料碰撞或动作捕捉，仍需真人试玩与动画师逐姿态润色。

`test_results.json`、`recording.json`及`validation_logs.txt`记录执行数据。`walk_peak_m_s`包括由奔跑减速后的非sprint过渡，4.2不是稳定步速；稳定步行样本为1.8。固定时步录像不是性能基准。GIF为10fps共用256色调色板预览，MP4为完整30fps。编码后实际重新读取视频，验证640×360/360帧。

`poses/`是材质接入前、手腕修正后的实际正侧八相位截图，用于动作轮廓检查；当前图案效果见地图视频和`docs/material_patterns`。材质变化不改变动作、模型顶点或rest。

复现录像：图形运行`tools/wayfarer/capture_valley_motion.gd -- --locomotion`；已有录像时默认拒绝覆盖，保存检查点后才可加`--replace-review`。原始PNG留在临时目录，编码器拒绝覆盖已有成片。
