import { AnimatePresence, motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { selectHasTrack } from '../model/selectors'
import { CoverArt } from './CoverArt'
import { IdleState } from './IdleState'
import { ProgressBar } from './ProgressBar'
import { TrackInfo } from './TrackInfo'
import './NowPlayingScreen.css'

export function NowPlayingScreen() {
  const hasTrack = useAppSelector(selectHasTrack)

  return (
    <main className="screen">
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
    </main>
  )
}
