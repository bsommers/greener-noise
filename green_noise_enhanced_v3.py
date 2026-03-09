import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import wave
import pyaudio
import argparse
import sys
import threading

class GreenNoiseGenerator:
    """Generate green noise (1/f^2 spectrum)"""
    def __init__(self, sample_rate=44100, duration=1.0):
        self.sample_rate = sample_rate
        self.duration = duration
        self.samples = int(sample_rate * duration)
        
    def generate_green_noise(self):
        # Generate green noise using cumulative sum of white noise
        white_noise = np.random.randn(self.samples)
        green_noise = np.cumsum(white_noise)
        
        # Normalize to prevent clipping
        green_noise = green_noise / np.max(np.abs(green_noise))
        
        return green_noise
        
    def save_to_wav(self, filename):
        """Save generated noise to WAV file"""
        noise = self.generate_green_noise()
        
        # Convert to 16-bit integers
        audio_data = (noise * 32767).astype(np.int16)
        
        # Write to WAV file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

class DataLoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Green Noise Generator")
        self.root.geometry("1400x900")
        
        self.playing = False
        self.audio_thread = None
        
        # Plot range defaults
        self.waveform_x_min = None
        self.waveform_x_max = None
        self.waveform_y_min = -1.0
        self.waveform_y_max = 1.0
        self.spectrum_x_min = 0
        self.spectrum_x_max = 5000
        self.spectrum_y_min = None
        self.spectrum_y_max = None

        self.themes = {
            "light": {
                "bg": "#F5F7FA",
                "panel_bg": "#FFFFFF",
                "surface_bg": "#EEF2F7",
                "text": "#1C2430",
                "muted_text": "#435163",
                "button_bg": "#DDE6F0",
                "button_fg": "#1C2430",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#1C2430",
                "accent": "#2A6DB0",
                "danger": "#AF2E2E",
                "status_fg": "#2A6DB0",
                "plot_bg": "#F5F7FA",
                "axes_bg": "#FFFFFF",
                "grid": "#CAD4DF",
                "waveform_line": "#2A6DB0",
                "spectrum_line": "#2F8C5A",
            },
            "dark": {
                "bg": "#12171E",
                "panel_bg": "#1B2430",
                "surface_bg": "#263243",
                "text": "#EAF0F7",
                "muted_text": "#BECBE0",
                "button_bg": "#314257",
                "button_fg": "#EAF0F7",
                "entry_bg": "#223041",
                "entry_fg": "#EAF0F7",
                "accent": "#58A6FF",
                "danger": "#FF7B72",
                "status_fg": "#7CC8FF",
                "plot_bg": "#12171E",
                "axes_bg": "#1B2430",
                "grid": "#3A4A5F",
                "waveform_line": "#7CC8FF",
                "spectrum_line": "#78E1AE",
            },
            "green": {
                "bg": "#EAF6EE",
                "panel_bg": "#D9EEDA",
                "surface_bg": "#CBE5D0",
                "text": "#123024",
                "muted_text": "#1E4A38",
                "button_bg": "#A2C8AA",
                "button_fg": "#123024",
                "entry_bg": "#F4FBF6",
                "entry_fg": "#123024",
                "accent": "#2E8B57",
                "danger": "#A12D2D",
                "status_fg": "#1D6B44",
                "plot_bg": "#EAF6EE",
                "axes_bg": "#F4FBF6",
                "grid": "#AACDB5",
                "waveform_line": "#2E8B57",
                "spectrum_line": "#1A5F3F",
            },
            "blues": {
                "bg": "#EAF3FF",
                "panel_bg": "#D7E8FF",
                "surface_bg": "#C6DCFA",
                "text": "#0F2A4A",
                "muted_text": "#27486E",
                "button_bg": "#A9C9F6",
                "button_fg": "#0F2A4A",
                "entry_bg": "#F5FAFF",
                "entry_fg": "#0F2A4A",
                "accent": "#2463B2",
                "danger": "#9E2E2E",
                "status_fg": "#1D4F8F",
                "plot_bg": "#EAF3FF",
                "axes_bg": "#F5FAFF",
                "grid": "#AFC6E6",
                "waveform_line": "#2463B2",
                "spectrum_line": "#3E8CD0",
            },
            "ocean": {
                "bg": "#E7F7F8",
                "panel_bg": "#D5EDF0",
                "surface_bg": "#C3E3E9",
                "text": "#123440",
                "muted_text": "#2A5969",
                "button_bg": "#8EC9D3",
                "button_fg": "#123440",
                "entry_bg": "#F2FBFC",
                "entry_fg": "#123440",
                "accent": "#1D7E94",
                "danger": "#A13030",
                "status_fg": "#0F6679",
                "plot_bg": "#E7F7F8",
                "axes_bg": "#F2FBFC",
                "grid": "#9FCAD2",
                "waveform_line": "#1D7E94",
                "spectrum_line": "#2F9A7D",
            },
        }
        self.current_theme = "light"
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        left_panel = tk.Frame(container, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # Theme selector
        theme_frame = tk.LabelFrame(left_panel, text="Theme", padx=10, pady=10)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_menu = tk.OptionMenu(theme_frame, self.theme_var, *self.themes.keys(), command=self.on_theme_changed)
        self.theme_menu.config(width=12)
        self.theme_menu.pack(anchor=tk.W)
        
        # Parameters frame
        params_frame = tk.LabelFrame(left_panel, text="Parameters", padx=10, pady=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sample rate parameter
        tk.Label(params_frame, text="Sample Rate:").pack(anchor=tk.W)
        self.sample_rate_var = tk.StringVar(value="44100")
        tk.Entry(params_frame, textvariable=self.sample_rate_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        # Duration parameter
        tk.Label(params_frame, text="Duration (s):").pack(anchor=tk.W)
        self.duration_var = tk.StringVar(value="5.0")
        tk.Entry(params_frame, textvariable=self.duration_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        # Low frequency parameter
        tk.Label(params_frame, text="Low Freq (Hz):").pack(anchor=tk.W)
        self.low_freq_var = tk.StringVar(value="20")
        tk.Entry(params_frame, textvariable=self.low_freq_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        # High frequency parameter
        tk.Label(params_frame, text="High Freq (Hz):").pack(anchor=tk.W)
        self.high_freq_var = tk.StringVar(value="800")
        tk.Entry(params_frame, textvariable=self.high_freq_var, width=15).pack(anchor=tk.W, pady=(0, 10))
        
        # Volume parameter
        tk.Label(params_frame, text="Volume (0-100):").pack(anchor=tk.W)
        volume_frame = tk.Frame(params_frame)
        volume_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.volume_var = tk.DoubleVar(value=50.0)
        self.volume_entry = tk.Entry(volume_frame, textvariable=self.volume_var, width=8)
        self.volume_entry.pack(side=tk.LEFT)
        self.volume_entry.bind('<Return>', self.on_volume_entry_changed)
        self.volume_entry.bind('<FocusOut>', self.on_volume_entry_changed)
        
        self.volume_slider = tk.Scale(params_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                      variable=self.volume_var, command=self.on_volume_slider_changed,
                                      showvalue=0, length=150)
        self.volume_slider.pack(anchor=tk.W, pady=(0, 10))
        
        # Amplitude parameter
        tk.Label(params_frame, text="Amplitude (0-1):").pack(anchor=tk.W)
        amplitude_frame = tk.Frame(params_frame)
        amplitude_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.amplitude_var = tk.DoubleVar(value=0.5)
        self.amplitude_entry = tk.Entry(amplitude_frame, textvariable=self.amplitude_var, width=8)
        self.amplitude_entry.pack(side=tk.LEFT)
        self.amplitude_entry.bind('<Return>', self.on_amplitude_entry_changed)
        self.amplitude_entry.bind('<FocusOut>', self.on_amplitude_entry_changed)
        
        self.amplitude_slider = tk.Scale(params_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                         variable=self.amplitude_var, command=self.on_amplitude_slider_changed,
                                         showvalue=0, length=150)
        self.amplitude_slider.pack(anchor=tk.W)
        
        # Buttons frame
        buttons_frame = tk.LabelFrame(left_panel, text="Actions", padx=10, pady=10)
        buttons_frame.pack(fill=tk.X)
        
        # Generate button
        self.generate_button = tk.Button(buttons_frame, text="Generate Noise", command=self.generate_noise, width=15)
        self.generate_button.pack(pady=2)
        
        # Play button
        self.play_button = tk.Button(buttons_frame, text="Play", command=self.play_noise, width=15, state=tk.DISABLED)
        self.play_button.pack(pady=2)
        
        # Stop button
        self.stop_button = tk.Button(buttons_frame, text="Stop", command=self.stop_noise, width=15, state=tk.DISABLED)
        self.stop_button.pack(pady=2)
        
        # Save to WAV button
        self.save_wav_button = tk.Button(buttons_frame, text="Save to WAV", command=self.save_to_wav, width=15)
        self.save_wav_button.pack(pady=2)
        
        # Show Command button
        self.show_cmd_button = tk.Button(buttons_frame, text="Show Command", command=self.show_command, width=15)
        self.show_cmd_button.pack(pady=2)
        
        # Quit button
        self.quit_button = tk.Button(buttons_frame, text="Quit", command=self.quit_app, width=15)
        self.quit_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(left_panel, text="Ready", wraplength=180)
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Right panel for plots and controls
        right_panel = tk.Frame(container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Plot controls frame
        plot_controls_frame = tk.LabelFrame(right_panel, text="Plot Controls", padx=10, pady=5)
        plot_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Waveform controls
        wf_frame = tk.Frame(plot_controls_frame)
        wf_frame.pack(fill=tk.X, pady=2)
        tk.Label(wf_frame, text="Waveform X:").pack(side=tk.LEFT, padx=2)
        tk.Label(wf_frame, text="Min:").pack(side=tk.LEFT)
        self.wf_x_min_var = tk.StringVar(value="auto")
        tk.Entry(wf_frame, textvariable=self.wf_x_min_var, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(wf_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.wf_x_max_var = tk.StringVar(value="auto")
        tk.Entry(wf_frame, textvariable=self.wf_x_max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Label(wf_frame, text="Y:").pack(side=tk.LEFT, padx=(20,2))
        tk.Label(wf_frame, text="Min:").pack(side=tk.LEFT)
        self.wf_y_min_var = tk.StringVar(value="-1.0")
        tk.Entry(wf_frame, textvariable=self.wf_y_min_var, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(wf_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.wf_y_max_var = tk.StringVar(value="1.0")
        tk.Entry(wf_frame, textvariable=self.wf_y_max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Spectrum controls
        sp_frame = tk.Frame(plot_controls_frame)
        sp_frame.pack(fill=tk.X, pady=2)
        tk.Label(sp_frame, text="Spectrum X:").pack(side=tk.LEFT, padx=2)
        tk.Label(sp_frame, text="Min:").pack(side=tk.LEFT)
        self.sp_x_min_var = tk.StringVar(value="0")
        tk.Entry(sp_frame, textvariable=self.sp_x_min_var, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(sp_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.sp_x_max_var = tk.StringVar(value="5000")
        tk.Entry(sp_frame, textvariable=self.sp_x_max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Label(sp_frame, text="Y:").pack(side=tk.LEFT, padx=(20,2))
        tk.Label(sp_frame, text="Min:").pack(side=tk.LEFT)
        self.sp_y_min_var = tk.StringVar(value="auto")
        tk.Entry(sp_frame, textvariable=self.sp_y_min_var, width=8).pack(side=tk.LEFT, padx=2)
        tk.Label(sp_frame, text="Max:").pack(side=tk.LEFT, padx=(10,0))
        self.sp_y_max_var = tk.StringVar(value="auto")
        tk.Entry(sp_frame, textvariable=self.sp_y_max_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Apply and Reset buttons
        btn_frame = tk.Frame(plot_controls_frame)
        btn_frame.pack(fill=tk.X, pady=2)
        self.apply_ranges_button = tk.Button(btn_frame, text="Apply Plot Ranges", command=self.apply_plot_ranges, width=15)
        self.apply_ranges_button.pack(side=tk.LEFT, padx=5)
        self.reset_ranges_button = tk.Button(btn_frame, text="Reset to Auto", command=self.reset_plot_ranges, width=15)
        self.reset_ranges_button.pack(side=tk.LEFT, padx=5)
        
        # Create matplotlib figure with subplots
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Initialize empty plots
        self.ax_waveform.set_xlabel('Time (s)')
        self.ax_waveform.set_ylabel('Amplitude')
        self.ax_waveform.set_title('Green Noise Waveform')
        self.ax_waveform.grid(True)
        
        self.ax_spectrum.set_xlabel('Frequency (Hz)')
        self.ax_spectrum.set_ylabel('Magnitude')
        self.ax_spectrum.set_title('Green Noise Spectrum')
        self.ax_spectrum.grid(True)
        
        # Embed matplotlib figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.apply_theme(self.current_theme)

    def on_theme_changed(self, selected_theme):
        self.apply_theme(selected_theme)

    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            return

        self.current_theme = theme_name
        colors = self.themes[theme_name]
        self.root.configure(bg=colors["bg"])
        self._apply_theme_to_widget(self.root, colors)
        self._apply_theme_to_plots(colors)
        self.canvas.draw_idle()

        current_status = self.status_label.cget("text")
        if current_status == "Ready":
            self.status_label.config(fg=colors["status_fg"])

    def _apply_theme_to_widget(self, widget, colors):
        widget_class = widget.winfo_class()
        config_map = {}

        if widget_class in ("Frame", "Toplevel"):
            config_map = {"bg": colors["bg"]}
        elif widget_class == "LabelFrame":
            config_map = {"bg": colors["panel_bg"], "fg": colors["text"]}
        elif widget_class == "Label":
            config_map = {"bg": colors["panel_bg"], "fg": colors["text"]}
            if widget is self.status_label:
                config_map["fg"] = colors["status_fg"]
        elif widget_class == "Button":
            config_map = {
                "bg": colors["button_bg"],
                "fg": colors["button_fg"],
                "activebackground": colors["accent"],
                "activeforeground": colors["panel_bg"],
            }
            if widget is self.quit_button:
                config_map["fg"] = colors["danger"]
        elif widget_class == "Entry":
            config_map = {
                "bg": colors["entry_bg"],
                "fg": colors["entry_fg"],
                "insertbackground": colors["entry_fg"],
            }
        elif widget_class == "Scale":
            config_map = {
                "bg": colors["panel_bg"],
                "fg": colors["text"],
                "troughcolor": colors["surface_bg"],
                "activebackground": colors["accent"],
                "highlightbackground": colors["panel_bg"],
            }
        elif widget_class == "Menubutton":
            config_map = {
                "bg": colors["button_bg"],
                "fg": colors["button_fg"],
                "activebackground": colors["accent"],
                "activeforeground": colors["panel_bg"],
                "highlightbackground": colors["panel_bg"],
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
        elif widget_class == "Text":
            config_map = {
                "bg": colors["entry_bg"],
                "fg": colors["entry_fg"],
                "insertbackground": colors["entry_fg"],
            }

        if config_map:
            try:
                widget.config(**config_map)
            except tk.TclError:
                pass

        for child in widget.winfo_children():
            self._apply_theme_to_widget(child, colors)

    def _apply_theme_to_plots(self, colors):
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

        if hasattr(self, "noise_data"):
            self.update_waveform()
            self.update_spectrum()
    
    def on_volume_slider_changed(self, value):
        """Called when volume slider moves"""
        # Update amplitude to match (volume 0-100 maps to amplitude 0-1)
        amplitude = float(value) / 100.0
        self.amplitude_var.set(amplitude)
    
    def on_volume_entry_changed(self, event=None):
        """Called when volume entry is changed"""
        try:
            volume = float(self.volume_var.get())
            volume = max(0, min(100, volume))  # Clamp to 0-100
            self.volume_var.set(volume)
            # Update amplitude
            amplitude = volume / 100.0
            self.amplitude_var.set(amplitude)
        except ValueError:
            pass
    
    def on_amplitude_slider_changed(self, value):
        """Called when amplitude slider moves"""
        # Update volume to match (amplitude 0-1 maps to volume 0-100)
        volume = float(value) * 100.0
        self.volume_var.set(volume)
    
    def on_amplitude_entry_changed(self, event=None):
        """Called when amplitude entry is changed"""
        try:
            amplitude = float(self.amplitude_var.get())
            amplitude = max(0, min(1, amplitude))  # Clamp to 0-1
            self.amplitude_var.set(amplitude)
            # Update volume
            volume = amplitude * 100.0
            self.volume_var.set(volume)
        except ValueError:
            pass
        
    def generate_noise(self):
        try:
            sample_rate = int(self.sample_rate_var.get())
            duration = float(self.duration_var.get())
            amplitude = float(self.amplitude_var.get())
            
            # Create generator and generate noise
            generator = GreenNoiseGenerator(sample_rate, duration)
            self.noise_data = generator.generate_green_noise()
            
            # Apply amplitude scaling
            self.noise_data = self.noise_data * amplitude
            
            self.sample_rate = sample_rate
            self.duration = duration
            
            # Update plots
            self.update_waveform()
            self.update_spectrum()
            
            # Enable play button
            self.play_button.config(state=tk.NORMAL)
            
            self.status_label.config(text=f"Generated {duration}s of green noise")
            
        except ValueError as e:
            self.status_label.config(text="Invalid parameter values")
            return
    
    def update_waveform(self):
        """Update waveform plot"""
        self.ax_waveform.clear()
        time_axis = np.linspace(0, self.duration, len(self.noise_data))
        self.ax_waveform.plot(time_axis, self.noise_data, color=self.themes[self.current_theme]["waveform_line"])
        self.ax_waveform.set_xlabel('Time (s)')
        self.ax_waveform.set_ylabel('Amplitude')
        self.ax_waveform.set_title('Green Noise Waveform')
        self.ax_waveform.grid(True)
        
        # Apply range limits
        if self.waveform_x_min is not None and self.waveform_x_max is not None:
            self.ax_waveform.set_xlim(self.waveform_x_min, self.waveform_x_max)
        if self.waveform_y_min is not None and self.waveform_y_max is not None:
            self.ax_waveform.set_ylim(self.waveform_y_min, self.waveform_y_max)
            
        self.canvas.draw()
    
    def update_spectrum(self):
        """Update spectrum plot"""
        self.ax_spectrum.clear()
        fft_data = np.fft.rfft(self.noise_data)
        frequencies = np.fft.rfftfreq(len(self.noise_data), 1/self.sample_rate)
        
        self.ax_spectrum.plot(frequencies, np.abs(fft_data), color=self.themes[self.current_theme]["spectrum_line"])
        self.ax_spectrum.set_xlabel('Frequency (Hz)')
        self.ax_spectrum.set_ylabel('Magnitude')
        self.ax_spectrum.set_title('Green Noise Spectrum')
        self.ax_spectrum.grid(True)
        
        # Apply range limits
        if self.spectrum_x_min is not None and self.spectrum_x_max is not None:
            self.ax_spectrum.set_xlim(self.spectrum_x_min, self.spectrum_x_max)
        if self.spectrum_y_min is not None and self.spectrum_y_max is not None:
            self.ax_spectrum.set_ylim(self.spectrum_y_min, self.spectrum_y_max)
            
        self.canvas.draw()
    
    def apply_plot_ranges(self):
        """Apply user-specified plot ranges"""
        try:
            # Waveform X
            wf_x_min = self.wf_x_min_var.get().strip().lower()
            wf_x_max = self.wf_x_max_var.get().strip().lower()
            self.waveform_x_min = None if wf_x_min == "auto" else float(wf_x_min)
            self.waveform_x_max = None if wf_x_max == "auto" else float(wf_x_max)
            
            # Waveform Y
            wf_y_min = self.wf_y_min_var.get().strip().lower()
            wf_y_max = self.wf_y_max_var.get().strip().lower()
            self.waveform_y_min = None if wf_y_min == "auto" else float(wf_y_min)
            self.waveform_y_max = None if wf_y_max == "auto" else float(wf_y_max)
            
            # Spectrum X
            sp_x_min = self.sp_x_min_var.get().strip().lower()
            sp_x_max = self.sp_x_max_var.get().strip().lower()
            self.spectrum_x_min = None if sp_x_min == "auto" else float(sp_x_min)
            self.spectrum_x_max = None if sp_x_max == "auto" else float(sp_x_max)
            
            # Spectrum Y
            sp_y_min = self.sp_y_min_var.get().strip().lower()
            sp_y_max = self.sp_y_max_var.get().strip().lower()
            self.spectrum_y_min = None if sp_y_min == "auto" else float(sp_y_min)
            self.spectrum_y_max = None if sp_y_max == "auto" else float(sp_y_max)
            
            # Update plots if data exists
            if hasattr(self, 'noise_data'):
                self.update_waveform()
                self.update_spectrum()
                self.status_label.config(text="Plot ranges updated")
            
        except ValueError:
            self.status_label.config(text="Invalid plot range values")
    
    def reset_plot_ranges(self):
        """Reset plot ranges to auto"""
        self.wf_x_min_var.set("auto")
        self.wf_x_max_var.set("auto")
        self.wf_y_min_var.set("-1.0")
        self.wf_y_max_var.set("1.0")
        self.sp_x_min_var.set("0")
        self.sp_x_max_var.set("5000")
        self.sp_y_min_var.set("auto")
        self.sp_y_max_var.set("auto")
        self.apply_plot_ranges()
            
    def play_noise(self):
        """Play the generated noise"""
        if not hasattr(self, 'noise_data'):
            self.status_label.config(text="No noise data to play")
            return
        
        if self.playing:
            return
        
        self.playing = True
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Playing...")
        
        # Play audio in a separate thread
        self.audio_thread = threading.Thread(target=self._play_audio)
        self.audio_thread.start()
    
    def _play_audio(self):
        """Internal method to play audio"""
        try:
            p = pyaudio.PyAudio()
            
            # Apply current volume/amplitude setting
            amplitude = float(self.amplitude_var.get())
            scaled_noise = self.noise_data * amplitude
            
            # Convert to 16-bit integers
            audio_data = (scaled_noise * 32767).astype(np.int16)
            
            stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=self.sample_rate,
                          output=True)
            
            # Play audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if not self.playing:
                    break
                chunk = audio_data[i:i+chunk_size]
                stream.write(chunk.tobytes())
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            self.status_label.config(text=f"Error playing: {str(e)}")
        finally:
            self.playing = False
            self.play_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Playback finished")
    
    def stop_noise(self):
        """Stop playing noise"""
        self.playing = False
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
            
    def save_to_wav(self):
        if not hasattr(self, 'noise_data'):
            self.status_label.config(text="No noise data to save")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
            )
            
            if filename:
                sample_rate = int(self.sample_rate_var.get())
                duration = float(self.duration_var.get())
                
                generator = GreenNoiseGenerator(sample_rate, duration)
                generator.save_to_wav(filename)
                
                self.status_label.config(text=f"Saved to {filename}")
                
        except Exception as e:
            self.status_label.config(text=f"Error saving: {str(e)}")
    
    def show_command(self):
        """Show equivalent command line"""
        sample_rate = self.sample_rate_var.get()
        duration = self.duration_var.get()
        low_freq = self.low_freq_var.get()
        high_freq = self.high_freq_var.get()
        theme = self.current_theme
        
        cmd = (
            f"python {sys.argv[0]} --no-gui --sample-rate {sample_rate} "
            f"--duration {duration} --low-freq {low_freq} --high-freq {high_freq} "
            f"--theme {theme} --output output.wav"
        )
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Command Line Equivalent")
        dialog.geometry("700x200")
        dialog.transient(self.root)
        dialog.grab_set()

        colors = self.themes[self.current_theme]
        dialog.config(bg=colors["panel_bg"])
        
        # Label
        tk.Label(
            dialog,
            text="Equivalent command line:",
            font=("Arial", 10, "bold"),
            bg=colors["panel_bg"],
            fg=colors["text"],
        ).pack(pady=10)
        
        # Text widget with command
        text_frame = tk.Frame(dialog, bg=colors["panel_bg"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_widget = tk.Text(
            text_frame,
            height=3,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg=colors["entry_bg"],
            fg=colors["entry_fg"],
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert("1.0", cmd)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=colors["panel_bg"])
        button_frame.pack(pady=10)
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            self.root.update()
            copy_btn.config(text="Copied!", state=tk.DISABLED)
            self.root.after(1500, lambda: copy_btn.config(text="Copy to Clipboard", state=tk.NORMAL) if copy_btn.winfo_exists() else None)
        
        copy_btn = tk.Button(
            button_frame,
            text="Copy to Clipboard",
            command=copy_to_clipboard,
            width=20,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            activebackground=colors["accent"],
            activeforeground=colors["panel_bg"],
        )
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=10,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            activebackground=colors["accent"],
            activeforeground=colors["panel_bg"],
        ).pack(side=tk.LEFT, padx=5)
    
    def quit_app(self):
        """Quit the application"""
        if self.playing:
            self.stop_noise()
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
            self.root.destroy()

def command_line_mode(args):
    """Run in command line mode"""
    print(f"Generating green noise...")
    print(f"  Sample Rate: {args.sample_rate} Hz")
    print(f"  Duration: {args.duration} s")
    print(f"  Low Freq: {args.low_freq} Hz")
    print(f"  High Freq: {args.high_freq} Hz")
    
    generator = GreenNoiseGenerator(args.sample_rate, args.duration)
    
    if args.output:
        generator.save_to_wav(args.output)
        print(f"Saved to {args.output}")
    else:
        print("No output file specified. Use --output to save the noise.")

def main():
    parser = argparse.ArgumentParser(description='Green Noise Generator')
    parser.add_argument('--no-gui', action='store_true', help='Run in command line mode')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--duration', type=float, default=5.0, help='Duration in seconds (default: 5.0)')
    parser.add_argument('--low-freq', type=int, default=20, help='Low frequency in Hz (default: 20)')
    parser.add_argument('--high-freq', type=int, default=800, help='High frequency in Hz (default: 800)')
    parser.add_argument('--theme', type=str, default='light', choices=['light', 'dark', 'green', 'blues', 'ocean'], help='UI color theme (default: light)')
    parser.add_argument('--output', type=str, help='Output WAV file (command line mode only)')
    
    args = parser.parse_args()
    
    if args.no_gui:
        # Command line mode
        command_line_mode(args)
    else:
        # GUI mode
        root = tk.Tk()
        app = DataLoggerGUI(root)
        
        # Set values from command line args if provided
        if len(sys.argv) > 1:
            app.sample_rate_var.set(str(args.sample_rate))
            app.duration_var.set(str(args.duration))
            app.low_freq_var.set(str(args.low_freq))
            app.high_freq_var.set(str(args.high_freq))
            app.theme_var.set(args.theme)
            app.on_theme_changed(args.theme)
        
        root.mainloop()

if __name__ == "__main__":
    main()
