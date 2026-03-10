from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .audio import play_signal, save_wav
from .config import NoiseConfig
from .core import generate_green_noise
from .plotting import compute_spectrum, compute_waveform
from .presets import PRESETS
from .themes import THEMES


class GreenNoiseGUI:
    SETTINGS_FILE = Path(".green_noise_ui.json")

    def __init__(self, root: tk.Tk, initial_args: object | None = None):
        self.root = root
        self.root.title("Green Noise Generator")
        self.root.geometry("1380x860")

        self.noise_data: np.ndarray | None = None
        self.playing = False
        self.current_theme = "light"

        self.vars: dict[str, tk.Variable] = {}
        self.entry_widgets: dict[str, tk.Entry] = {}
        self.error_labels: dict[str, tk.Label] = {}

        self.waveform_limits = {"x_min": None, "x_max": None, "y_min": -1.0, "y_max": 1.0}
        self.spectrum_limits = {"x_min": 0.0, "x_max": 5000.0, "y_min": None, "y_max": None}

        self._build_vars()
        self._build_layout()
        self._bind_shortcuts()

        self._load_settings()
        self._apply_initial_args(initial_args)

        self.validate_all()
        self.apply_theme(self.vars["theme"].get())

    def _build_vars(self) -> None:
        self.vars["theme"] = tk.StringVar(value="light")
        self.vars["preset"] = tk.StringVar(value="Custom")

        self.vars["sample_rate"] = tk.StringVar(value="44100")
        self.vars["duration"] = tk.StringVar(value="5.0")
        self.vars["low_freq"] = tk.StringVar(value="20")
        self.vars["high_freq"] = tk.StringVar(value="800")
        self.vars["amplitude"] = tk.StringVar(value="0.5")
        self.vars["volume"] = tk.StringVar(value="50")

        self.vars["wf_x_min"] = tk.StringVar(value="auto")
        self.vars["wf_x_max"] = tk.StringVar(value="auto")
        self.vars["wf_y_min"] = tk.StringVar(value="-1.0")
        self.vars["wf_y_max"] = tk.StringVar(value="1.0")
        self.vars["sp_x_min"] = tk.StringVar(value="0")
        self.vars["sp_x_max"] = tk.StringVar(value="5000")
        self.vars["sp_y_min"] = tk.StringVar(value="auto")
        self.vars["sp_y_max"] = tk.StringVar(value="auto")

        self.vars["log_spectrum"] = tk.BooleanVar(value=False)
        self.vars["smoothing"] = tk.IntVar(value=1)

        for name in ["sample_rate", "duration", "low_freq", "high_freq", "amplitude", "volume"]:
            self.vars[name].trace_add("write", self._on_input_changed)

    def _build_layout(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        main = tk.Frame(self.root)
        main.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=0)
        main.grid_columnconfigure(1, weight=1)

        self.left_panel = tk.Frame(main)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        right_panel = tk.Frame(main)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self._build_signal_frame()
        self._build_playback_frame()
        self._build_output_frame()
        self._build_display_frame()

        plot_controls = tk.LabelFrame(right_panel, text="Plot Controls", padx=10, pady=8)
        plot_controls.grid(row=0, column=0, sticky="ew")
        self._build_plot_controls(plot_controls)

        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.status_label = tk.Label(self.root, text="Ready", anchor="w", padx=12, pady=6)
        self.status_label.grid(row=1, column=0, sticky="ew")

    def _build_signal_frame(self) -> None:
        frame = tk.LabelFrame(self.left_panel, text="Signal", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 8))

        self._add_numeric_row(frame, "Sample Rate", "sample_rate", 0)
        self._add_numeric_row(frame, "Duration (s)", "duration", 1)
        self._add_numeric_row(frame, "Low Freq (Hz)", "low_freq", 2)
        self._add_numeric_row(frame, "High Freq (Hz)", "high_freq", 3)
        self._add_numeric_row(frame, "Amplitude (0-1)", "amplitude", 4)

        tk.Label(frame, text="Preset").grid(row=5, column=0, sticky="w", pady=(6, 0))
        preset_menu = tk.OptionMenu(
            frame, self.vars["preset"], *PRESETS.keys(), command=self.apply_preset
        )
        preset_menu.grid(row=5, column=1, sticky="ew", pady=(6, 0))

        self.generate_button = tk.Button(
            frame, text="Generate", command=self.generate_noise, width=14
        )
        self.generate_button.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        frame.grid_columnconfigure(1, weight=1)

    def _build_playback_frame(self) -> None:
        frame = tk.LabelFrame(self.left_panel, text="Playback", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 8))

        self._add_numeric_row(frame, "Volume (0-100)", "volume", 0)

        self.play_button = tk.Button(frame, text="Play", command=self.play_noise, width=14)
        self.play_button.grid(row=1, column=0, pady=(8, 0), sticky="ew")
        self.stop_button = tk.Button(frame, text="Stop", command=self.stop_noise, width=14)
        self.stop_button.grid(row=1, column=1, pady=(8, 0), sticky="ew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def _build_output_frame(self) -> None:
        frame = tk.LabelFrame(self.left_panel, text="Output", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 8))

        self.save_wav_button = tk.Button(frame, text="Save WAV", command=self.save_to_wav)
        self.save_wav_button.pack(fill=tk.X, pady=2)

        self.export_png_button = tk.Button(
            frame, text="Export Plot PNG", command=self.export_plot_png
        )
        self.export_png_button.pack(fill=tk.X, pady=2)

        self.export_csv_button = tk.Button(
            frame, text="Export Spectrum CSV", command=self.export_spectrum_csv
        )
        self.export_csv_button.pack(fill=tk.X, pady=2)

        self.show_cmd_button = tk.Button(frame, text="Show Command", command=self.show_command)
        self.show_cmd_button.pack(fill=tk.X, pady=2)

        self.quit_button = tk.Button(frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(fill=tk.X, pady=(10, 2))

    def _build_display_frame(self) -> None:
        frame = tk.LabelFrame(self.left_panel, text="Display", padx=10, pady=10)
        frame.pack(fill=tk.X)

        tk.Label(frame, text="Theme").grid(row=0, column=0, sticky="w")
        self.theme_menu = tk.OptionMenu(
            frame, self.vars["theme"], *THEMES.keys(), command=self.on_theme_changed
        )
        self.theme_menu.grid(row=0, column=1, sticky="ew")

        tk.Checkbutton(
            frame,
            text="Log Spectrum",
            variable=self.vars["log_spectrum"],
            command=self.update_plots,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        tk.Label(frame, text="Smoothing").grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Scale(
            frame,
            from_=1,
            to=101,
            orient=tk.HORIZONTAL,
            variable=self.vars["smoothing"],
            command=lambda _: self.update_plots(),
            resolution=2,
            showvalue=True,
        ).grid(row=2, column=1, sticky="ew", pady=(6, 0))

        tk.Button(frame, text="Autoscale", command=self.autoscale_plots).grid(
            row=3, column=0, sticky="ew", pady=(8, 0)
        )
        tk.Button(frame, text="Reset Zoom", command=self.reset_plot_ranges).grid(
            row=3, column=1, sticky="ew", pady=(8, 0)
        )

        frame.grid_columnconfigure(1, weight=1)

    def _build_plot_controls(self, parent: tk.Widget) -> None:
        row = 0
        for key, label in [
            ("wf_x_min", "Wave X Min"),
            ("wf_x_max", "Wave X Max"),
            ("wf_y_min", "Wave Y Min"),
            ("wf_y_max", "Wave Y Max"),
            ("sp_x_min", "Spec X Min"),
            ("sp_x_max", "Spec X Max"),
            ("sp_y_min", "Spec Y Min"),
            ("sp_y_max", "Spec Y Max"),
        ]:
            tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
            tk.Entry(parent, textvariable=self.vars[key], width=12).grid(
                row=row, column=1, sticky="w", pady=2, padx=(6, 0)
            )
            row += 1

        tk.Button(parent, text="Apply Plot Ranges", command=self.apply_plot_ranges).grid(
            row=0, column=2, sticky="ew", padx=(14, 0)
        )
        tk.Button(parent, text="Reset to Auto", command=self.reset_plot_ranges).grid(
            row=1, column=2, sticky="ew", padx=(14, 0)
        )

    def _add_numeric_row(self, parent: tk.Widget, label: str, name: str, row: int) -> None:
        tk.Label(parent, text=label).grid(row=row * 2, column=0, sticky="w")
        entry = tk.Entry(parent, textvariable=self.vars[name], width=12)
        entry.grid(row=row * 2, column=1, sticky="ew")
        error = tk.Label(parent, text="", anchor="w")
        error.grid(row=row * 2 + 1, column=0, columnspan=2, sticky="w")

        self.entry_widgets[name] = entry
        self.error_labels[name] = error

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-g>", lambda _: self.generate_noise())
        self.root.bind("<Control-p>", lambda _: self.play_noise())
        self.root.bind("<Control-s>", lambda _: self.save_to_wav())
        self.root.bind("<Control-r>", lambda _: self.reset_plot_ranges())
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def _on_input_changed(self, *_: object) -> None:
        self.validate_all()

    def _validate_float(
        self, name: str, min_value: float | None = None, max_value: float | None = None
    ) -> tuple[bool, float | None]:
        raw = self.vars[name].get().strip()
        try:
            value = float(raw)
        except ValueError:
            self._set_field_error(name, "Must be numeric")
            return False, None

        if min_value is not None and value < min_value:
            self._set_field_error(name, f">= {min_value}")
            return False, None
        if max_value is not None and value > max_value:
            self._set_field_error(name, f"<= {max_value}")
            return False, None

        self._set_field_error(name, "")
        return True, value

    def _set_field_error(self, name: str, message: str) -> None:
        colors = THEMES[self.vars["theme"].get()]
        self.error_labels[name].config(text=message)
        if message:
            self.entry_widgets[name].config(bg="#FFDADB")
            self.error_labels[name].config(fg=colors["status_error"])
        else:
            self.entry_widgets[name].config(bg=colors["entry_bg"])

    def validate_all(self) -> bool:
        ok = True

        valid_sample_rate, sample_rate = self._validate_float("sample_rate", min_value=1)
        valid_duration, duration = self._validate_float("duration", min_value=0.001)
        valid_low, low_freq = self._validate_float("low_freq", min_value=0)
        valid_high, high_freq = self._validate_float("high_freq", min_value=0.001)
        valid_amp, _ = self._validate_float("amplitude", min_value=0.0, max_value=1.0)
        valid_vol, _ = self._validate_float("volume", min_value=0.0, max_value=100.0)

        ok = all([valid_sample_rate, valid_duration, valid_low, valid_high, valid_amp, valid_vol])

        if ok and low_freq is not None and high_freq is not None and low_freq >= high_freq:
            self._set_field_error("high_freq", "Must be > low freq")
            ok = False

        if (
            ok
            and sample_rate is not None
            and high_freq is not None
            and high_freq > sample_rate / 2.0
        ):
            self._set_field_error("high_freq", "Must be <= Nyquist")
            ok = False

        self._refresh_action_states(ok)
        return ok

    def _refresh_action_states(self, inputs_valid: bool) -> None:
        self.generate_button.config(state=tk.NORMAL if inputs_valid else tk.DISABLED)
        has_noise = self.noise_data is not None
        self.play_button.config(
            state=tk.NORMAL if has_noise and not self.playing and inputs_valid else tk.DISABLED
        )
        self.stop_button.config(state=tk.NORMAL if self.playing else tk.DISABLED)
        save_state = tk.NORMAL if has_noise else tk.DISABLED
        self.save_wav_button.config(state=save_state)
        self.export_png_button.config(state=save_state)
        self.export_csv_button.config(state=save_state)

    def build_config(self) -> NoiseConfig:
        return NoiseConfig(
            sample_rate=int(float(self.vars["sample_rate"].get())),
            duration=float(self.vars["duration"].get()),
            low_freq=float(self.vars["low_freq"].get()),
            high_freq=float(self.vars["high_freq"].get()),
            amplitude=float(self.vars["amplitude"].get()),
        )

    def apply_preset(self, preset_name: str) -> None:
        if preset_name not in PRESETS:
            return
        preset = PRESETS[preset_name]
        self.vars["sample_rate"].set(str(preset.sample_rate))
        self.vars["duration"].set(str(preset.duration))
        self.vars["low_freq"].set(str(preset.low_freq))
        self.vars["high_freq"].set(str(preset.high_freq))
        self.vars["amplitude"].set(str(preset.amplitude))
        self.set_status(f"Applied {preset_name} preset", "info")

    def generate_noise(self) -> None:
        if not self.validate_all():
            self.set_status("Fix input errors before generating", "warning")
            return

        try:
            config = self.build_config()
            self.noise_data = generate_green_noise(config)
            self.update_plots()
            self.set_status(f"Generated {config.duration:.2f}s green noise", "info")
        except ValueError as exc:
            self.set_status(str(exc), "error")
        finally:
            self._refresh_action_states(self.validate_all())

    def update_plots(self) -> None:
        if self.noise_data is None:
            return

        config = self.build_config()
        colors = THEMES[self.current_theme]

        self.ax_waveform.clear()
        self.ax_spectrum.clear()

        time_axis, waveform = compute_waveform(self.noise_data, config.duration)
        self.ax_waveform.plot(time_axis, waveform, color=colors["waveform_line"])
        self.ax_waveform.set_xlabel("Time (s)")
        self.ax_waveform.set_ylabel("Amplitude")
        self.ax_waveform.set_title("Green Noise Waveform")

        frequencies, magnitudes = compute_spectrum(
            self.noise_data,
            config.sample_rate,
            smoothing_window=int(self.vars["smoothing"].get()),
            use_log_scale=bool(self.vars["log_spectrum"].get()),
        )
        self.ax_spectrum.plot(frequencies, magnitudes, color=colors["spectrum_line"])
        self.ax_spectrum.set_xlabel("Frequency (Hz)")
        self.ax_spectrum.set_ylabel(
            "Log Magnitude" if self.vars["log_spectrum"].get() else "Magnitude"
        )
        self.ax_spectrum.set_title("Green Noise Spectrum")

        self._apply_plot_ranges_to_axes()
        self._apply_theme_to_plots(colors)
        self.canvas.draw_idle()

    def _apply_plot_ranges_to_axes(self) -> None:
        wf = self.waveform_limits
        sp = self.spectrum_limits
        if wf["x_min"] is not None and wf["x_max"] is not None:
            self.ax_waveform.set_xlim(wf["x_min"], wf["x_max"])
        if wf["y_min"] is not None and wf["y_max"] is not None:
            self.ax_waveform.set_ylim(wf["y_min"], wf["y_max"])
        if sp["x_min"] is not None and sp["x_max"] is not None:
            self.ax_spectrum.set_xlim(sp["x_min"], sp["x_max"])
        if sp["y_min"] is not None and sp["y_max"] is not None:
            self.ax_spectrum.set_ylim(sp["y_min"], sp["y_max"])

    def apply_plot_ranges(self) -> None:
        try:
            self.waveform_limits["x_min"] = self._parse_axis(self.vars["wf_x_min"].get())
            self.waveform_limits["x_max"] = self._parse_axis(self.vars["wf_x_max"].get())
            self.waveform_limits["y_min"] = self._parse_axis(self.vars["wf_y_min"].get())
            self.waveform_limits["y_max"] = self._parse_axis(self.vars["wf_y_max"].get())

            self.spectrum_limits["x_min"] = self._parse_axis(self.vars["sp_x_min"].get())
            self.spectrum_limits["x_max"] = self._parse_axis(self.vars["sp_x_max"].get())
            self.spectrum_limits["y_min"] = self._parse_axis(self.vars["sp_y_min"].get())
            self.spectrum_limits["y_max"] = self._parse_axis(self.vars["sp_y_max"].get())

            self.update_plots()
            self.set_status("Plot ranges applied", "info")
        except ValueError:
            self.set_status("Invalid plot range values", "warning")

    def _parse_axis(self, raw: str) -> float | None:
        raw = raw.strip().lower()
        if raw in {"auto", ""}:
            return None
        return float(raw)

    def reset_plot_ranges(self) -> None:
        self.vars["wf_x_min"].set("auto")
        self.vars["wf_x_max"].set("auto")
        self.vars["wf_y_min"].set("-1.0")
        self.vars["wf_y_max"].set("1.0")
        self.vars["sp_x_min"].set("0")
        self.vars["sp_x_max"].set("5000")
        self.vars["sp_y_min"].set("auto")
        self.vars["sp_y_max"].set("auto")

        self.waveform_limits = {"x_min": None, "x_max": None, "y_min": -1.0, "y_max": 1.0}
        self.spectrum_limits = {"x_min": 0.0, "x_max": 5000.0, "y_min": None, "y_max": None}
        self.update_plots()
        self.set_status("Plot ranges reset", "info")

    def autoscale_plots(self) -> None:
        self.waveform_limits = {"x_min": None, "x_max": None, "y_min": None, "y_max": None}
        self.spectrum_limits = {"x_min": None, "x_max": None, "y_min": None, "y_max": None}
        self.update_plots()
        self.set_status("Autoscale enabled", "info")

    def play_noise(self) -> None:
        if self.noise_data is None:
            self.set_status("Generate noise first", "warning")
            return
        if self.playing:
            return

        self.playing = True
        self._refresh_action_states(self.validate_all())

        volume = float(self.vars["volume"].get()) / 100.0
        signal = self.noise_data * volume

        def worker() -> None:
            try:
                play_signal(signal, self.build_config().sample_rate, lambda: self.playing)
                self.root.after(0, lambda: self.set_status("Playback finished", "info"))
            except Exception as exc:  # noqa: BLE001
                message = str(exc)
                self.root.after(0, lambda: self.set_status(f"Playback error: {message}", "error"))
            finally:
                self.playing = False
                self.root.after(0, lambda: self._refresh_action_states(self.validate_all()))

        threading.Thread(target=worker, daemon=True).start()
        self.set_status("Playing...", "info")

    def stop_noise(self) -> None:
        self.playing = False
        self._refresh_action_states(self.validate_all())
        self.set_status("Playback stopped", "info")

    def save_to_wav(self) -> None:
        if self.noise_data is None:
            self.set_status("No generated signal to save", "warning")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if not filename:
            return

        config = self.build_config()
        save_wav(filename, self.noise_data, config.sample_rate)
        self.set_status(f"Saved WAV: {filename}", "info")

    def export_plot_png(self) -> None:
        if self.noise_data is None:
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png")]
        )
        if not filename:
            return
        self.fig.savefig(filename, dpi=180)
        self.set_status(f"Saved PNG: {filename}", "info")

    def export_spectrum_csv(self) -> None:
        if self.noise_data is None:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return

        config = self.build_config()
        freqs, mags = compute_spectrum(
            self.noise_data,
            config.sample_rate,
            smoothing_window=int(self.vars["smoothing"].get()),
            use_log_scale=bool(self.vars["log_spectrum"].get()),
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write("frequency,magnitude\n")
            for freq, mag in zip(freqs, mags):
                f.write(f"{freq},{mag}\n")

        self.set_status(f"Saved CSV: {filename}", "info")

    def show_command(self) -> None:
        cmd = (
            "green-noise --no-gui "
            f"--sample-rate {self.vars['sample_rate'].get()} "
            f"--duration {self.vars['duration'].get()} "
            f"--low-freq {self.vars['low_freq'].get()} "
            f"--high-freq {self.vars['high_freq'].get()} "
            f"--amplitude {self.vars['amplitude'].get()} "
            f"--theme {self.vars['theme'].get()} "
            f"--smoothing {self.vars['smoothing'].get()}"
        )

        dialog = tk.Toplevel(self.root)
        dialog.title("Command Line Equivalent")
        dialog.geometry("760x210")
        text = tk.Text(dialog, wrap=tk.WORD, height=5)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert("1.0", cmd)
        text.config(state=tk.DISABLED)

    def on_theme_changed(self, selected_theme: str) -> None:
        self.apply_theme(selected_theme)
        self.update_plots()

    def apply_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return

        self.current_theme = theme_name
        colors = THEMES[theme_name]

        self.root.configure(bg=colors["bg"])
        self._apply_theme_to_widget(self.root, colors)
        self._apply_theme_to_plots(colors)
        self.canvas.draw_idle()

    def _apply_theme_to_widget(self, widget: tk.Widget, colors: dict[str, str]) -> None:
        widget_class = widget.winfo_class()
        config_map: dict[str, object] = {}

        if widget_class in ("Frame", "Toplevel"):
            config_map = {"bg": colors["bg"]}
        elif widget_class == "LabelFrame":
            config_map = {"bg": colors["panel_bg"], "fg": colors["text"]}
        elif widget_class == "Label":
            config_map = {"bg": colors["panel_bg"], "fg": colors["text"]}
            if widget is self.status_label:
                config_map = {"bg": colors["surface_bg"], "fg": colors["status_info"]}
        elif widget_class == "Entry":
            config_map = {
                "bg": colors["entry_bg"],
                "fg": colors["entry_fg"],
                "insertbackground": colors["entry_fg"],
            }
        elif widget_class == "Button":
            config_map = {
                "bg": colors["button_bg"],
                "fg": colors["button_fg"],
                "activebackground": colors["accent"],
                "activeforeground": colors["panel_bg"],
            }
            if widget is self.quit_button:
                config_map["fg"] = colors["danger"]
        elif widget_class == "Scale":
            config_map = {
                "bg": colors["panel_bg"],
                "fg": colors["text"],
                "troughcolor": colors["surface_bg"],
                "activebackground": colors["accent"],
            }
        elif widget_class == "Checkbutton":
            config_map = {
                "bg": colors["panel_bg"],
                "fg": colors["text"],
                "activebackground": colors["panel_bg"],
                "activeforeground": colors["text"],
                "selectcolor": colors["surface_bg"],
            }
        elif widget_class == "Menubutton":
            config_map = {
                "bg": colors["button_bg"],
                "fg": colors["button_fg"],
                "activebackground": colors["accent"],
                "activeforeground": colors["panel_bg"],
            }
            try:
                widget["menu"].config(
                    bg=colors["panel_bg"],
                    fg=colors["text"],
                    activebackground=colors["accent"],
                    activeforeground=colors["panel_bg"],
                )
            except tk.TclError:
                pass

        if config_map:
            try:
                widget.config(**config_map)
            except tk.TclError:
                pass

        for child in widget.winfo_children():
            self._apply_theme_to_widget(child, colors)

    def _apply_theme_to_plots(self, colors: dict[str, str]) -> None:
        self.fig.patch.set_facecolor(colors["plot_bg"])
        self.canvas.get_tk_widget().config(bg=colors["plot_bg"])

        for ax in (self.ax_waveform, self.ax_spectrum):
            ax.set_facecolor(colors["axes_bg"])
            ax.xaxis.label.set_color(colors["text"])
            ax.yaxis.label.set_color(colors["text"])
            ax.title.set_color(colors["text"])
            ax.tick_params(axis="x", colors=colors["muted_text"])
            ax.tick_params(axis="y", colors=colors["muted_text"])
            for spine in ax.spines.values():
                spine.set_color(colors["muted_text"])
            ax.grid(True, color=colors["grid"], alpha=0.65)

    def set_status(self, message: str, level: str = "info") -> None:
        colors = THEMES[self.current_theme]
        color_key = {
            "info": "status_info",
            "warning": "status_warning",
            "error": "status_error",
        }.get(level, "status_info")
        self.status_label.config(text=message, fg=colors[color_key])

    def _save_settings(self) -> None:
        settings = {
            "geometry": self.root.geometry(),
            "theme": self.vars["theme"].get(),
            "preset": self.vars["preset"].get(),
            "sample_rate": self.vars["sample_rate"].get(),
            "duration": self.vars["duration"].get(),
            "low_freq": self.vars["low_freq"].get(),
            "high_freq": self.vars["high_freq"].get(),
            "amplitude": self.vars["amplitude"].get(),
            "volume": self.vars["volume"].get(),
            "log_spectrum": self.vars["log_spectrum"].get(),
            "smoothing": self.vars["smoothing"].get(),
        }
        self.SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    def _load_settings(self) -> None:
        if not self.SETTINGS_FILE.exists():
            return
        try:
            settings = json.loads(self.SETTINGS_FILE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return

        if geometry := settings.get("geometry"):
            self.root.geometry(geometry)

        for key in [
            "theme",
            "preset",
            "sample_rate",
            "duration",
            "low_freq",
            "high_freq",
            "amplitude",
            "volume",
        ]:
            if key in settings:
                self.vars[key].set(str(settings[key]))

        if "log_spectrum" in settings:
            self.vars["log_spectrum"].set(bool(settings["log_spectrum"]))
        if "smoothing" in settings:
            self.vars["smoothing"].set(int(settings["smoothing"]))

    def _apply_initial_args(self, args: object | None) -> None:
        if args is None:
            return
        for arg_name, var_name in [
            ("sample_rate", "sample_rate"),
            ("duration", "duration"),
            ("low_freq", "low_freq"),
            ("high_freq", "high_freq"),
            ("amplitude", "amplitude"),
            ("theme", "theme"),
            ("smoothing", "smoothing"),
        ]:
            value = getattr(args, arg_name, None)
            if value is not None:
                self.vars[var_name].set(str(value))

        log_spectrum = getattr(args, "log_spectrum", None)
        if log_spectrum is not None:
            self.vars["log_spectrum"].set(bool(log_spectrum))

    def quit_app(self) -> None:
        self.playing = False
        self._save_settings()
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
            self.root.destroy()


def launch_gui(args: object | None = None) -> None:
    root = tk.Tk()
    app = GreenNoiseGUI(root, initial_args=args)
    app.update_plots()
    root.mainloop()
