shader_type spatial;

uniform sampler2D soil_albedo : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D moss_albedo : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D slate_albedo : source_color, filter_nearest_mipmap, repeat_enable;
uniform sampler2D soil_normal : hint_normal, filter_nearest_mipmap, repeat_enable;
uniform sampler2D moss_normal : hint_normal, filter_nearest_mipmap, repeat_enable;
uniform sampler2D slate_normal : hint_normal, filter_nearest_mipmap, repeat_enable;
uniform sampler2D soil_roughness : filter_nearest_mipmap, repeat_enable;
uniform sampler2D moss_roughness : filter_nearest_mipmap, repeat_enable;
uniform sampler2D slate_roughness : filter_nearest_mipmap, repeat_enable;
uniform bool detail_enabled = true;

void fragment() {
	// Blender-authored weights: moss in red, steep exposed stone in green.
	float moss = clamp(COLOR.r, 0.0, 1.0);
	float rock = clamp(COLOR.g, 0.0, 1.0);
	vec3 weights = vec3(max(0.0, 1.0 - moss - rock), moss, rock);
	weights /= max(dot(weights, vec3(1.0)), 0.001);
	if (detail_enabled) {
		ALBEDO = texture(soil_albedo, UV).rgb * weights.x + texture(moss_albedo, UV).rgb * weights.y + texture(slate_albedo, UV).rgb * weights.z;
		NORMAL_MAP = texture(soil_normal, UV).rgb * weights.x + texture(moss_normal, UV).rgb * weights.y + texture(slate_normal, UV).rgb * weights.z;
		NORMAL_MAP_DEPTH = 0.45;
		ROUGHNESS = texture(soil_roughness, UV).r * weights.x + texture(moss_roughness, UV).r * weights.y + texture(slate_roughness, UV).r * weights.z;
	} else {
		NORMAL_MAP = vec3(0.5, 0.5, 1.0);
		NORMAL_MAP_DEPTH = 0.0;
		ALBEDO = vec3(0.21, 0.16, 0.11) * weights.x + vec3(0.16, 0.22, 0.10) * weights.y + vec3(0.28, 0.30, 0.29) * weights.z;
		ROUGHNESS = 0.9;
	}
}
