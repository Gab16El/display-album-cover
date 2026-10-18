from collections import deque

import numpy as np

HISTORY_SECONDS = 8
UPDATE_SECONDS = 1.0
MIN_BPM = 65
MAX_BPM = 200
ONSET_LEVEL = 0.25
BPM_SMOOTHING = 0.35
ENERGY_SMOOTHING = 0.25
BUSY_ONSETS_PER_SECOND = 6.0
MIN_VARIATION = 1e-3


class TempoTracker:
    def __init__(self, frames_per_second: float) -> None:
        self._fps = frames_per_second
        self._series: deque[float] = deque(maxlen=int(HISTORY_SECONDS * frames_per_second))
        self._every = max(1, int(UPDATE_SECONDS * frames_per_second))
        self._count = 0
        self.bpm = 0.0
        self.energy = 0.0

    def push(self, onset_strength: float) -> None:
        self._series.append(onset_strength)
        self._count += 1
        if self._count % self._every == 0 and len(self._series) == self._series.maxlen:
            self._update()

    def _update(self) -> None:
        series = np.array(self._series, dtype=np.float64)
        above = series > ONSET_LEVEL
        onsets = int(np.count_nonzero(above[1:] & ~above[:-1]))
        per_second = onsets / (len(series) / self._fps)
        density = min(per_second / BUSY_ONSETS_PER_SECOND, 1.0)
        self.energy += (density - self.energy) * ENERGY_SMOOTHING
        centered = series - series.mean()
        if centered.std() < MIN_VARIATION:
            return
        autocorr = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
        low = int(self._fps * 60 / MAX_BPM)
        high = int(self._fps * 60 / MIN_BPM)
        lag = low + int(np.argmax(autocorr[low:high]))
        measured = 60 * self._fps / lag
        self.bpm = measured if self.bpm == 0 else self.bpm + (measured - self.bpm) * BPM_SMOOTHING
