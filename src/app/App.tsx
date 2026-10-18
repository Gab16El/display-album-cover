import { useEffect } from 'react'
import { AmbientBackground } from '../features/ambient-background/ui/AmbientBackground'
import { FullscreenToggle } from '../features/fullscreen/ui/FullscreenToggle'
import { bridgeSocketStarted } from '../features/now-playing/model/nowPlayingSlice'
import { NowPlayingScreen } from '../features/now-playing/ui/NowPlayingScreen'
import { useAppDispatch } from './hooks'

export default function App() {
  const dispatch = useAppDispatch()

  useEffect(() => {
    dispatch(bridgeSocketStarted())
  }, [dispatch])

  return (
    <>
      <AmbientBackground />
      <NowPlayingScreen />
      <FullscreenToggle />
    </>
  )
}
