from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NoiseConfig:
    sample_rate: int = 44100
    duration: float = 5.0
    low_freq: float = 20.0
    high_freq: float = 800.0
    amplitude: float = 0.5

    @property
    def nyquist(self) -> float:
        return self.sample_rate / 2.0

    @property
    def samples(self) -> int:
        return int(self.sample_rate * self.duration)

    def validate(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be > 0")
        if self.duration <= 0:
            raise ValueError("duration must be > 0")
        if not 0.0 <= self.amplitude <= 1.0:
            raise ValueError("amplitude must be between 0 and 1")
        if self.low_freq < 0:
            raise ValueError("low_freq must be >= 0")
        if self.high_freq <= self.low_freq:
            raise ValueError("high_freq must be greater than low_freq")
        if self.high_freq > self.nyquist:
            raise ValueError("high_freq must be <= Nyquist frequency")
