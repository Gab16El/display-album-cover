import { AnimatePresence, motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import { BRIDGE_HTTP_URL } from '../../../shared/config/env'
import { selectCoverVersion, selectPalette } from '../model/selectors'
import './CoverArt.css'

export function CoverArt() {
  const version = useAppSelector(selectCoverVersion)
  const palette = useAppSelector(selectPalette)
  const glow = palette?.vibrant ?? '#000000'

  return (
    <motion.div
      className="cover"
      animate={{ boxShadow: `0 40px 120px -20px ${glow}aa, 0 10px 30px rgb(0 0 0 / 0.4)` }}
      transition={{ duration: 1.2 }}
    >
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
    </motion.div>
  )
}
