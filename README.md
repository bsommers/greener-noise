# Green Noise

Green noise generator with a Tkinter desktop UI, command-line mode, plotting tools, and configurable color themes.

## What Was Implemented
- Modular architecture in `src/green_noise` (`core`, `audio`, `plotting`, `gui`, `cli`, `config`).
- Strict parameter validation (`sample_rate`, `duration`, `amplitude`, frequency bounds vs Nyquist).
- Unified generation pipeline used by GUI playback/export and CLI export.
- UI upgrades:
  - grouped controls (`Signal`, `Playback`, `Output`, `Display`)
  - live validation with inline field errors
  - status strip severity levels (`info`, `warning`, `error`)
  - presets (`Sleep`, `Focus`, `Masking`)
  - log/linear spectrum toggle
  - smoothing slider
  - autoscale/reset zoom controls and keyboard shortcuts
  - settings persistence (`.green_noise_ui.json`)
- Theme support: `light`, `dark`, `green`, `blues`, `ocean`.
- Quality gates: pytest tests and CI workflow for lint+format+tests.

## Install

```bash
pip install -r requirements.txt
```

Or directly:

```bash
pip install .
```

## Run GUI

```bash
green-noise
```

Compatibility launchers also work:

```bash
python3 green_noise_enhanced_v3.py
python3 main.py
```

## Run CLI (No GUI)

```bash
green-noise --no-gui --sample-rate 44100 --duration 10 --low-freq 40 --high-freq 900 --amplitude 0.45 --output output.wav
```

## Theme Examples

```bash
green-noise --theme light
green-noise --theme dark
green-noise --theme green
green-noise --theme blues
green-noise --theme ocean
```

## Tests and Checks

```bash
pytest
ruff check .
ruff format --check .
```

## Repository Layout

- `src/green_noise/config.py` - validated noise configuration dataclass
- `src/green_noise/core.py` - noise generation, filtering, normalization
- `src/green_noise/audio.py` - playback and WAV writing
- `src/green_noise/plotting.py` - waveform/spectrum computations
- `src/green_noise/gui.py` - Tkinter application
- `src/green_noise/cli.py` - CLI argument parsing and mode dispatch
- `tests/` - unit tests

## Docs
- [Code Improvement Plan](docs/CODE_IMPROVEMENT_PLAN.md)
- [UI Improvement Plan](docs/UI_IMPROVEMENT_PLAN.md)
- [Theming Guide](docs/THEMING.md)
