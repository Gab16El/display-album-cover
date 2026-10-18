import math
import time

from .levels import AudioLevels

BPM = 112


class SyntheticAnalyzer:
    def start(self) -> None:
        self._start = time.monotonic()

    def stop(self) -> None:
        pass

    def snapshot(self) -> AudioLevels:
        t = time.monotonic() - self._start
        beat_pos = t * BPM / 60
        phase = beat_pos - int(beat_pos)
        hit = math.exp(-phase * 6)
        on_backbeat = int(beat_pos) % 2 == 1
        return AudioLevels(
            bass=0.35 + 0.25 * math.sin(t * 0.8) ** 2,
            kick=0.0 if on_backbeat else hit,
            snare=hit if on_backbeat else 0.0,
            voice=0.5 + 0.4 * math.sin(t * 0.5) ** 2,
            guitar_left=max(0.0, math.sin(t * 0.9)),
            guitar_right=max(0.0, math.sin(t * 0.9 + 2.2)),
            level=0.35 + 0.4 * hit,
        )
