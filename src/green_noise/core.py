from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

from .config import NoiseConfig


def normalize(signal: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal.astype(np.float64)
    return (signal / peak).astype(np.float64)


def bandpass_filter(signal: np.ndarray, config: NoiseConfig, order: int = 4) -> np.ndarray:
    nyquist = config.nyquist
    low = max(1e-6, config.low_freq / nyquist)
    high = min(0.999999, config.high_freq / nyquist)
    sos = butter(order, [low, high], btype="band", output="sos")
    return sosfiltfilt(sos, signal)


def generate_green_noise(config: NoiseConfig, rng: np.random.Generator | None = None) -> np.ndarray:
    config.validate()
    generator = rng or np.random.default_rng()

    white_noise = generator.standard_normal(config.samples)
    integrated = np.cumsum(white_noise)
    filtered = bandpass_filter(integrated, config)
    normalized = normalize(filtered)
    return normalized * config.amplitude
