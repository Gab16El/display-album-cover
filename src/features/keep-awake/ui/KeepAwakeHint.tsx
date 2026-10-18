import NoSleep from 'nosleep.js'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../../../app/hooks'
import { keepAwakeChanged } from '../model/keepAwakeSlice'
import './KeepAwakeHint.css'

const noSleep = new NoSleep()
const IS_TOUCH_DEVICE = window.matchMedia('(pointer: coarse)').matches

export function KeepAwakeHint() {
  const dispatch = useAppDispatch()
  const active = useAppSelector((state) => state.keepAwake.active)

  useEffect(() => {
    if (active) return

    let cancelled = false
    const tryEnable = () =>
      noSleep
        .enable()
        .then(() => {
          if (!cancelled) dispatch(keepAwakeChanged(true))
        })
        .catch(() => undefined)

    void tryEnable()
    document.addEventListener('pointerup', tryEnable)
    return () => {
      cancelled = true
      document.removeEventListener('pointerup', tryEnable)
    }
  }, [active, dispatch])

  return (
    <AnimatePresence>
      {!active && IS_TOUCH_DEVICE && (
        <motion.p
          className="keep-awake-hint"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: [0.55, 1, 0.55], y: 0 }}
          exit={{ opacity: 0, y: 10, transition: { duration: 0.3 } }}
          transition={{ opacity: { duration: 2.4, repeat: Infinity }, y: { duration: 0.4 } }}
        >
          Toca la pantalla una vez para que no se apague
        </motion.p>
      )}
    </AnimatePresence>
  )
}
