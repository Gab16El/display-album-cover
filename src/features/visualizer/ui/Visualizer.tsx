import { useEffect, useRef } from 'react'
import { useAppSelector } from '../../../app/hooks'
import { BRIDGE_HTTP_URL } from '../../../shared/config/env'
import { selectCoverVersion, selectGenre, selectPalette } from '../../now-playing/model/selectors'
import type { Palette } from '../../now-playing/model/types'
import { connectAudioSocket } from '../api/audioSocket'
import { blurCover } from '../lib/blurCover'
import { startVisualizer } from '../lib/visualizerEngine'
import type { VisualizerInputs } from '../lib/visualizerEngine'
import { paramsForGenre } from '../model/presets'
import './Visualizer.css'

const FALLBACK_COLORS: VisualizerInputs['colors'] = ['#1c1c24', '#2a2a3a', '#232333', '#0b0b10']

function colorsFromPalette(palette: Palette | null): VisualizerInputs['colors'] {
  if (!palette) return FALLBACK_COLORS
  return [palette.dominant, palette.vibrant, palette.muted, palette.dark]
}

export function Visualizer() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const palette = useAppSelector(selectPalette)
  const genre = useAppSelector(selectGenre)
  const coverVersion = useAppSelector(selectCoverVersion)
  const inputsRef = useRef<VisualizerInputs>({ colors: FALLBACK_COLORS, params: paramsForGenre(null) })
  const imageRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    inputsRef.current = { colors: colorsFromPalette(palette), params: paramsForGenre(genre) }
  }, [palette, genre])

  useEffect(() => {
    if (!coverVersion) return
    const image = new Image()
    image.crossOrigin = 'anonymous'
    image.onload = () => {
      imageRef.current = blurCover(image)
    }
    image.src = `${BRIDGE_HTTP_URL}/cover?v=${coverVersion}`
    return () => {
      image.onload = null
    }
  }, [coverVersion])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const stop = startVisualizer(canvas, {
      read: () => inputsRef.current,
      takeImage: () => {
        const image = imageRef.current
        imageRef.current = null
        return image
      },
    })
    const disconnect = connectAudioSocket()
    return () => {
      stop?.()
      disconnect()
    }
  }, [])

  return <canvas ref={canvasRef} className="visualizer" />
}
