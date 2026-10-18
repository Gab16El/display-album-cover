import { motion } from 'motion/react'
import { useAppSelector } from '../../../app/hooks'
import './IdleState.css'

const MESSAGES = {
  connecting: { title: 'Conectando', hint: 'Buscando el puente local' },
  offline: { title: 'Puente desconectado', hint: 'Inicia el puente de Python en tu PC' },
  online: { title: 'Nada sonando', hint: 'Reproduce una cancion en Apple Music' },
} as const

export function IdleState() {
  const connection = useAppSelector((state) => state.nowPlaying.connection)
  const message = MESSAGES[connection]

  return (
    <motion.div
      className="idle"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="idle__pulse"
        animate={{ scale: [1, 1.25, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
      />
      <h1 className="idle__title">{message.title}</h1>
      <p className="idle__hint">{message.hint}</p>
    </motion.div>
  )
}
