import { BRIDGE_AUDIO_WS_URL, RECONNECT_DELAY_MS } from '../../../shared/config/env'
import { audioLevels } from '../model/audioLevels'

interface AudioMessage {
  bass: number
  kick: number
  snare: number
  level: number
}

export function connectAudioSocket(): () => void {
  let socket: WebSocket | null = null
  let retryTimer: number | undefined
  let closed = false

  const connect = () => {
    socket = new WebSocket(BRIDGE_AUDIO_WS_URL)
    socket.onmessage = (event: MessageEvent<string>) => {
      const data = JSON.parse(event.data) as AudioMessage
      audioLevels.bass = data.bass
      audioLevels.kick = Math.max(data.kick, audioLevels.kick)
      audioLevels.snare = Math.max(data.snare, audioLevels.snare)
      audioLevels.level = data.level
      audioLevels.updatedAt = performance.now()
    }
    socket.onclose = () => {
      if (!closed) retryTimer = window.setTimeout(connect, RECONNECT_DELAY_MS)
    }
  }

  connect()

  return () => {
    closed = true
    window.clearTimeout(retryTimer)
    socket?.close()
  }
}
