import { useId } from 'react'

const SHAPE =
  'M18 12H46Q52 12 52 18C52 24 58 26 58 32C58 38 52 40 52 46Q52 52 46 52H18Q12 52 12 46V18Q12 12 18 12Z'

interface BrandMarkProps {
  width?: number
}

export function BrandMark({ width = 64 }: BrandMarkProps) {
  const uid = useId().replace(/:/g, '')
  const mask = `${uid}-ripple`
  const gradient = `${uid}-iridescent`

  return (
    <svg viewBox="8 8 52 48" width={width} height={(width * 48) / 52} aria-hidden="true">
      <defs>
        <mask id={mask} maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">
          <rect width="64" height="64" fill="#fff" />
          <g fill="none" stroke="#000" strokeWidth="3.5">
            <circle cx="36" cy="32" r="7" />
            <circle cx="36" cy="32" r="14" />
          </g>
          <circle cx="36" cy="32" r="2.6" fill="#000" />
        </mask>
        <linearGradient id={gradient} gradientUnits="userSpaceOnUse" x1="10" y1="54" x2="54" y2="10">
          <stop offset="0" stopColor="#ff5a3c" />
          <stop offset="0.5" stopColor="#8a5cff" />
          <stop offset="1" stopColor="#3d8bff" />
        </linearGradient>
      </defs>
      <path d={SHAPE} fill={`url(#${gradient})`} mask={`url(#${mask})`} />
    </svg>
  )
}
