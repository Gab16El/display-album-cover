const SIZE = 256
const BLUR_PX = 22
const OVERSCAN = 1.25

export function blurCover(image: HTMLImageElement): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = SIZE
  canvas.height = SIZE
  const ctx = canvas.getContext('2d')!
  const drawn = SIZE * OVERSCAN
  const offset = (SIZE - drawn) / 2
  ctx.filter = `blur(${BLUR_PX}px)`
  ctx.drawImage(image, offset, offset, drawn, drawn)
  return canvas
}
