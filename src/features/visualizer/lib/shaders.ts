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
uniform float uBass, uKick, uSnare, uVoice, uGuitarL, uGuitarR, uFade;
uniform float uRippleRadius, uRippleAmp;
uniform float uFlow, uRibbons, uHalo, uRipple, uGrain, uSpeed;

vec2 mirror(vec2 x) { return 1.0 - abs(1.0 - mod(x, 2.0)); }
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

void main() {
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = (uv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
  float t = uTime * uSpeed;
  float r = length(p);

  float amp = uFlow * (0.02 + uBass * 0.035);
  vec2 q = p;
  q += amp * vec2(sin(q.y * 2.2 + t * 0.7), cos(q.x * 2.2 - t * 0.6));
  q += amp * 0.6 * vec2(sin(q.y * 4.1 - t * 0.5), cos(q.x * 3.7 + t * 0.4));
  q *= 1.0 - uKick * 0.015 * uRipple;

  vec3 col = texture(uCover, mirror(q + 0.5)).rgb;
  float lum = dot(col, vec3(0.299, 0.587, 0.114));
  col = mix(vec3(lum), col, 0.7);
  col = mix(col, col * mix(uC0, uC1, 0.5) * 1.6, 0.15);
  col *= 0.3;

  float edge = smoothstep(0.25, 1.0, r);
  col += uC1 * edge * (0.04 + uBass * 0.16);

  float ring = exp(-pow((r - uRippleRadius) * 7.0, 2.0)) * uRippleAmp * uRipple;
  col += mix(uC0, uC1, 0.5) * ring * 0.22;

  float halo = exp(-r * r * 2.6) * uVoice * uHalo;
  col += mix(uC0, vec3(1.0), 0.35) * halo * 0.2;

  float wl = 1.0 - smoothstep(-0.7, 0.1, p.x);
  float wr = smoothstep(-0.1, 0.7, p.x);
  float wave = sin(p.y * 5.0 + t * 1.1 + sin(p.x * 3.0 + t * 0.6) * 1.6);
  float ribbon = pow(0.5 + 0.5 * wave, 6.0);
  col += uC2 * ribbon * (wl * uGuitarL + wr * uGuitarR) * uRibbons * 0.3;

  float grain = hash(gl_FragCoord.xy + fract(uTime) * 100.0) - 0.5;
  col += grain * (0.012 + uSnare * 0.05 * uGrain);

  col = 1.0 - exp(-col * 1.4);
  col *= (0.55 + 0.45 * smoothstep(1.3, 0.2, r * 1.2)) * uFade;
  outColor = vec4(col, 1.0);
}`
