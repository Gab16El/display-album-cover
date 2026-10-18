import threading
import time

import numpy as np
import pyaudiowpatch as pyaudio

from .levels import AudioLevels

FRAME = 1024
BANDS = {"bass": (20, 150), "mid": (150, 2000), "treble": (2000, 8000)}
STALE_SECONDS = 0.3
BEAT_COOLDOWN = 0.25
BEAT_RATIO = 1.35
PEAK_DECAY = 0.997
RISE = 0.6
FALL = 0.15


class LoopbackAnalyzer:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._levels = {"bass": 0.0, "mid": 0.0, "treble": 0.0, "level": 0.0}
        self._peaks = {"bass": 1e-3, "mid": 1e-3, "treble": 1e-3, "level": 1e-3}
        self._bass_avg = 0.0
        self._last_beat = 0.0
        self._beat_pending = False
        self._stamp = 0.0
        self._channels = 2
        self._window = np.hanning(FRAME).astype(np.float32)
        self._pa = None
        self._stream = None

    def start(self) -> None:
        self._pa = pyaudio.PyAudio()
        device = self._pa.get_default_wasapi_loopback()
        rate = int(device["defaultSampleRate"])
        self._channels = int(device["maxInputChannels"])
        self._freqs = np.fft.rfftfreq(FRAME, 1.0 / rate)
        self._masks = {
            name: (self._freqs >= low) & (self._freqs < high)
            for name, (low, high) in BANDS.items()
        }
        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=self._channels,
            rate=rate,
            frames_per_buffer=FRAME,
            input=True,
            input_device_index=device["index"],
            stream_callback=self._on_audio,
        )

    def stop(self) -> None:
        if self._stream:
            self._stream.close()
        if self._pa:
            self._pa.terminate()

    def _smooth(self, name: str, raw: float) -> None:
        self._peaks[name] = max(self._peaks[name] * PEAK_DECAY, raw, 1e-3)
        target = min(raw / self._peaks[name], 1.0)
        current = self._levels[name]
        speed = RISE if target > current else FALL
        self._levels[name] = current + (target - current) * speed

    def _on_audio(self, data, frame_count, time_info, status):
        mono = np.frombuffer(data, dtype=np.float32).reshape(-1, self._channels).mean(axis=1)
        if mono.size != FRAME:
            return (None, pyaudio.paContinue)
        spectrum = np.abs(np.fft.rfft(mono * self._window))
        now = time.monotonic()
        with self._lock:
            for name, mask in self._masks.items():
                self._smooth(name, float(spectrum[mask].mean()))
            self._smooth("level", float(np.sqrt(np.mean(mono**2))))
            bass = self._levels["bass"]
            if (
                bass > self._bass_avg * BEAT_RATIO
                and bass > 0.35
                and now - self._last_beat > BEAT_COOLDOWN
            ):
                self._beat_pending = True
                self._last_beat = now
            self._bass_avg += (bass - self._bass_avg) * 0.08
            self._stamp = now
        return (None, pyaudio.paContinue)

    def snapshot(self) -> AudioLevels:
        with self._lock:
            if time.monotonic() - self._stamp > STALE_SECONDS:
                for name in self._levels:
                    self._levels[name] *= 0.85
            beat, self._beat_pending = self._beat_pending, False
            return AudioLevels(beat=beat, **self._levels)
