const bridgeHost: string = import.meta.env.VITE_BRIDGE_HOST ?? 'localhost:8765'

export const BRIDGE_WS_URL = `ws://${bridgeHost}/ws`
export const BRIDGE_AUDIO_WS_URL = `ws://${bridgeHost}/audio`
export const BRIDGE_HTTP_URL = `http://${bridgeHost}`
export const RECONNECT_DELAY_MS = 2000
