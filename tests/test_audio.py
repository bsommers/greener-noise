from __future__ import annotations

import numpy as np

from green_noise.audio import to_int16


def test_to_int16_clips_values() -> None:
    data = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    pcm = to_int16(data)

    assert pcm.dtype == np.int16
    assert pcm[0] == -32767
    assert pcm[-1] == 32767
