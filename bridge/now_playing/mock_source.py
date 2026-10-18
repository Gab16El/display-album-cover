import io
import time

from PIL import Image, ImageDraw

from .smtc_source import SmtcSnapshot

SEGMENT_SECONDS = 24.0
TRACKS = [
    ("Neon Drive", "Synth Harbor", "Night Circuits", ((255, 70, 120), (40, 10, 90))),
    ("Slow Tide", "Ocean Atlas", "Blue Hours", ((30, 160, 200), (10, 30, 70))),
    ("Amber Field", "Dry Season", "Golden Hush", ((255, 180, 60), (120, 40, 20))),
    ("Moss Signal", "Forest Radio", "Green Static", ((90, 200, 130), (10, 50, 40))),
]


def _cover(colors: tuple[tuple[int, int, int], tuple[int, int, int]]) -> bytes:
    top, bottom = colors
    size = 600
    img = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / size
        draw.line([(0, y), (size, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    draw.ellipse((150, 150, 450, 450), outline=(255, 255, 255), width=10)
    draw.ellipse((255, 255, 345, 345), fill=(255, 255, 255))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


class MockSource:
    def __init__(self) -> None:
        self._start = time.monotonic()
        self._covers = [_cover(t[3]) for t in TRACKS]

    async def read(self, with_thumbnail: bool) -> SmtcSnapshot:
        elapsed = time.monotonic() - self._start
        index = int(elapsed // SEGMENT_SECONDS) % len(TRACKS)
        title, artist, album, _ = TRACKS[index]
        return SmtcSnapshot(
            title=title,
            artist=artist,
            album=album,
            status="playing",
            position=elapsed % SEGMENT_SECONDS,
            duration=SEGMENT_SECONDS,
            thumbnail=self._covers[index] if with_thumbnail else None,
        )
