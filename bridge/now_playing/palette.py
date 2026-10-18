import colorsys
import io

from PIL import Image

from .track import Palette


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def _luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _saturation(rgb: tuple[int, int, int]) -> float:
    r, g, b = (c / 255 for c in rgb)
    return colorsys.rgb_to_hsv(r, g, b)[1]


def _ranked_colors(image_bytes: bytes, count: int = 8) -> list[tuple[int, int, int]]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((96, 96))
    quant = img.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    pal = quant.getpalette() or []
    counts = sorted(quant.getcolors() or [], reverse=True)
    return [tuple(pal[i * 3 : i * 3 + 3]) for _, i in counts]


def extract_palette(image_bytes: bytes) -> Palette:
    colors = _ranked_colors(image_bytes)
    dominant = colors[0]
    vibrant = max(colors, key=lambda c: _saturation(c) * (0.4 + _luma(c)))
    muted = min(colors, key=lambda c: abs(_luma(c) - 0.45) + _saturation(c) * 0.3)
    dark = min(colors, key=_luma)
    text = "#0b0b0f" if _luma(dominant) > 0.6 else "#f5f5f7"
    return Palette(_hex(dominant), _hex(vibrant), _hex(muted), _hex(dark), text)
