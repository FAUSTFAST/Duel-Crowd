# 原创像素细节纹理

64×64 PNG：granite（石块细裂纹）、flagstone（石板）、earth（泥土苔草斑块）、wood（木板）、bark（树皮）、grass（草叶）、leaves（针叶）、steel（金属板缝铆点）、cloth（织物），stone/road 保留旧砖纹生成样本。

PNG 使用中性亮度与少量苔藓色，最终颜色由对应 StandardMaterial3D 的统一色板调制；不是带烘焙光照的照片贴图。可直接在像素编辑器修改 PNG，游戏使用 Godot ResourceLoader 加载后缓存并生成 mipmap。近景最近邻、远景 mipmap；环境约 29–64 texel/m、角色约 96 texel/m。

生成源位于 scripts/rendering/pixel_materials.gd。tools/export_pixel_textures.gd 用于重新生成 PNG，执行会覆盖同名源纹理；手工编辑前提交 Git，不要随意重新运行生成器。

第四阶段使用曲边苔斑、低对比平滑土壤斑块、弯曲木纹/木结及磨损金属色阶，避免方块苔藓与强条带。新增 torch_flame.png 为256×32 RGBA、8个32px原创帧（火星/橙色边缘/金黄与浅色内核），使用透明裁切与最近邻，不生成mipmap。tools/export_environment_textures.gd 仅重生成granite/flagstone/earth/wood/leaves/steel与火焰图；不会改写其余五张PNG，执行前仍须提交手工改动。
