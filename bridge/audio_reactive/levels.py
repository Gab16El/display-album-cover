from dataclasses import dataclass


@dataclass
class AudioLevels:
    bass: float = 0.0
    kick: float = 0.0
    snare: float = 0.0
    voice: float = 0.0
    guitar_left: float = 0.0
    guitar_right: float = 0.0
    level: float = 0.0
    bpm: float = 0.0
    energy: float = 0.0

    def to_dict(self) -> dict:
        return {
            "bass": self.bass,
            "kick": self.kick,
            "snare": self.snare,
            "voice": self.voice,
            "guitarL": self.guitar_left,
            "guitarR": self.guitar_right,
            "level": self.level,
            "bpm": self.bpm,
            "energy": self.energy,
        }
