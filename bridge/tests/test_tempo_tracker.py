import random

from audio_reactive.tempo_tracker import TempoTracker

FPS = 48000 / 1024
SECONDS = 20


def run_tracker(bpm: float, with_offbeats: bool) -> TempoTracker:
    tracker = TempoTracker(FPS)
    rng = random.Random(1)
    period = round(FPS * 60 / bpm)
    for frame in range(int(FPS * SECONDS)):
        phase = frame % period
        if phase == 0:
            strength = 0.9
        elif with_offbeats and phase == period // 2:
            strength = 0.35
        else:
            strength = 0.05 * rng.random()
        tracker.push(strength)
    return tracker


def test_estimates_tempo_within_five_percent():
    for bpm in (70, 100, 128, 150, 180):
        assert abs(run_tracker(bpm, False).bpm - bpm) / bpm < 0.05


def test_busier_music_has_more_energy():
    sparse = run_tracker(100, False).energy
    busy = run_tracker(100, True).energy
    assert busy > sparse


def test_silence_reports_no_tempo():
    tracker = TempoTracker(FPS)
    for _ in range(int(FPS * SECONDS)):
        tracker.push(0.0)
    assert tracker.bpm == 0
