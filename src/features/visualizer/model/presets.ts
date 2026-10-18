export interface VisualParams {
  flow: number
  distort: number
  wave: number
  halo: number
  ripple: number
  grain: number
  speed: number
}

const PSYCHEDELIC: VisualParams = { flow: 0.9, distort: 1.0, wave: 1.0, halo: 0.8, ripple: 0.7, grain: 0.5, speed: 0.6 }
const HEAVY: VisualParams = { flow: 1.0, distort: 1.2, wave: 1.2, halo: 0.6, ripple: 1.2, grain: 0.9, speed: 0.9 }
const ELECTRONIC: VisualParams = { flow: 0.5, distort: 0.5, wave: 1.3, halo: 0.5, ripple: 1.3, grain: 0.8, speed: 1.0 }
const HIPHOP: VisualParams = { flow: 0.5, distort: 0.3, wave: 0.8, halo: 1.0, ripple: 1.2, grain: 0.6, speed: 0.6 }
const POP: VisualParams = { flow: 0.6, distort: 0.6, wave: 0.8, halo: 1.0, ripple: 0.8, grain: 0.4, speed: 0.6 }
const CALM: VisualParams = { flow: 0.3, distort: 0.5, wave: 0.4, halo: 0.9, ripple: 0.3, grain: 0.2, speed: 0.3 }
const DEFAULT: VisualParams = { flow: 0.6, distort: 0.7, wave: 0.7, halo: 0.8, ripple: 0.7, grain: 0.4, speed: 0.5 }

const RULES: [RegExp, VisualParams][] = [
  [/metal|hard rock|punk|grunge/i, HEAVY],
  [/psychedelic|alternative|indie|rock|shoegaze/i, PSYCHEDELIC],
  [/electronic|dance|house|techno|trance|edm/i, ELECTRONIC],
  [/hip-hop|rap|r&b|soul|trap/i, HIPHOP],
  [/pop|k-pop|latin/i, POP],
  [/jazz|classical|acoustic|folk|singer|country|ambient|new age|blues/i, CALM],
]

export function paramsForGenre(genre: string | null): VisualParams {
  if (!genre) return DEFAULT
  return RULES.find(([pattern]) => pattern.test(genre))?.[1] ?? DEFAULT
}
