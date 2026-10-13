# 原创像素细节纹理

64×64 PNG：granite（石块细裂纹）、flagstone（石板）、earth（泥土苔草斑块）、wood（木板）、bark（树皮）、grass（草叶）、leaves（针叶）、steel（金属板缝铆点）、cloth（织物），stone/road 保留旧砖纹生成样本。

PNG 使用中性亮度与少量苔藓色，最终颜色由对应 StandardMaterial3D 的统一色板调制；不是带烘焙光照的照片贴图。可直接在像素编辑器修改 PNG，游戏使用 Godot ResourceLoader 加载后缓存并生成 mipmap。近景最近邻、远景 mipmap；环境约 29–64 texel/m、角色约 96 texel/m。

生成源位于 scripts/rendering/pixel_materials.gd。tools/export_pixel_textures.gd 用于重新生成 PNG，执行会覆盖同名源纹理；手工编辑前提交 Git，不要随意重新运行生成器。
