import { AnimatePresence, motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { selectNowPlaying } from '../model/selectors'
import './TrackInfo.css'

const line = {
  hidden: { opacity: 0, y: 22, filter: 'blur(6px)' },
  show: { opacity: 1, y: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -14, filter: 'blur(6px)' },
}

export function TrackInfo() {
  const { title, artist, album } = useAppSelector(selectNowPlaying)

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`${title}|${artist}|${album}`}
        className="track"
        initial="hidden"
        animate="show"
        exit="exit"
        transition={{ staggerChildren: 0.09, duration: 0.55, ease: 'easeOut' }}
      >
        <motion.h1 className="track__title" variants={line}>{title}</motion.h1>
        <motion.p className="track__artist" variants={line}>{artist}</motion.p>
        <motion.p className="track__album" variants={line}>{album}</motion.p>
      </motion.div>
    </AnimatePresence>
  )
}
