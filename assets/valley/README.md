# 森林山谷美术研究资产

这是可游览的**视觉样板**，不是已完成的商业级资产包。旧教堂地图与占位资产原样保留。本目录采用真实 Blender 4.5.9 LTS → GLB → Godot 4.7.2 工作流，没有使用 Duel Corp 的模型、纹理或游戏截图，也没有引入第三方美术包。

## 来源与制作

- `source/blender/valley_studies.blend`：可打开、贴图已打包的 Blender 源库。`source/blender/.gdignore` 防止 Godot 自动调用本机未配置的 Blender；运行时使用明确导出的 GLB。
- `tools/valley/build_assets.py`：可重做的米制原创建模脚本；连续地形、侵蚀岩石、根系/树干/枝条/叶片、灌木、弯曲草叶/花瓣，以及分离四肢的铠甲骑士。主动三角化并导出 UV/切线、地形顶点混合权重。骑士没有骨骼绑定，沿用原控制器的四肢节点运动。
- `models/*.glb`：9 个可复用研究模型（地形、两种岩石、两种树、灌木、草簇、花簇、骑士）。源统计见 `source/model_manifest.json`。树冠使用有透明空隙的叶片卡，不用球形冠团或圆锥。岩石采用连续变形的侵蚀面，不用方块堆叠。
- `source/forest_material_atlas.png`：本轮使用 **built-in imagegen** 生成的原创四区域材质源图；是纹理源，不是游戏截图。提示词要点见下面的制作记录。全部实际游戏截图在 `docs/valley`。
- `tools/valley/prepare_materials.py`：裁切、256px 降采样、96 色量化、轻量接缝处理；输出泥土、页岩、苔藓、树皮 Albedo / Normal / Roughness。叶片、钢、皮革、布料由本地代码绘制，保持单独的可编辑 PNG。
- Normal 是**由 Albedo 亮度估算**的微表面信息，Roughness 是美术设定；没有宣称扫描数据、高模烘焙或真实物理测量。
- `source/heightfield.json` 为建模记录；`heightfield.tres` 是运行时显式依赖，保证地形高度/小径数据随场景导出。实际碰撞直接由 GLB 网格生成，高度表用于放置装饰。

## Imagegen 提示词记录

提示词要点（制作意图摘要）：原创暗黑奇幻森林的平铺材质图集，四个等大的正方形；左上为带枯叶和树根痕迹的湿褐色泥土，右上为有细小侵蚀裂隙的青灰层状页岩，左下为有蕨叶细节的深橄榄色苔藓，右下为深沟槽、木结丰富的老树树皮。要求平坦漫反射、丰富且统一的复古材质细节、不烘焙方向阴影、无文字/边框/场景物体、不复制任何游戏资产。实际生成结果偏自然材质研究，经过量化与采样处理后用于本样板；不能把它称为手工像素画或扫描 PBR 套装。

## 重做流程

先检查 Git、保留检查点及所有手工编辑。这些工具会**覆盖本目录生成文件**，不修改旧地图的纹理或模型。

```sh
python3 tools/valley/prepare_materials.py  # 需要 Pillow / numpy
Blender --background --factory-startup --python tools/valley/build_assets.py
Godot --headless --path . --editor --import
python3 tools/valley/configure_imports.py
Godot --headless --path . --editor --import
Godot --path . --script tests/valley_test.gd
Godot --path . --script tools/valley/capture_valley.gd
```

GLB sidecar 使用 Embed as Uncompressed（3），保留单文件预览纹理；运行时由材料库统一引用 `textures/`。已提交 PNG 导入侧文件启用 mipmap，材质与地形 sampler 采用最近邻 mipmap，呈现层保持精确最近邻。[官方 GLTFState 模式说明](https://docs.godotengine.org/en/stable/classes/class_gltfstate.html)。初次导入新 GLB 默认可能提取副本；不要把副本当作可编辑源。已有 sidecar 时不会重复提取。

## 仍需人工美术工作的部分

树冠分枝和叶卡分布有程序化规律；岩石只有两个基础变体；角色面罩、铠甲比例、金属磨损及动作仍需手工建模/UV/烘焙和骨骼动画。近地纹理仍可能显得细碎，远景与任意镜头边界需要继续打磨。正式生产资产要逐个审核后再替换旧地图，不能以三角形数量、纹理生成或渲染完成代替美术质量验收。
