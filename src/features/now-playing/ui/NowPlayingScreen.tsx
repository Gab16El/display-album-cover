import { AnimatePresence, motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { selectHasTrack, selectPalette } from '../model/selectors'
import { CoverArt } from './CoverArt'
import { IdleState } from './IdleState'
import { ProgressBar } from './ProgressBar'
import { TrackInfo } from './TrackInfo'
import './NowPlayingScreen.css'

export function NowPlayingScreen() {
  const hasTrack = useAppSelector(selectHasTrack)
  const palette = useAppSelector(selectPalette)

  return (
    <motion.main
      className="screen"
      animate={{ color: palette?.text ?? '#f5f5f7' }}
      transition={{ duration: 1.2 }}
    >
      <AnimatePresence mode="wait">
        {hasTrack ? (
          <motion.section
            key="playing"
            className="screen__player"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <CoverArt />
            <div className="screen__details">
              <TrackInfo />
              <ProgressBar />
            </div>
          </motion.section>
        ) : (
          <IdleState key="idle" />
        )}
      </AnimatePresence>
    </motion.main>
  )
}
