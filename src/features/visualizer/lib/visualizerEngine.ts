import { hexToRgb } from '../../../shared/lib/color'
import type { Rgb } from '../../../shared/lib/color'
import { audioLevels } from '../model/audioLevels'
import { paramsForGenre } from '../model/presets'
import type { VisualParams } from '../model/presets'
import { createCoverTexture, createProgram, uploadCover } from './gl'
import { PulsePool } from './pulses'
import { FRAGMENT_SHADER, VERTEX_SHADER } from './shaders'

const RENDER_SCALE = 0.75
const AUDIO_LIVE_MS = 1000
const FADE_IN_PER_SECOND = 0.8
const COLOR_EASE = 2
const PARAM_EASE = 1.5
const SLOW_EASE = 5
const FAST_EASE = 14
const BASS_AVERAGE_EASE = 1.2
const HIT_DECAY = 7
const CONTRAST = 2
const KICK_ONSET = 0.55
const SNARE_ONSET = 0.6
const BASS_ONSET_LEVEL = 0.7
const BASS_ONSET_RISE = 0.15
const BASS_COOLDOWN = 0.35

export interface VisualizerInputs {
  colors: [string, string, string, string]
  params: VisualParams
}

export interface VisualizerSource {
  read: () => VisualizerInputs
  takeImage: () => TexImageSource | null
}

const PARAM_KEYS: (keyof VisualParams)[] = ['flow', 'distort', 'halo', 'ripple', 'grain', 'speed']
const COLOR_UNIFORMS = ['uC0', 'uC1', 'uC2', 'uC3']

interface LiveAudio {
  bass: number
  kick: number
  snare: number
  voice: number
  guitarL: number
  guitarR: number
}

const IDLE_AUDIO: LiveAudio = { bass: 0.2, kick: 0, snare: 0, voice: 0.15, guitarL: 0, guitarR: 0 }

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
  const levels: LiveAudio = { ...IDLE_AUDIO }
  const pulses = new PulsePool()
  const previous = { kick: 0, snare: 0 }
  let bassAverage = 0
  let bassCooldown = 0
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
  }

  const readAudio = (now: number): LiveAudio =>
    now - audioLevels.updatedAt < AUDIO_LIVE_MS ? audioLevels : IDLE_AUDIO

  const easeAudio = (audio: LiveAudio, dt: number) => {
    const slow = Math.min(1, dt * SLOW_EASE)
    const fast = Math.min(1, dt * FAST_EASE)
    levels.bass += (audio.bass - levels.bass) * fast
    levels.voice += (audio.voice ** CONTRAST - levels.voice) * slow
    levels.guitarL += (audio.guitarL ** CONTRAST - levels.guitarL) * slow
    levels.guitarR += (audio.guitarR ** CONTRAST - levels.guitarR) * slow
    levels.kick = audio.kick
    levels.snare = audio.snare
  }

  const detectHits = (dt: number, aspect: number) => {
    if (levels.kick > KICK_ONSET && previous.kick <= KICK_ONSET) pulses.spawn(0, aspect)
    if (levels.snare > SNARE_ONSET && previous.snare <= SNARE_ONSET) pulses.spawn(1, aspect)
    previous.kick = levels.kick
    previous.snare = levels.snare

    bassCooldown = Math.max(0, bassCooldown - dt)
    const rising = levels.bass - bassAverage
    if (bassCooldown === 0 && levels.bass > BASS_ONSET_LEVEL && rising > BASS_ONSET_RISE) {
      pulses.spawn(2, aspect)
      bassCooldown = BASS_COOLDOWN
    }
    bassAverage += (levels.bass - bassAverage) * Math.min(1, dt * BASS_AVERAGE_EASE)
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

    resize()
    easeAudio(readAudio(now), dt)
    detectHits(dt, canvas.width / canvas.height)
    pulses.update(dt)
    const decay = Math.exp(-dt * HIT_DECAY)
    audioLevels.kick *= decay
    audioLevels.snare *= decay

    gl.uniform2f(uniform('uRes'), canvas.width, canvas.height)
    gl.uniform1f(uniform('uTime'), now / 1000)
    gl.uniform1f(uniform('uFade'), fade)
    gl.uniform1f(uniform('uBass'), levels.bass)
    gl.uniform1f(uniform('uVoice'), levels.voice)
    gl.uniform1f(uniform('uGuitarL'), levels.guitarL)
    gl.uniform1f(uniform('uGuitarR'), levels.guitarR)
    gl.uniform4fv(uniform('uPulses'), pulses.positions)
    gl.uniform1fv(uniform('uKinds'), pulses.kinds)
    gl.uniform1f(uniform('uFlow'), params.flow)
    gl.uniform1f(uniform('uDistort'), params.distort)
    gl.uniform1f(uniform('uHalo'), params.halo)
    gl.uniform1f(uniform('uRipple'), params.ripple)
    gl.uniform1f(uniform('uGrain'), params.grain)
    gl.uniform1f(uniform('uSpeed'), params.speed)
    COLOR_UNIFORMS.forEach((name, i) => gl.uniform3f(uniform(name), ...colors[i]))
    gl.drawArrays(gl.TRIANGLES, 0, 3)

    frameId = requestAnimationFrame(frame)
  }

  frameId = requestAnimationFrame(frame)
  return () => cancelAnimationFrame(frameId)
}
