# UI Improvement Plan

## UX Objectives
- Keep generation controls fast and obvious for first-time users.
- Reduce accidental invalid input.
- Improve visual readability across different environments.
- Make core tasks one-click: generate, preview, play/stop, save.

## Current UX Gaps
- Numeric fields allow invalid values until runtime errors occur.
- Frequency fields are present but not clearly tied to audible result in all flows.
- Status messaging is single-line and not severity-scoped.
- Layout density is high for smaller screens.

## Plan

### 1. Input Reliability
- Add live validation for all numeric entries with inline error hints.
- Disable action buttons when inputs are invalid.
- Add a compact preset selector (e.g., `Sleep`, `Focus`, `Masking`) that fills ranges.

### 2. Information Architecture
- Group controls by intent:
  - `Signal`: sample rate, duration, low/high frequency, amplitude
  - `Playback`: play/stop, live volume
  - `Output`: save WAV, export chart
  - `Display`: plot ranges and theme
- Keep status strip persistent with color-coded states: info/warning/error.

### 3. Plot Experience
- Add a toggle for linear/log spectrum view.
- Add reset-zoom and autoscale shortcuts.
- Add optional smoothing window for spectrum readability.

### 4. Accessibility
- Ensure minimum contrast ratios in all themes.
- Add keyboard-first navigation order and shortcuts.
- Increase default touch target sizing for buttons/sliders.

### 5. Responsiveness
- Replace fixed window sizing with weight-based grid layout.
- Define compact mode behavior below ~1100px width.
- Persist last-used window size and UI settings.

## Validation and Metrics
- Measure time-to-first-audio for a new user.
- Track invalid-input error frequency before/after validation.
- Run manual checks on Linux/macOS/Windows for Tk rendering parity.
