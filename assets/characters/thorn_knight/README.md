# Thorn Warden / 枝誓守卫 — 独立美术候选

这是一份可以继续手工制作的原创角色候选及技术流程，不是已获美术批准的商业成品。Forest Valley仍使用原Ashen Knight；对比场景才引用本角色。没有引入任何第三方游戏模型、纹理或动画。

## 交付与状态

| 内容 | 实际交付 | 状态 |
| --- | --- | --- |
| 新模型 | `thorn_knight.glb`；38骨、5蒙皮表面、59,060三角形 | 可运行候选；三角形数不证明质量 |
| Blender源 | `source/blender/thorn_knight.blend` | 70个独立可编辑曲面零件 + 5个合并导出网格，打包2张材质图 |
| UV | `EquipmentUV` / `source/equipment_uv.svg` | 16用途区、留边；镜像四肢及小饰边有意共享，不是唯一烘焙UV |
| Albedo | `textures/equipment_albedo.png`，1254² | imagegen辅助绘制候选，需要像素美术师统一网格/色板；非严格32色图 |
| Roughness | `textures/equipment_roughness.png`，256² | 依据材料类别设计，不称扫描或高模烘焙 |
| Normal | 没有新法线贴图 | 形体靠真实曲面/折边/几何法线；高模雕刻烘焙待做 |
| 骨架/动作 | 原项目原创38骨与idle/walk/run/左右turn，五个Action均Fake User | 复用成熟接口，非全新手工动画或mocap |
| 2D/3D样本 | `textures/fern_cutout.png` | imagegen透明素材，三交叉卡、alpha scissor，仅在实验室 |

## Blender → Godot 流程

1. 修改前检查Git，保存手工编辑；使用Blender4.5.9 LTS米制、+Y向前/Z向上，GLB转为Godot-Y up/-Z forward。临时只读工具不安装全局软件。
2. 模型由 `tools/atelier/build_thorn_knight.py` 的设计曲面生成；胸甲前后/盔/盾/披风专门展开，关节和衣甲间隙保留。没有读取旧网格，只把原骨架/Action作为可复用动画库。几何量增加服务于形体，仍需人工检视。
3. 16格用途顺序见 `source/build_manifest.json`，行0在图像上方。Blender SVG显示真实UV线，工作UV在`.blend`中；小饰边/左右肢体复用区域已明确。禁止把本UV称为无重叠的烘焙UV。
4. 按材料合并仅用于导出：权重/UV/切线保留，原编辑曲面保留在隐藏集合。导出GLB使用ACTIONS、蒙皮、强制采样和切线；所有Action保留Fake User。
5. Godot首次导入后运行 `python3 tools/atelier/configure_imports.py` 再导入：仅本目录GLB使用嵌入图，PNG生成mipmap。`atlas_materials.gd` 独立管理局部UV材质，`thorn_visual.gd`继承已有状态机，不改生产输入/控制器。
6. `python3 tests/atelier_asset_test.py` 检查实际GLB；图形运行 `tests/atelier_test.gd`。用截图工具逐图比较，不能以脚本通过代替美术验收。

```sh
Blender -b --factory-startup --python-exit-code 1 --python tools/atelier/build_thorn_knight.py
Blender -b --factory-startup --python-exit-code 1 --python tools/atelier/audit_source.py
Godot --headless --path . --editor --import
python3 tools/atelier/configure_imports.py
Godot --headless --path . --editor --import
python3 tests/atelier_asset_test.py
Godot --path . --script tests/atelier_test.gd
Godot --path . --script tools/atelier/capture_atelier.gd
Godot --path . --script tools/atelier/capture_forest_context.gd
```

已有GLB时生成器拒绝覆盖；只有保存手工修改后才加 `-- --replace-generated`。Blender审计重新打开保存文件，实际检查全部动作、UV、打包图片与走跑平地剑尖高度。截图工具会覆盖 `docs/atelier`，运行前保存旧比较。

## 人工美术接续（下一步的可执行方案）

打开 `.blend` 后另存 `thorn_knight_artist.blend`。在Outliner显示 `EDITABLE_SURFACES`、暂时隐藏五个`Thorn_*`导出网格，避免重复显示。逐件检查肩颈连接、肘膝转折、头盔侧面、手部包握和披风落点；保留骨架与单位，不应用Armature modifier到静态姿态。

在UV工作区打开打包的Albedo，按胸/背/盔/盾/披风用途重新整理512px整数网格。先以128–256有效texel/m为主体目标做checker检查，装饰只在镜头下可读时保留。AI素材现有细碎锁子环、生成纹样及各格不一致的笔触需要人工重绘；原提示词见 `source/art/prompts.json`、`fern_prompt.json`，**实际尺寸/色数以文件为准**。

若采用雕刻高模，另存高模集合、重拓扑、建立不重叠烘焙UV并真正执行Normal/AO烘焙；本候选没有这些成果。最后按材质合并导出副本，保留编辑源与原五动作。不要直接重跑生成器覆盖人工源。

需要角色美术师/动画师完成正式造型与像素绘制、全姿态穿插、手部与原地踏转。现有自动化不能替代这些审美和表演工作；本轮没有采购或下载第三方资产。先在独立场景通过人工审图，再决定替换山谷。

## 实际运行对比

`docs/atelier/old_*` 与 `new_*` 是相同位置、姿态、镜头和光照下逐个替换资源的Godot实图。近景yaw=PI+0.3/pitch=-0.2/距离3.8m；本实验最小距离2.6m只作用实验室。游戏镜头0.16/-0.48/8m；1280×720窗口，640×360默认，另有480/960/原生。森林环境图为临时运行夹具替换，未保存修改生产场景。无AI合成游戏截图。

第一轮实图发现肩甲衔接空、披风偏亮，修形并调整两版共用中性灯光后重拍。动作周期审计发现垂直佩剑走跑穿地，改正握持高度与向外0.9rad倾角后复测。详细实测、限制和性能见项目 `docs/VALIDATION.md`。
