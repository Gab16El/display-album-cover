export interface VisualParams {
  warp: number
  kaleido: number
  swirl: number
  speed: number
  blur: number
  grade: number
}

const PSYCHEDELIC: VisualParams = { warp: 1.0, kaleido: 0, swirl: 1.1, speed: 0.6, blur: 3, grade: 0.25 }
const HEAVY: VisualParams = { warp: 1.3, kaleido: 0, swirl: 1.5, speed: 1.0, blur: 2.5, grade: 0.35 }
const ELECTRONIC: VisualParams = { warp: 0.5, kaleido: 6, swirl: 0.5, speed: 1.0, blur: 2.5, grade: 0.5 }
const HIPHOP: VisualParams = { warp: 0.55, kaleido: 0, swirl: 0.3, speed: 0.7, blur: 3, grade: 0.4 }
const POP: VisualParams = { warp: 0.6, kaleido: 8, swirl: 0.4, speed: 0.6, blur: 4, grade: 0.3 }
const CALM: VisualParams = { warp: 0.25, kaleido: 0, swirl: 0.2, speed: 0.3, blur: 5, grade: 0.15 }
const DEFAULT: VisualParams = { warp: 0.5, kaleido: 0, swirl: 0.5, speed: 0.5, blur: 3.5, grade: 0.25 }

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
