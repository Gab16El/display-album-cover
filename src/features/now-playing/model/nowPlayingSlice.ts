import { createAction, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import type { BridgePayload, ConnectionStatus } from './types'

export interface NowPlayingState extends BridgePayload {
  connection: ConnectionStatus
}

const initialState: NowPlayingState = {
  connection: 'connecting',
  status: 'idle',
  title: '',
  artist: '',
  album: '',
  position: 0,
  duration: 0,
  coverVersion: null,
  genre: null,
  palette: null,
}

export const bridgeSocketStarted = createAction('nowPlaying/bridgeSocketStarted')

const nowPlayingSlice = createSlice({
  name: 'nowPlaying',
  initialState,
  reducers: {
    connectionChanged(state, action: PayloadAction<ConnectionStatus>) {
      state.connection = action.payload
    },
    bridgeMessageReceived(_state, action: PayloadAction<BridgePayload>) {
      return { ...action.payload, connection: 'online' }
    },
  },
})

export const { connectionChanged, bridgeMessageReceived } = nowPlayingSlice.actions
export default nowPlayingSlice.reducer
