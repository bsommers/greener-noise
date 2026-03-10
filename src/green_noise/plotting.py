from __future__ import annotations

import numpy as np


def moving_average(signal: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return signal
    kernel = np.ones(window, dtype=np.float64) / window
    return np.convolve(signal, kernel, mode="same")


def compute_waveform(signal: np.ndarray, duration: float) -> tuple[np.ndarray, np.ndarray]:
    time_axis = np.linspace(0, duration, len(signal))
    return time_axis, signal


def compute_spectrum(
    signal: np.ndarray,
    sample_rate: int,
    smoothing_window: int = 1,
    use_log_scale: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    fft_data = np.fft.rfft(signal)
    frequencies = np.fft.rfftfreq(len(signal), 1 / sample_rate)
    magnitudes = np.abs(fft_data)
    if smoothing_window > 1:
        magnitudes = moving_average(magnitudes, smoothing_window)
    if use_log_scale:
        magnitudes = np.log10(np.maximum(magnitudes, 1e-12))
    return frequencies, magnitudes
