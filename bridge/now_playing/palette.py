import colorsys
import io
import math

from PIL import Image

from .track import Palette

SAMPLE_SIZE = 64
QUANT_COLORS = 16
MIN_DISTANCE = 70
MIN_DARK_AREA = 0.02

RGB = tuple[int, int, int]


def _hex(rgb: RGB) -> str:
    return "#%02x%02x%02x" % rgb


def _luma(rgb: RGB) -> float:
    r, g, b = rgb
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _saturation(rgb: RGB) -> float:
    return colorsys.rgb_to_hsv(*(c / 255 for c in rgb))[1]


def _distance(a: RGB, b: RGB) -> float:
    return math.dist(a, b)


def _weighted_colors(image_bytes: bytes) -> list[tuple[RGB, float]]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((SAMPLE_SIZE, SAMPLE_SIZE))
    quant = img.quantize(colors=QUANT_COLORS, method=Image.Quantize.MEDIANCUT)
    pal = quant.getpalette() or []
    total = SAMPLE_SIZE * SAMPLE_SIZE
    return [(tuple(pal[i * 3 : i * 3 + 3]), count / total) for count, i in quant.getcolors() or []]


def _score(rgb: RGB, area: float) -> float:
    brightness = min(_luma(rgb), 0.85)
    return (area**0.5) * (0.15 + _saturation(rgb)) * (0.25 + brightness)


def _distinct_accents(weighted: list[tuple[RGB, float]], limit: int = 4) -> list[RGB]:
    ranked = sorted(weighted, key=lambda item: _score(*item), reverse=True)
    accents: list[RGB] = []
    for rgb, _ in ranked:
        if all(_distance(rgb, other) >= MIN_DISTANCE for other in accents):
            accents.append(rgb)
        if len(accents) == limit:
            break
    return accents


def extract_palette(image_bytes: bytes) -> Palette:
    weighted = _weighted_colors(image_bytes)
    accents = _distinct_accents(weighted)
    dominant = accents[0]
    vibrant = max(accents, key=lambda c: _saturation(c) * (0.2 + _luma(c)))
    muted = next((c for c in accents if c not in (dominant, vibrant)), dominant)
    solid = [c for c, area in weighted if area >= MIN_DARK_AREA] or [c for c, _ in weighted]
    dark = min(solid, key=_luma)
    text = "#0b0b0f" if _luma(dominant) > 0.6 else "#f5f5f7"
    return Palette(
        dominant=_hex(dominant),
        vibrant=_hex(vibrant),
        muted=_hex(muted),
        dark=_hex(dark),
        text=text,
        accents=tuple(_hex(c) for c in accents),
    )
