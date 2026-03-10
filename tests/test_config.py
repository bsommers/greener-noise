from __future__ import annotations

import pytest

from green_noise.config import NoiseConfig


def test_config_validation_passes_for_defaults() -> None:
    NoiseConfig().validate()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"sample_rate": 0}, "sample_rate"),
        ({"duration": 0}, "duration"),
        ({"amplitude": 1.1}, "amplitude"),
        ({"low_freq": -1}, "low_freq"),
        ({"low_freq": 500, "high_freq": 100}, "high_freq"),
        ({"sample_rate": 1000, "high_freq": 900}, "Nyquist"),
    ],
)
def test_config_validation_errors(kwargs: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        NoiseConfig(**kwargs).validate()
