import { configureStore } from '@reduxjs/toolkit'
import { bridgeSocketMiddleware } from '../features/now-playing/api/bridgeSocketMiddleware'
import nowPlaying from '../features/now-playing/model/nowPlayingSlice'
import fullscreen from '../features/fullscreen/model/fullscreenSlice'

export const store = configureStore({
  reducer: { nowPlaying, fullscreen },
  middleware: (getDefault) => getDefault().concat(bridgeSocketMiddleware),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
