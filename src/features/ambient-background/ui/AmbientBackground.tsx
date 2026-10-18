import { motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { selectPalette } from '../../now-playing/model/selectors'
import './AmbientBackground.css'

const FALLBACK = { dominant: '#1c1c24', vibrant: '#2a2a3a', dark: '#0b0b10' }
const COLOR_TRANSITION = { duration: 1.6, ease: 'easeInOut' } as const

const blobs = [
  { key: 'dominant', size: '70vmax', x: [-12, 10, -12], y: [-8, 12, -8], top: '-20%', left: '-15%' },
  { key: 'vibrant', size: '60vmax', x: [8, -14, 8], y: [10, -10, 10], top: '30%', left: '40%' },
  { key: 'dark', size: '55vmax', x: [-6, 12, -6], y: [-12, 6, -12], top: '50%', left: '-20%' },
] as const

export function AmbientBackground() {
  const palette = useAppSelector(selectPalette) ?? FALLBACK

  return (
    <motion.div
      className="ambient"
      animate={{ backgroundColor: palette.dark }}
      transition={COLOR_TRANSITION}
    >
      {blobs.map((blob, index) => (
        <motion.div
          key={blob.key}
          className="ambient__blob"
          style={{ width: blob.size, height: blob.size, top: blob.top, left: blob.left }}
          animate={{
            backgroundColor: palette[blob.key],
            x: `${blob.x[1]}%`,
            y: `${blob.y[1]}%`,
          }}
          transition={{
            backgroundColor: COLOR_TRANSITION,
            x: { duration: 18 + index * 4, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' },
            y: { duration: 22 + index * 3, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' },
          }}
        />
      ))}
      <div className="ambient__grain" />
    </motion.div>
  )
}
