from collections import deque

import numpy as np

HISTORY_SECONDS = 8
ENERGY_WINDOW_SECONDS = 4
MIN_SECONDS_TO_ESTIMATE = 4
UPDATE_SECONDS = 0.5
MIN_BPM = 65
MAX_BPM = 200
ONSET_LEVEL = 0.25
BPM_SMOOTHING = 0.5
ENERGY_SMOOTHING = 0.5
BUSY_ONSETS_PER_SECOND = 6.0
MIN_VARIATION = 1e-3


class TempoTracker:
    def __init__(self, frames_per_second: float) -> None:
        self._fps = frames_per_second
        self._series: deque[float] = deque(maxlen=int(HISTORY_SECONDS * frames_per_second))
        self._every = max(1, int(UPDATE_SECONDS * frames_per_second))
        self._min_frames = int(MIN_SECONDS_TO_ESTIMATE * frames_per_second)
        self._count = 0
        self.bpm = 0.0
        self.energy = 0.0

    def push(self, onset_strength: float) -> None:
        self._series.append(onset_strength)
        self._count += 1
        if self._count % self._every == 0 and len(self._series) >= self._min_frames:
            self._update_energy()
            self._update_tempo()

    def _update_energy(self) -> None:
        recent = np.array(self._series, dtype=np.float64)[-int(ENERGY_WINDOW_SECONDS * self._fps) :]
        above = recent > ONSET_LEVEL
        onsets = int(np.count_nonzero(above[1:] & ~above[:-1]))
        density = min(onsets / (len(recent) / self._fps) / BUSY_ONSETS_PER_SECOND, 1.0)
        self.energy += (density - self.energy) * ENERGY_SMOOTHING

    def _update_tempo(self) -> None:
        series = np.array(self._series, dtype=np.float64)
        centered = series - series.mean()
        if centered.std() < MIN_VARIATION:
            return
        autocorr = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
        low = int(self._fps * 60 / MAX_BPM)
        high = min(int(self._fps * 60 / MIN_BPM), len(autocorr))
        lag = low + int(np.argmax(autocorr[low:high]))
        measured = 60 * self._fps / lag
        self.bpm = measured if self.bpm == 0 else self.bpm + (measured - self.bpm) * BPM_SMOOTHING
