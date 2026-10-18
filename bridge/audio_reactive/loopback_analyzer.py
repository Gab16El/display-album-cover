import threading
import time

import numpy as np
import pyaudiowpatch as pyaudio

from .levels import AudioLevels

FRAME = 1024
BASS_BAND = (30, 200)
KICK_BAND = (30, 120)
SNARE_BAND = (200, 8000)
STALE_SECONDS = 0.3
PEAK_DECAY = 0.997
PULSE_DECAY = 0.8
KICK_THRESHOLD = 0.3
SNARE_THRESHOLD = 0.55
BASS_RISE = 0.5
BASS_FALL = 0.12


class LoopbackAnalyzer:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._peaks = {"bass": 1e-3, "kick": 1e-3, "snare": 1e-3, "level": 1e-3}
        self._levels = {"bass": 0.0, "kick": 0.0, "snare": 0.0, "level": 0.0}
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
                "bass": (freqs >= BASS_BAND[0]) & (freqs < BASS_BAND[1]),
                "kick": (freqs >= KICK_BAND[0]) & (freqs < KICK_BAND[1]),
                "snare": (freqs >= SNARE_BAND[0]) & (freqs < SNARE_BAND[1]),
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

    def _flux(self, spectrum: np.ndarray, mask: np.ndarray) -> float:
        if self._previous is None:
            return 0.0
        return float(np.maximum(spectrum[mask] - self._previous[mask], 0.0).sum())

    def _pulse(self, name: str, raw_flux: float, threshold: float) -> None:
        onset = max(0.0, (self._normalize(name, raw_flux) - threshold) / (1 - threshold))
        self._levels[name] = max(self._levels[name] * PULSE_DECAY, onset)

    def _on_audio(self, data, frame_count, time_info, status):
        mono = np.frombuffer(data, dtype=np.float32).reshape(-1, self._channels).mean(axis=1)
        if mono.size != FRAME:
            return (None, pyaudio.paContinue)
        spectrum = np.abs(np.fft.rfft(mono * self._window))
        with self._lock:
            bass = self._normalize("bass", float(spectrum[self._masks["bass"]].mean()))
            speed = BASS_RISE if bass > self._levels["bass"] else BASS_FALL
            self._levels["bass"] += (bass - self._levels["bass"]) * speed
            self._pulse("kick", self._flux(spectrum, self._masks["kick"]), KICK_THRESHOLD)
            self._pulse("snare", self._flux(spectrum, self._masks["snare"]), SNARE_THRESHOLD)
            self._levels["level"] = self._normalize("level", float(np.sqrt(np.mean(mono**2))))
            self._previous = spectrum
            self._stamp = time.monotonic()
        return (None, pyaudio.paContinue)

    def snapshot(self) -> AudioLevels:
        with self._lock:
            if time.monotonic() - self._stamp > STALE_SECONDS:
                for name in self._levels:
                    self._levels[name] *= 0.85
            return AudioLevels(**self._levels)
