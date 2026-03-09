# Theming Guide

The GUI now supports five named color schemes:
- `light`
- `dark`
- `green`
- `blues`
- `ocean`

## In-App Usage
- Open the app normally.
- Use the `Theme` selector in the left panel.
- Theme changes apply to controls and matplotlib plots.

## CLI Usage
- Start the GUI with a theme:

```bash
python3 green_noise_enhanced_v3.py --theme ocean
```

Allowed values:

```bash
python3 green_noise_enhanced_v3.py --theme light
python3 green_noise_enhanced_v3.py --theme dark
python3 green_noise_enhanced_v3.py --theme green
python3 green_noise_enhanced_v3.py --theme blues
python3 green_noise_enhanced_v3.py --theme ocean
```

## Implementation Notes
- Theme definitions live in `DataLoggerGUI.themes`.
- `apply_theme()` updates Tk widget styling recursively.
- Plot colors are synchronized through `_apply_theme_to_plots()`.
- Waveform and spectrum line colors are theme-specific.

## Extending Themes
To add a new theme, copy an existing entry and provide values for:
- `bg`, `panel_bg`, `surface_bg`
- `text`, `muted_text`
- `button_bg`, `button_fg`
- `entry_bg`, `entry_fg`
- `accent`, `danger`, `status_fg`
- `plot_bg`, `axes_bg`, `grid`
- `waveform_line`, `spectrum_line`
