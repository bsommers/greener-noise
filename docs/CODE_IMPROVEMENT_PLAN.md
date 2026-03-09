# Code Improvement Plan

## Goals
- Reduce maintenance overhead from many overlapping scripts.
- Improve correctness of signal generation parameters.
- Make the codebase testable and easier to evolve.
- Standardize packaging, dependency management, and releases.

## Current Observations
- Multiple generator scripts (`green-noise.py`, `greener_noise.py`, `green_noise_enhanced.py`, `green_noise_enhanced_v3.py`, etc.) appear to overlap in purpose.
- `low_freq` and `high_freq` are exposed in the UI/CLI, but not consistently applied to generation paths in all scripts.
- `pyproject.toml` metadata is minimal and dependencies are split between `pyproject.toml` and `requirements.txt`.
- No automated tests or lint/type checks are currently defined.
- Audio generation, playback, plotting, and Tkinter UI concerns are tightly coupled.

## Priority Roadmap

### Phase 1: Stabilize (1-2 days)
- Choose one canonical app entrypoint (recommended: `green_noise_enhanced_v3.py` for now).
- Mark other scripts as legacy or archive them under `legacy/`.
- Add clear parameter validation:
  - `sample_rate > 0`
  - `duration > 0`
  - `0 <= amplitude <= 1`
  - `0 <= low_freq < high_freq <= Nyquist`
- Ensure the same generation pipeline is used for both playback and WAV export.

### Phase 2: Refactor Architecture (2-4 days)
- Split into modules:
  - `src/green_noise/core.py` (noise generation, filtering, normalization)
  - `src/green_noise/audio.py` (playback and wav writing)
  - `src/green_noise/plotting.py` (spectrum/waveform visualization)
  - `src/green_noise/gui.py` (Tkinter UI only)
  - `src/green_noise/cli.py` (argument parsing and command mode)
- Move hard-coded defaults into a single config dataclass.
- Introduce typed interfaces between modules.

### Phase 3: Quality Gates (1-2 days)
- Add `pytest` with unit tests for:
  - output length and dtype
  - normalization/clipping behavior
  - frequency-domain checks for filter boundaries
- Add linting/formatting (`ruff`, `black`) and optional type checks (`mypy`).
- Add CI workflow to run tests and lint on push/PR.

### Phase 4: Packaging and Releases (1 day)
- Move dependencies into `pyproject.toml` and keep one source of truth.
- Add console script entrypoint (e.g., `green-noise`).
- Add semantic versioning and release notes process.

## Technical Debt Backlog
- Replace direct thread-to-UI widget updates with Tk-safe callbacks (`root.after`) for thread safety.
- Remove duplicate layout assignment in UI code paths where panels are recreated.
- Add structured logging instead of print/status-only diagnostics.
- Add waveform/spectrum export (PNG/CSV) to support reproducibility.

## Done Criteria
- Single canonical app path and module layout.
- Parameter behavior matches UI labels and CLI arguments.
- Test suite and linting pass locally and in CI.
- README reflects actual run/install flow and references docs.
