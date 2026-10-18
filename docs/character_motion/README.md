# 森林地图移动实录 — 2026-10-18

[播放12秒MP4](forest_movement.mp4) · [10秒动图](forest_movement.gif)

实录使用现有 Forest Valley Study 地图和 reference_silhouette 轮廓候选。角色初始空手、无护甲、无盾牌；仅在录制运行夹具中替换外观，原地图文件和原角色保留。

视频展示正面步行、镜头环绕、背面奔跑、沿山谷小路折返与减速。通过原控制器的 Input actions 驱动实际 CharacterBody3D 移动，动画状态机、地形碰撞、摄像机平滑跟随和环境动画保持运行，没有逐帧传送或合成动作。

640×360内部渲染。MP4为360帧/30fps/12秒；GIF取前10秒，每3帧采一帧，使用统一256色色板。视频更适合观察完整连续动作，动图存在降帧和色板量化。固定录制时步不代表实机性能测试。

实际记录见 [recording.json](recording.json)：水平累计移动44.43m，360/360帧控制器接地，稳定步行采样约3.2m/s，奔跑峰值约5.8m/s。walk_peak字段包括从奔跑减速过渡，因此不是稳定步行速度。接地记录只验证控制器，不代替脚底视觉、坡地IK或动作自然程度验收。

[步行截图](walking.png) · [奔跑截图](running.png) · [转向截图](turning.png)。当前模型与动画仍是待审核候选；本轮没有重制美术或改变原动画。

复现：图形运行 tools/wayfarer/capture_valley_motion.gd（Godot --fixed-fps 30），帧写到/private/tmp/duel-crowd-motion-20261018；用 encode_motion_gif.py（Pillow）或 Blender 4.5 的 encode_motion_video.py 编码。后者使用Blender内置FFmpeg，不依赖系统Swift/SDK；本机Swift与SDK版本不匹配，未修改全局配置。编码工具拒绝覆盖已有成片，重录前保存旧录像。大批PNG帧不提交Git。
