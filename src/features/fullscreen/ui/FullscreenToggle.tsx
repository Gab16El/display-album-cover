import { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../../../app/hooks'
import { fullscreenChanged } from '../model/fullscreenSlice'
import './FullscreenToggle.css'

export function FullscreenToggle() {
  const dispatch = useAppDispatch()
  const active = useAppSelector((state) => state.fullscreen.active)

  useEffect(() => {
    const sync = () => dispatch(fullscreenChanged(document.fullscreenElement !== null))
    document.addEventListener('fullscreenchange', sync)
    return () => document.removeEventListener('fullscreenchange', sync)
  }, [dispatch])

  const toggle = () => {
    if (document.fullscreenElement) void document.exitFullscreen()
    else void document.documentElement.requestFullscreen()
  }

  return (
    <button
      type="button"
      className="fullscreen-toggle"
      onClick={toggle}
      aria-label={active ? 'Salir de pantalla completa' : 'Pantalla completa'}
    >
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        {active ? (
          <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" />
        ) : (
          <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
        )}
      </svg>
    </button>
  )
}
