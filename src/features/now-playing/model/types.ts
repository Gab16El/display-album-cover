export interface Palette {
  dominant: string
  vibrant: string
  muted: string
  dark: string
  text: string
  accents: string[]
}

export type PlaybackStatus = 'idle' | 'playing' | 'paused' | 'stopped'

export type ConnectionStatus = 'connecting' | 'online' | 'offline'

export interface BridgePayload {
  status: PlaybackStatus
  title: string
  artist: string
  album: string
  position: number
  duration: number
  coverVersion: string | null
  genre: string | null
  palette: Palette | null
}
