import io

from PIL import Image

from now_playing.palette import extract_palette


def png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def hue_family(hex_color: str) -> str:
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    if r > g and r > b:
        return "red"
    if b > r and b > g:
        return "blue"
    return "other"


def test_keeps_both_colors_of_a_two_color_cover():
    image = Image.new("RGB", (128, 128), (200, 40, 40))
    image.paste((40, 90, 200), (64, 0, 128, 128))
    palette = extract_palette(png_bytes(image))
    families = {hue_family(color) for color in palette.accents}
    assert {"red", "blue"} <= families


def test_dark_color_is_darker_than_dominant():
    image = Image.new("RGB", (128, 128), (230, 180, 60))
    image.paste((12, 10, 20), (0, 64, 128, 128))
    palette = extract_palette(png_bytes(image))
    luma = lambda c: sum(int(c[i : i + 2], 16) for i in (1, 3, 5))
    assert luma(palette.dark) < luma(palette.dominant)


def test_palette_values_are_hex_colors():
    palette = extract_palette(png_bytes(Image.new("RGB", (64, 64), (120, 60, 200))))
    for value in (palette.dominant, palette.vibrant, palette.muted, palette.dark, *palette.accents):
        assert len(value) == 7 and value.startswith("#")
