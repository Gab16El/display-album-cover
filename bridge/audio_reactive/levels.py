from dataclasses import asdict, dataclass


@dataclass
class AudioLevels:
    bass: float = 0.0
    kick: float = 0.0
    snare: float = 0.0
    level: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)
