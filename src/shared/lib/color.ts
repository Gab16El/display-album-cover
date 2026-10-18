export type Rgb = [number, number, number]

export function hexToRgb(hex: string): Rgb {
  const value = parseInt(hex.replace('#', ''), 16)
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255].map((c) => c / 255) as Rgb
}
