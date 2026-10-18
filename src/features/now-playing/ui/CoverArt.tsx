import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useRef } from 'react'
import { useAppSelector } from '../../../app/hooks'
import { BRIDGE_HTTP_URL } from '../../../shared/config/env'
import { hexToRgb } from '../../../shared/lib/color'
import type { Rgb } from '../../../shared/lib/color'
import { audioLevels } from '../../audio-input/model/audioLevels'
import { selectCoverVersion, selectPalette } from '../model/selectors'
import './CoverArt.css'

const AUDIO_LIVE_MS = 1000
const VOICE_CONTRAST = 1.6
const VOICE_GAIN = 1.4
const VOICE_EASE = 6
const COLOR_EASE = 2
const IDLE_GLOW: Rgb = [0, 0, 0]

export function CoverArt() {
  const version = useAppSelector(selectCoverVersion)
  const palette = useAppSelector(selectPalette)
  const frameRef = useRef<HTMLDivElement>(null)
  const glowTarget = useRef<Rgb>(IDLE_GLOW)

  useEffect(() => {
    glowTarget.current = palette ? hexToRgb(palette.vibrant) : IDLE_GLOW
  }, [palette])

  useEffect(() => {
    const color: Rgb = [...glowTarget.current]
    let voice = 0
    let last = performance.now()
    let frameId = 0

    const tick = (now: number) => {
      const dt = Math.min((now - last) / 1000, 0.1)
      last = now
      const live = now - audioLevels.updatedAt < AUDIO_LIVE_MS
      const target = live ? Math.min(1, audioLevels.voice ** VOICE_CONTRAST * VOICE_GAIN) : 0
      voice += (target - voice) * Math.min(1, dt * VOICE_EASE)
      for (let c = 0; c < 3; c++) color[c] += (glowTarget.current[c] - color[c]) * Math.min(1, dt * COLOR_EASE)
      const [r, g, b] = color.map((v) => Math.round(v * 255))
      const rgb = `${r} ${g} ${b}`
      if (frameRef.current) {
        frameRef.current.style.boxShadow =
          `0 0 ${24 + 36 * voice}px ${2 + 8 * voice}px rgb(${rgb} / ${0.45 + 0.5 * voice}), ` +
          `0 0 ${90 + 150 * voice}px ${12 + 36 * voice}px rgb(${rgb} / ${0.4 + 0.6 * voice}), ` +
          '0 14px 40px rgb(0 0 0 / 0.45)'
      }
      frameId = requestAnimationFrame(tick)
    }

    frameId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frameId)
  }, [])

  return (
    <div className="cover" ref={frameRef}>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.img
          key={version ?? 'empty'}
          className="cover__image"
          src={version ? `${BRIDGE_HTTP_URL}/cover?v=${version}` : undefined}
          alt=""
          initial={{ opacity: 0, scale: 1.08, rotate: -2 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          exit={{ opacity: 0, scale: 0.94, rotate: 2 }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        />
      </AnimatePresence>
    </div>
  )
}
