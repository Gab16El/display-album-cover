import math
import time

from .levels import AudioLevels

BPM = 112


class SyntheticAnalyzer:
    def start(self) -> None:
        self._start = time.monotonic()
        self._last_beat_index = -1

    def stop(self) -> None:
        pass

    def snapshot(self) -> AudioLevels:
        t = time.monotonic() - self._start
        beat_pos = t * BPM / 60
        index = int(beat_pos)
        phase = beat_pos - index
        kick = math.exp(-phase * 5)
        beat = index != self._last_beat_index
        self._last_beat_index = index
        return AudioLevels(
            bass=0.25 + 0.7 * kick,
            mid=0.4 + 0.25 * math.sin(t * 1.3),
            treble=0.3 + 0.2 * math.sin(t * 3.1),
            level=0.35 + 0.4 * kick,
            beat=beat,
        )
