import { motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { formatClock } from '../../../shared/lib/time'
import { selectNowPlaying } from '../model/selectors'
import './ProgressBar.css'

export function ProgressBar() {
  const { position, duration, status } = useAppSelector(selectNowPlaying)
  const ratio = duration > 0 ? Math.min(position / duration, 1) : 0
  const tickSeconds = status === 'playing' ? 1 : 0.2

  return (
    <div className="progress">
      <div className="progress__track">
        <motion.div
          className="progress__fill"
          initial={false}
          animate={{ scaleX: ratio }}
          transition={{ duration: tickSeconds, ease: 'linear' }}
        />
      </div>
      <div className="progress__times">
        <span>{formatClock(position)}</span>
        <span>{formatClock(duration)}</span>
      </div>
    </div>
  )
}
