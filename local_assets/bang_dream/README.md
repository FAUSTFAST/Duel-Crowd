# BanG Dream 角色本地素材库

这是用户要求收集的第三方角色资料，独立于 Ashen Oath 的原创游戏资产。Godot 自动导入已通过 `.gdignore` 隔离；模型、压缩包、贴图和预览均不提交 Git。2026-11-03按新增要求接入独立本地地图陈列，没有更换正式角色或原地图。下载不等于取得游戏发布、商用或再分发许可。

## 查看若叶睦在地图里的效果（2026-11-03）

Godot打开 `scenes/visual_lab/local_model_preview.tscn`，使用“运行当前场景”（F6，Mac功能键设置可能需要Fn+F6）。F5依然运行原项目主场景。

- 默认静态陈列：鼠标旋转、滚轮缩放，Esc释放鼠标、点击重新捕获。
- Tab切回原骑士游览：WASD移动、Shift奔跑；再次Tab返回模型。
- F1开关像素化、F2三档内部尺寸；F3仅切环境/原骑士细节，不会切若叶睦的PBR纹理。
- 模型没有待机/走跑动画，不能把静态站姿当作已适配的可操作人物。陈列物无独立碰撞。

本机实际图形运行截图仅本地保存：`previews/mutsumi_map_v2/forest_front_640.png`、`forest_three_quarter_640.png`、`forest_three_quarter_native.png`。

本轮新副本 `models/mutsumi/map_preview_v2/mutsumi_map.glb`：12网格、45,512三角形、204导入骨（203原骨+neutral_bone）、约3MB。`source_display_pose`是原源单帧站姿快照，不是动作片段。制服/裙/鞋用原彩色图，头发/肤色为简化近似；森林强光下肤色偏亮，原卡通材质、描边和物理尚未复现。旧失败prepared副本保留，不再用作地图展示。

