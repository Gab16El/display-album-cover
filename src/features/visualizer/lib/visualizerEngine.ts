import { hexToRgb } from '../../../shared/lib/color'
import type { Rgb } from '../../../shared/lib/color'
import { audioLevels } from '../model/audioLevels'
import { paramsForGenre } from '../model/presets'
import type { VisualParams } from '../model/presets'
import { createCoverTexture, createProgram, uploadCover } from './gl'
import { FRAGMENT_SHADER, VERTEX_SHADER } from './shaders'

const RENDER_SCALE = 0.5
const AUDIO_LIVE_MS = 1000
const FADE_IN_PER_SECOND = 0.8
const COLOR_EASE = 2
const PARAM_EASE = 1.5
const AUDIO_EASE = 14
const BEAT_DECAY = 6

export interface VisualizerInputs {
  colors: [string, string, string, string]
  params: VisualParams
}

export interface VisualizerSource {
  read: () => VisualizerInputs
  takeImage: () => HTMLImageElement | null
}

const PARAM_KEYS: (keyof VisualParams)[] = ['warp', 'swirl', 'speed', 'blur', 'grade']
const COLOR_UNIFORMS = ['uC0', 'uC1', 'uC2', 'uC3']

export function startVisualizer(canvas: HTMLCanvasElement, source: VisualizerSource): (() => void) | null {
  const gl = canvas.getContext('webgl2', { antialias: false, alpha: false })
  if (!gl) return null

  let program: WebGLProgram
  try {
    program = createProgram(gl, VERTEX_SHADER, FRAGMENT_SHADER)
  } catch (error) {
    console.error('visualizer disabled:', error)
    return null
  }
  gl.useProgram(program)
  const uniform = (name: string) => gl.getUniformLocation(program, name)
  const texture = createCoverTexture(gl)
  gl.activeTexture(gl.TEXTURE0)
  gl.uniform1i(uniform('uCover'), 0)

  const colors: Rgb[] = [0, 1, 2, 3].map(() => [0.04, 0.04, 0.06] as Rgb)
  const params: VisualParams = { ...paramsForGenre(null) }
  const levels = { bass: 0, mid: 0, treble: 0 }
  let fade = 0
  let last = performance.now()
  let frameId = 0

  const resize = () => {
    const width = Math.max(2, Math.floor(canvas.clientWidth * RENDER_SCALE))
    const height = Math.max(2, Math.floor(canvas.clientHeight * RENDER_SCALE))
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }
    gl.viewport(0, 0, width, height)
  }

  const easeColors = (targets: string[], k: number) => {
    targets.forEach((hex, i) => {
      const target = hexToRgb(hex)
      for (let c = 0; c < 3; c++) colors[i][c] += (target[c] - colors[i][c]) * k
    })
  }

  const easeParams = (target: VisualParams, k: number) => {
    for (const key of PARAM_KEYS) params[key] += (target[key] - params[key]) * k
    params.kaleido = target.kaleido
  }

  const readAudio = (now: number) => {
    const live = now - audioLevels.updatedAt < AUDIO_LIVE_MS
    const t = now / 1000
    return live
      ? audioLevels
      : { bass: 0.2 + 0.1 * Math.sin(t * 1.2), mid: 0.3, treble: 0.2, beat: 0 }
  }

  const frame = (now: number) => {
    const dt = Math.min((now - last) / 1000, 0.1)
    last = now

    const image = source.takeImage()
    if (image) {
      uploadCover(gl, texture, image)
      fade = 0
    }
    fade = Math.min(1, fade + dt * FADE_IN_PER_SECOND)

    const inputs = source.read()
    easeColors(inputs.colors, Math.min(1, dt * COLOR_EASE))
    easeParams(inputs.params, Math.min(1, dt * PARAM_EASE))

    const audio = readAudio(now)
    const audioK = Math.min(1, dt * AUDIO_EASE)
    levels.bass += (audio.bass - levels.bass) * audioK
    levels.mid += (audio.mid - levels.mid) * audioK
    levels.treble += (audio.treble - levels.treble) * audioK
    audioLevels.beat *= Math.exp(-dt * BEAT_DECAY)

    resize()
    gl.uniform2f(uniform('uRes'), canvas.width, canvas.height)
    gl.uniform1f(uniform('uTime'), now / 1000)
    gl.uniform1f(uniform('uBass'), levels.bass)
    gl.uniform1f(uniform('uMid'), levels.mid)
    gl.uniform1f(uniform('uTreble'), levels.treble)
    gl.uniform1f(uniform('uBeat'), audioLevels.beat)
    gl.uniform1f(uniform('uFade'), fade)
    gl.uniform1f(uniform('uWarp'), params.warp)
    gl.uniform1f(uniform('uKaleido'), params.kaleido)
    gl.uniform1f(uniform('uSwirl'), params.swirl)
    gl.uniform1f(uniform('uSpeed'), params.speed)
    gl.uniform1f(uniform('uBlur'), params.blur)
    gl.uniform1f(uniform('uGrade'), params.grade)
    COLOR_UNIFORMS.forEach((name, i) => gl.uniform3f(uniform(name), ...colors[i]))
    gl.drawArrays(gl.TRIANGLES, 0, 3)

    frameId = requestAnimationFrame(frame)
  }

  frameId = requestAnimationFrame(frame)
  return () => cancelAnimationFrame(frameId)
}
