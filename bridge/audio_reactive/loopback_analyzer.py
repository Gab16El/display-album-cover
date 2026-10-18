import threading
import time

import numpy as np
import pyaudiowpatch as pyaudio

from .levels import AudioLevels

FRAME = 1024
BANDS = {
    "bass": (30, 200),
    "kick": (30, 120),
    "snare": (200, 8000),
    "voice": (250, 3500),
    "guitar": (100, 5000),
}
STALE_SECONDS = 0.3
PEAK_DECAY = 0.997
PULSE_DECAY = 0.8
KICK_THRESHOLD = 0.3
SNARE_THRESHOLD = 0.55
SMOOTHING = {
    "bass": (0.5, 0.12),
    "voice": (0.3, 0.07),
    "guitar_left": (0.35, 0.1),
    "guitar_right": (0.35, 0.1),
}
STATE_NAMES = ("bass", "kick", "snare", "voice", "guitar_left", "guitar_right", "level")


class LoopbackAnalyzer:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._peaks = {name: 1e-3 for name in STATE_NAMES}
        self._levels = {name: 0.0 for name in STATE_NAMES}
        self._previous: np.ndarray | None = None
        self._stamp = 0.0
        self._channels = 2
        self._window = np.hanning(FRAME).astype(np.float32)
        self._pa = None
        self._stream = None

    def start(self) -> None:
        ready = threading.Event()
        self._error: OSError | None = None
        self._thread = threading.Thread(target=self._run, args=(ready,), daemon=True)
        self._thread.start()
        ready.wait(timeout=5)
        if self._error:
            raise self._error

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self, ready: threading.Event) -> None:
        # PyAudio initializes COM on its thread; keep it away from the winrt thread.
        try:
            self._pa = pyaudio.PyAudio()
            device = self._pa.get_default_wasapi_loopback()
            rate = int(device["defaultSampleRate"])
            self._channels = int(device["maxInputChannels"])
            freqs = np.fft.rfftfreq(FRAME, 1.0 / rate)
            self._masks = {
                name: (freqs >= low) & (freqs < high) for name, (low, high) in BANDS.items()
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
        except OSError as exc:
            self._error = exc
            ready.set()
            return
        ready.set()
        self._stop_event.wait()
        self._stream.close()
        self._pa.terminate()

    def _normalize(self, name: str, raw: float) -> float:
        self._peaks[name] = max(self._peaks[name] * PEAK_DECAY, raw, 1e-3)
        return min(raw / self._peaks[name], 1.0)

    def _smooth(self, name: str, raw: float) -> None:
        target = self._normalize(name, raw)
        rise, fall = SMOOTHING[name]
        current = self._levels[name]
        self._levels[name] = current + (target - current) * (rise if target > current else fall)

    def _flux(self, spectrum: np.ndarray, band: str) -> float:
        if self._previous is None:
            return 0.0
        mask = self._masks[band]
        return float(np.maximum(spectrum[mask] - self._previous[mask], 0.0).sum())

    def _pulse(self, name: str, raw_flux: float, threshold: float) -> None:
        onset = max(0.0, (self._normalize(name, raw_flux) - threshold) / (1 - threshold))
        self._levels[name] = max(self._levels[name] * PULSE_DECAY, onset)

    def _on_audio(self, data, frame_count, time_info, status):
        frames = np.frombuffer(data, dtype=np.float32).reshape(-1, self._channels)
        if frames.shape[0] != FRAME:
            return (None, pyaudio.paContinue)
        left = frames[:, 0]
        right = frames[:, 1] if self._channels > 1 else left
        mono = (left + right) / 2
        mono_fft = np.abs(np.fft.rfft(mono * self._window))
        left_fft = np.abs(np.fft.rfft(left * self._window))
        right_fft = np.abs(np.fft.rfft(right * self._window))
        center = np.minimum(left_fft, right_fft)
        guitar = self._masks["guitar"]
        with self._lock:
            self._smooth("bass", float(mono_fft[self._masks["bass"]].mean()))
            self._pulse("kick", self._flux(mono_fft, "kick"), KICK_THRESHOLD)
            self._pulse("snare", self._flux(mono_fft, "snare"), SNARE_THRESHOLD)
            self._smooth("voice", float(center[self._masks["voice"]].mean()))
            self._smooth("guitar_left", float(np.maximum(left_fft - right_fft, 0)[guitar].mean()))
            self._smooth("guitar_right", float(np.maximum(right_fft - left_fft, 0)[guitar].mean()))
            self._levels["level"] = self._normalize("level", float(np.sqrt(np.mean(mono**2))))
            self._previous = mono_fft
            self._stamp = time.monotonic()
        return (None, pyaudio.paContinue)

    def snapshot(self) -> AudioLevels:
        with self._lock:
            if time.monotonic() - self._stamp > STALE_SECONDS:
                for name in self._levels:
                    self._levels[name] *= 0.85
            return AudioLevels(**self._levels)
