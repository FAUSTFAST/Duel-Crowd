# 设计图轮廓候选（非正式成品）

用户设定图为唯一主要造型参考；图的版权归原权利人。新3D网格在本项目通过Blender建模，未使用第三方模型。此目录与旧wayfarer完全分开，默认无护甲/武器/盾牌。

source/blender/wayfarer.blend：146个可编辑源部件、32骨、五段Action、10张打包图。wayfarer.glb供Godot使用。equipment为已有接口的分离测试资源，默认不装备。

制作入口 tools/wayfarer/build_wayfarer.py -- --silhouette-study；形体配方 reference_surfaces.py。覆盖前保存手工更改；--replace-generated仅针对选中的输出目录。纹理仍沿用旧工作贴图，未完成最终绘制；没有新的高模烘焙。材质控制沿用旧wayfarer_materials，当前候选与旧贴图相同；进入细节阶段如独立绘图，需要单独配置材质路径。

详见 docs/silhouette_review/README.md。当前轮廓与面部仍有差距，不能作为正式角色验收完成。