新增GLB在ignored库中，由主项目GLTFDocument运行时读取，未取消.gdignore；GitHub不包含第三方模型/贴图/截图。另一台机器需合法取得本地模型并按同一路径放置，否则预览显示缺失提示。可复验：

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path . --script res://tests/local_model_preview_test.gd
```

`tools/model_library/export_local_preview.py`只在禁用自动执行的Blender进程运行，读取原生源而不保存，默认拒绝覆盖已有输出。衍生副本及原件摘要分别记录在本地manifest和catalog；不把近似显示当作游戏发布授权或正式适配。

## 已下载

- **若叶睦**：`models/mutsumi/还原睦.glb`；原压缩包 `archives/mutsumi/还原睦.zip`。来自 [小泽LoneL 的 GLB 分享说明](https://www.bilibili.com/video/BV1V5QoYHE1g/)，分享者说明改自很ying的哈呵。实际包只有 GLB，没有独立授权文件；游戏用途尚未获确认。
- **同一人物的原生资料包**：同一分享说明的 [另一公开下载](https://wwzh.lanzout.com/iJXJm2l4931g) 实际取得 `MyGO.zip`（26,977,956 字节），不是五人合集。原压缩包在 `archives/mutsumi/MyGO.zip`，解压在 `source/mutsumi/`，可在 Blender 打开 `source/mutsumi/01doing.blend`，保留同目录 `textures/`。已禁用自动脚本后只读重开，203 骨、0 动作、29 张图可加载；没有覆盖或保存原生文件。
- 文件审计及实际 Blender 导入结果保存在本地 `reports/`，预览在 `previews/`。静态导入不代表已经适配现有角色骨骼或动作。

### 实际发现的兼容性问题

原 GLB 有 104 个网格资源、204 骨、0 动画和 7 张内嵌图；Blender 导入形成105个网格对象，包含可见的 MMD 刚体辅助物和地面。原 GLB 主要把阴影/高光图接在自发光通道，**实际渲染颜色不正确，不能当作已完成游戏适配**。

`reviews/mutsumi_prepared_review.blend` 和 `models/mutsumi/prepared/mutsumi_preview.glb` 仅为本地诊断实验：隐藏89个辅助物、尝试通道迁移，保留骨架；颜色仍异常，不作为可用角色推荐。`previews/mutsumi*` 保存真实试渲染，包括失败结果，不用绘图修饰冒充成功。下一步应从原生 `.blend` 恢复卡通材质/Albedo导出，再单独测试Godot；当前没有进行动画、控制器、碰撞或性能适配。

## 其余 8 名：尚未下载

| 角色 | 已确认的来源 | 当前阻碍 |
| --- | --- | --- |
| 千早爱音 | [Liope 原配布](https://www.aplaybox.com/details/model/6FWdVCZUFzMh) · [作者视频](https://www.bilibili.com/video/BV1Zx4y1e7Ec/) | 模之屋已登录；关注作者、点赞和收藏的下载条件待明确授权。原百度盘通道被浏览器安全策略阻止。作者页禁止商用。 |
| 高松灯 | [BungleScrungle MyGO 包](https://www.deviantart.com/bunglescrungle/art/BanG-Dream-MyGO-FBX-and-PMX-DL-1036304336) · [竹芩子改版](https://www.aplaybox.com/details/model/rSoGnOxd1faF) | 原包作者页访问受限；改版需登录/密码，禁止商用和暴力表现。未验证包内角色。 |
| 椎名立希 | [MyGO 联动服装包](https://www.deviantart.com/bunglescrungle/art/BanG-Dream-Ave-Mujica-collab-FBX-and-PMX-DL-1188270509) | 作者标签包含立希等五人，但下载托管 MEGA 被浏览器安全策略阻止；未验证包内容。 |
| 要乐奈 | [MyGO 联动服装包](https://www.deviantart.com/bunglescrungle/art/BanG-Dream-Ave-Mujica-collab-FBX-and-PMX-DL-1188270509) | 同上；不能只凭标签称模型已经齐全。 |
| 长崎素世 | [Liope 原配布](https://www.aplaybox.com/details/model/iuJMdFxoU6KY) · [作者视频](https://www.bilibili.com/video/BV1e84y1S7R2/) | 模之屋已登录；同作者配布下载条件待明确授权。允许视频外用途但禁止商用。 |
| 丰川祥子 | [Liope 原配布](https://www.aplaybox.com/details/model/Q0IbLG0mIe4l) · [作者视频](https://www.bilibili.com/video/BV17p4y1T79e/) | 模之屋已登录；同作者配布下载条件待明确授权。禁止商用。 |
| 八幡海铃 | [很ying的哈呵模型展示](https://www.bilibili.com/video/BV1XTtpeyETK/) | 仅确认模型展示，简介没有配布链接，未找到可核实的公开原包。 |
| 三角初华 | [SSSS.sagisu 免费 Blender 模型](https://sagi3d.gumroad.com/l/xjhwh) | Gumroad 零元领取需用户邮箱；尚未领取或确认游戏许可。Blender 4.x/MerlinToon 不能直接等同 Godot 材质。 |

八幡海铃在请求中重复，按一名计；共 9 名。没有擅自补入未列出的祐天寺若麦。

## 其他公开候选

- [Sedl_04 的爱音/素世 Blender 配布](https://www.bilibili.com/video/BV1pZuE6UE4i/)：作者公开的夸克分享为 `https://pan.quark.cn/s/4292fd44c202?pwd=KWW4`，显示 `Soyo_Anon_5.2_Ver0.5.rar`，57.6 MB；匿名访问需要登录。禁止商用和公开二次配布，尚未下载。
- 联动 FBX/PMX 包的作者公开托管：`https://mega.nz/file/lftlhJDY#xc06lDPBn0FtiR4OJgKm_b-YWBKOgKsZsT0dAxN-bYg`。浏览器安全策略拒绝自动访问，未使用其他工具绕过。该包名称含 Ave Mujica，但作者标签指向 MyGO 成员，不能当作 Ave Mujica 四人的已下载资源。
- [MyGO 原服包](https://www.deviantart.com/bunglescrungle/art/BanG-Dream-MyGO-FBX-and-PMX-DL-1036304336) 当前标题是 `MyGO!!! Let's Start a Lifetime Costume`，作者 BungleScrungle 公开标注33.2MB、FBX/PMX；公开托管为 `https://mega.nz/file/we8ESLYJ#5cSmQK1NFgYNADAFnFGS8adID9kle7OVlo8CGLBphB8`。只记录链接，未绕过 MEGA 访问限制。作者说明游戏提取、需署名 Bushiroad Games、禁止销售数据，并提示缺物理/姿态与眼骨权重仍待修复；这不是权利人的游戏发布授权。

## 后续领取与检查

模之屋已确认登录成功，但关注作者、点赞和收藏的动作被自动审批拒绝，因为此前下载授权没有明确包括账号互动；现正等待用户对这三类必要下载条件的明确授权，未绕过拒绝。Gumroad 初华仍需用户提供授权领取邮箱或自行领取。涉及验证码或同意网站条款的步骤需用户操作/明确确认。被浏览器安全策略阻止的网盘如需继续，请用户自行下载到系统“下载”目录，再告知文件名；不会要求发送密码或 Token。

收到文件后逐包校验、保留原作者说明与来源，更新 `catalog.json`，再检查骨骼、材质、比例和动画。尚未明确许可的素材继续保留在隔离目录，不自动进入可发布游戏或 GitHub。

复核本地现有文件：

```sh
python3 tools/model_library/audit_library.py
```

本轮更新：2026-11-03。精确状态及 SHA256 见 `catalog.json`，未下载项的 `files` 必须为空。
