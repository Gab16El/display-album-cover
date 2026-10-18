export const VERTEX_SHADER = `#version 300 es
void main() {
  vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`

export const FRAGMENT_SHADER = `#version 300 es
precision highp float;
out vec4 outColor;

#define PULSES 8

uniform vec2 uRes;
uniform float uTime;
uniform sampler2D uCover;
uniform vec3 uC0, uC1, uC2, uC3;
uniform float uBass, uVoice, uGuitarL, uGuitarR, uFade;
uniform vec4 uPulses[PULSES];
uniform float uKinds[PULSES];
uniform float uFlow, uDistort, uHalo, uRipple, uGrain, uSpeed;

vec2 mirror(vec2 x) { return 1.0 - abs(1.0 - mod(x, 2.0)); }
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

vec3 cover(vec2 p) { return texture(uCover, mirror(p + 0.5)).rgb; }

void main() {
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = (uv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
  float t = uTime * uSpeed;
  float r = length(p);

  float wl = 1.0 - smoothstep(-0.45, 0.45, p.x);
  float dist = uDistort * (wl * uGuitarL + (1.0 - wl) * uGuitarR);

  float amp = uFlow * (0.02 + uBass * 0.03) + dist * 0.16;
  vec2 q = p;
  q += amp * vec2(sin(q.y * 2.2 + t * 0.7), cos(q.x * 2.2 - t * 0.6));
  q += amp * 0.7 * vec2(sin(q.y * 4.6 - t * 0.9 + q.x * 2.0), cos(q.x * 4.1 + t * 0.8 - q.y * 2.0));
  float twist = dist * 0.9 * exp(-r * 1.1) * sin(t * 0.8);
  float cs = cos(twist);
  float sn = sin(twist);
  q = mat2(cs, -sn, sn, cs) * q;

  for (int i = 0; i < PULSES; i++) {
    vec4 pulse = uPulses[i];
    if (pulse.w <= 0.0) continue;
    vec2 away = p - pulse.xy;
    float d = length(away);
    vec2 dir = away / max(d, 0.0001);
    if (uKinds[i] < 0.5) {
      q -= dir * exp(-pow((d - pulse.z) * 6.0, 2.0)) * pulse.w * 0.07 * uRipple;
    } else if (uKinds[i] < 1.5) {
      q -= dir * exp(-pow((d - pulse.z) * 14.0, 2.0)) * pulse.w * 0.035 * uRipple;
    } else {
      q -= away * exp(-d * d / (pulse.z * pulse.z + 0.02)) * pulse.w * 0.35 * uRipple;
    }
  }

  float ab = 0.002 + dist * 0.014;
  vec3 col = vec3(cover(q + vec2(ab, 0.0)).r, cover(q).g, cover(q - vec2(ab, 0.0)).b);
  float lum = dot(col, vec3(0.299, 0.587, 0.114));
  col = mix(vec3(lum), col, 0.7);
  col = mix(col, col * mix(uC0, uC1, 0.5) * 1.6, 0.15);
  col *= 0.3;

  float edge = smoothstep(0.25, 1.0, r);
  col += uC1 * edge * (0.04 + uBass * 0.12);

  float halo = exp(-r * r * 2.6) * uVoice * uHalo;
  col += mix(uC0, vec3(1.0), 0.35) * halo * 0.2;

  float grain = hash(gl_FragCoord.xy + fract(uTime) * 100.0) - 0.5;
  col += grain * (0.008 + uGrain * 0.02);

  col = 1.0 - exp(-col * 1.4);
  col *= (0.55 + 0.45 * smoothstep(1.3, 0.2, r * 1.2)) * uFade;
  outColor = vec4(col, 1.0);
}`
