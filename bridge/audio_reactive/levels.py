from dataclasses import asdict, dataclass


@dataclass
class AudioLevels:
    bass: float = 0.0
    mid: float = 0.0
    treble: float = 0.0
    level: float = 0.0
    beat: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
