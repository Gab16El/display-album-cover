export const POOL_SIZE = 8

export type PulseKind = 0 | 1 | 2

interface Pulse {
  x: number
  y: number
  radius: number
  amp: number
  kind: PulseKind
  speed: number
  fade: number
  maxRadius: number
}

const KIND_SETTINGS: Record<PulseKind, { speed: number; fade: number; startRadius: number; maxRadius: number }> = {
  0: { speed: 0.9, fade: 1.4, startRadius: 0, maxRadius: 1.4 },
  1: { speed: 0.7, fade: 2.2, startRadius: 0, maxRadius: 0.6 },
  2: { speed: 0.35, fade: 0.9, startRadius: 0.1, maxRadius: 0.55 },
}

export class PulsePool {
  private pulses: Pulse[] = Array.from({ length: POOL_SIZE }, () => ({
    x: 0,
    y: 0,
    radius: 0,
    amp: 0,
    kind: 0 as PulseKind,
    speed: 0,
    fade: 0,
    maxRadius: 0,
  }))
  readonly positions = new Float32Array(POOL_SIZE * 4)
  readonly kinds = new Float32Array(POOL_SIZE)

  spawn(kind: PulseKind, aspect: number): void {
    const target = this.pulses.reduce((a, b) => (b.amp < a.amp ? b : a))
    const settings = KIND_SETTINGS[kind]
    target.x = (Math.random() - 0.5) * aspect * 0.95
    target.y = (Math.random() - 0.5) * 0.9
    target.radius = settings.startRadius
    target.amp = 1
    target.kind = kind
    target.speed = settings.speed
    target.fade = settings.fade
    target.maxRadius = settings.maxRadius
  }

  update(dt: number): void {
    this.pulses.forEach((pulse, i) => {
      pulse.radius = Math.min(pulse.maxRadius, pulse.radius + dt * pulse.speed)
      pulse.amp = Math.max(0, pulse.amp - dt * pulse.fade)
      this.positions.set([pulse.x, pulse.y, pulse.radius, pulse.amp], i * 4)
      this.kinds[i] = pulse.kind
    })
  }
}
