from dataclasses import dataclass, field


@dataclass(frozen=True)
class Palette:
    dominant: str
    vibrant: str
    muted: str
    dark: str
    text: str
    accents: tuple[str, ...] = ()


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    album: str

    @property
    def key(self) -> str:
        return f"{self.title}|{self.artist}|{self.album}"


@dataclass
class NowPlayingState:
    status: str = "idle"
    track: Track | None = None
    position: float = 0.0
    duration: float = 0.0
    cover_version: str | None = None
    palette: Palette | None = None
    genre: str | None = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        t = self.track
        p = self.palette
        return {
            "status": self.status,
            "title": t.title if t else "",
            "artist": t.artist if t else "",
            "album": t.album if t else "",
            "position": self.position,
            "duration": self.duration,
            "coverVersion": self.cover_version,
            "genre": self.genre,
            "palette": (
                {
                    "dominant": p.dominant,
                    "vibrant": p.vibrant,
                    "muted": p.muted,
                    "dark": p.dark,
                    "text": p.text,
                    "accents": list(p.accents),
                }
                if p
                else None
            ),
        }
