from __future__ import annotations

import numpy as np

from green_noise.config import NoiseConfig
from green_noise.core import generate_green_noise


def test_generate_green_noise_length_and_dtype() -> None:
    cfg = NoiseConfig(sample_rate=8000, duration=2.0, low_freq=100, high_freq=500, amplitude=0.5)
    signal = generate_green_noise(cfg, rng=np.random.default_rng(1234))

    assert len(signal) == cfg.samples
    assert np.issubdtype(signal.dtype, np.floating)


def test_generate_green_noise_respects_amplitude() -> None:
    cfg = NoiseConfig(sample_rate=8000, duration=1.0, low_freq=120, high_freq=900, amplitude=0.25)
    signal = generate_green_noise(cfg, rng=np.random.default_rng(7))

    assert np.max(np.abs(signal)) <= cfg.amplitude + 1e-9


def test_generate_green_noise_band_limited() -> None:
    cfg = NoiseConfig(sample_rate=8000, duration=3.0, low_freq=200, high_freq=800, amplitude=0.8)
    signal = generate_green_noise(cfg, rng=np.random.default_rng(42))

    freqs = np.fft.rfftfreq(len(signal), d=1 / cfg.sample_rate)
    power = np.abs(np.fft.rfft(signal)) ** 2

    in_band = power[(freqs >= cfg.low_freq) & (freqs <= cfg.high_freq)].sum()
    out_band = power[(freqs < cfg.low_freq * 0.7) | (freqs > cfg.high_freq * 1.3)].sum()

    assert in_band > out_band
