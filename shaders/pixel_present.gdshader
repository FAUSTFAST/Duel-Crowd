shader_type canvas_item;
render_mode unshaded;
// Sample texel centres explicitly; presentation never blends neighboring pixels.
void fragment() {
	vec2 dimensions = vec2(textureSize(TEXTURE, 0));
	vec2 texel_uv = (floor(UV * dimensions) + 0.5) / dimensions;
	COLOR = texture(TEXTURE, texel_uv);
}
