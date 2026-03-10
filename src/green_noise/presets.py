from __future__ import annotations

from .config import NoiseConfig


PRESETS: dict[str, NoiseConfig] = {
    "Custom": NoiseConfig(),
    "Sleep": NoiseConfig(duration=30.0, low_freq=40.0, high_freq=400.0, amplitude=0.35),
    "Focus": NoiseConfig(duration=15.0, low_freq=80.0, high_freq=1200.0, amplitude=0.45),
    "Masking": NoiseConfig(duration=10.0, low_freq=120.0, high_freq=2500.0, amplitude=0.55),
}
