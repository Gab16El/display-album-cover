import { configureStore } from '@reduxjs/toolkit'
import { bridgeSocketMiddleware } from '../features/now-playing/api/bridgeSocketMiddleware'
import nowPlaying from '../features/now-playing/model/nowPlayingSlice'
import fullscreen from '../features/fullscreen/model/fullscreenSlice'
import keepAwake from '../features/keep-awake/model/keepAwakeSlice'

export const store = configureStore({
  reducer: { nowPlaying, fullscreen, keepAwake },
  middleware: (getDefault) => getDefault().concat(bridgeSocketMiddleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
