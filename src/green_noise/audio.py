from __future__ import annotations

import wave

import numpy as np


def to_int16(signal: np.ndarray) -> np.ndarray:
    clipped = np.clip(signal, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16)


def save_wav(filename: str, signal: np.ndarray, sample_rate: int) -> None:
    audio_data = to_int16(signal)
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())


def play_signal(signal: np.ndarray, sample_rate: int, should_continue: callable) -> None:
    try:
        import pyaudio
    except ImportError as exc:
        raise RuntimeError("pyaudio is required for playback") from exc

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)

    try:
        audio_data = to_int16(signal)
        chunk_size = 1024
        for i in range(0, len(audio_data), chunk_size):
            if not should_continue():
                break
            stream.write(audio_data[i : i + chunk_size].tobytes())
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
