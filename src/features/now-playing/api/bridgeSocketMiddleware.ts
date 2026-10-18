import type { Middleware } from '@reduxjs/toolkit'
import { BRIDGE_WS_URL, RECONNECT_DELAY_MS } from '../../../shared/config/env'
import {
  bridgeMessageReceived,
  bridgeSocketStarted,
  connectionChanged,
} from '../model/nowPlayingSlice'
import type { BridgePayload } from '../model/types'

export const bridgeSocketMiddleware: Middleware = (api) => {
  let socket: WebSocket | null = null
  let retryTimer: number | undefined

  const connect = () => {
    window.clearTimeout(retryTimer)
    socket = new WebSocket(BRIDGE_WS_URL)

    socket.onopen = () => api.dispatch(connectionChanged('online'))
    socket.onmessage = (event: MessageEvent<string>) => {
      api.dispatch(bridgeMessageReceived(JSON.parse(event.data) as BridgePayload))
    }
    socket.onclose = () => {
      api.dispatch(connectionChanged('offline'))
      retryTimer = window.setTimeout(connect, RECONNECT_DELAY_MS)
    }
  }

  return (next) => (action) => {
    if (bridgeSocketStarted.match(action) && !socket) connect()
    return next(action)
  }
}
