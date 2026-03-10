from __future__ import annotations

import argparse

from .audio import save_wav
from .config import NoiseConfig
from .core import generate_green_noise
from .gui import launch_gui
from .themes import THEMES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Green Noise Generator")
    parser.add_argument("--no-gui", action="store_true", help="Run in command line mode")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Sample rate in Hz")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds")
    parser.add_argument("--low-freq", type=float, default=20.0, help="Low frequency in Hz")
    parser.add_argument("--high-freq", type=float, default=800.0, help="High frequency in Hz")
    parser.add_argument("--amplitude", type=float, default=0.5, help="Amplitude (0-1)")
    parser.add_argument(
        "--theme", type=str, default="light", choices=sorted(THEMES.keys()), help="UI theme"
    )
    parser.add_argument("--smoothing", type=int, default=1, help="Spectrum smoothing window")
    parser.add_argument(
        "--log-spectrum", action="store_true", help="Use log magnitude scale for spectrum"
    )
    parser.add_argument(
        "--output", type=str, default="output.wav", help="Output WAV file for command mode"
    )
    return parser


def run_command_mode(args: argparse.Namespace) -> None:
    config = NoiseConfig(
        sample_rate=args.sample_rate,
        duration=args.duration,
        low_freq=args.low_freq,
        high_freq=args.high_freq,
        amplitude=args.amplitude,
    )
    config.validate()
    noise = generate_green_noise(config)
    save_wav(args.output, noise, config.sample_rate)
    print(f"Saved WAV: {args.output}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.no_gui:
        run_command_mode(args)
    else:
        launch_gui(args)


if __name__ == "__main__":
    main()
