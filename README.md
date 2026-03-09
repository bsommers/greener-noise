# Green Noise

A Python desktop app for generating, visualizing, playing, and exporting green noise.

## Current Entrypoint
- GUI + CLI: `green_noise_enhanced_v3.py`

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 green_noise_enhanced_v3.py
```

## Command-Line Mode

```bash
python3 green_noise_enhanced_v3.py --no-gui --sample-rate 44100 --duration 10 --output output.wav
```

## Theme Support
Available schemes:
- `light`
- `dark`
- `green`
- `blues`
- `ocean`

Example:

```bash
python3 green_noise_enhanced_v3.py --theme ocean
```

## Documentation
- [Code Improvement Plan](docs/CODE_IMPROVEMENT_PLAN.md)
- [UI Improvement Plan](docs/UI_IMPROVEMENT_PLAN.md)
- [Theming Guide](docs/THEMING.md)
