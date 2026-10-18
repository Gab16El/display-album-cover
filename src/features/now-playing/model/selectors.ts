import type { RootState } from '../../../app/store'

export const selectNowPlaying = (state: RootState) => state.nowPlaying
export const selectPalette = (state: RootState) => state.nowPlaying.palette
export const selectCoverVersion = (state: RootState) => state.nowPlaying.coverVersion
export const selectHasTrack = (state: RootState) =>
  state.nowPlaying.connection === 'online' && state.nowPlaying.title !== ''
