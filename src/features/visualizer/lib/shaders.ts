export const VERTEX_SHADER = `#version 300 es
void main() {
  vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`

export const FRAGMENT_SHADER = `#version 300 es
precision highp float;
out vec4 outColor;

uniform vec2 uRes;
uniform float uTime;
uniform sampler2D uCover;
uniform vec3 uC0, uC1, uC2, uC3;
uniform float uBass, uKick, uSnare, uFade;
uniform float uWarp, uKaleido, uSwirl, uSpeed, uBlur, uGrade;

vec2 mirror(vec2 x) { return 1.0 - abs(1.0 - mod(x, 2.0)); }

vec3 cover(vec2 p) { return textureLod(uCover, mirror(p + 0.5), uBlur).rgb; }

void main() {
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = (uv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
  float t = uTime * uSpeed;

  if (uKaleido > 1.5) {
    float seg = 6.2831853 / floor(uKaleido);
    float a = atan(p.y, p.x) + t * 0.1;
    a = abs(mod(a, seg) - seg * 0.5);
    p = length(p) * vec2(cos(a), sin(a));
  }

  float amp = uWarp * (0.1 + uBass * 0.2 + uKick * 0.3);
  vec2 q = p;
  for (int i = 0; i < 3; i++) {
    float fi = float(i);
    q += amp * vec2(sin(q.y * 3.0 + t + fi * 1.7), cos(q.x * 3.0 - t * 1.1 + fi * 2.3));
  }

  float swirl = uSwirl * (0.4 + uBass * 0.8 + uSnare * 0.4) * exp(-length(q) * 1.2) * sin(t * 0.6);
  float cs = cos(swirl);
  float sn = sin(swirl);
  q = mat2(cs, -sn, sn, cs) * q;

  vec2 tuv = q * (0.9 - uKick * 0.07);
  float ab = 0.004 + uSnare * 0.02;
  vec3 col = vec3(
    cover(tuv + vec2(ab, 0.0)).r,
    cover(tuv).g,
    cover(tuv - vec2(ab, 0.0)).b
  );

  float lum = dot(col, vec3(0.299, 0.587, 0.114));
  vec3 ramp = mix(uC3, mix(uC0, uC1, smoothstep(0.35, 0.8, lum)), smoothstep(0.05, 0.5, lum));
  col = mix(col, ramp * (0.6 + lum), uGrade);
  col += mix(uC1, uC2, 0.5) * (uKick * 0.14 + uSnare * 0.1);

  float vig = smoothstep(1.25, 0.25, length(uv - 0.5) * 1.5);
  col *= (0.35 + 0.4 * vig) * uFade;
  outColor = vec4(col, 1.0);
}`
