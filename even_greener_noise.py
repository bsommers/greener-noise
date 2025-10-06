import tkinter as tk
from tkinter import filedialog
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
        self.root.geometry("1200x800")
        
        self.playing = False
        self.audio_thread = None
        
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
        tk.Entry(params_frame, textvariable=self.high_freq_var, width=15).pack(anchor=tk.W)
        
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
        
        # Status label
        self.status_label = tk.Label(left_panel, text="Ready", fg="blue", wraplength=180)
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Right panel for plots
        right_panel = tk.Frame(container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure with subplots
        self.fig, (self.ax_waveform, self.ax_spectrum) = plt.subplots(2, 1, figsize=(8, 8))
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
        
    def generate_noise(self):
        try:
            sample_rate = int(self.sample_rate_var.get())
            duration = float(self.duration_var.get())
            
            # Create generator and generate noise
            generator = GreenNoiseGenerator(sample_rate, duration)
            self.noise_data = generator.generate_green_noise()
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
        self.ax_waveform.plot(time_axis, self.noise_data)
        self.ax_waveform.set_xlabel('Time (s)')
        self.ax_waveform.set_ylabel('Amplitude')
        self.ax_waveform.set_title('Green Noise Waveform')
        self.ax_waveform.grid(True)
        self.canvas.draw()
    
    def update_spectrum(self):
        """Update spectrum plot"""
        self.ax_spectrum.clear()
        fft_data = np.fft.rfft(self.noise_data)
        frequencies = np.fft.rfftfreq(len(self.noise_data), 1/self.sample_rate)
        
        self.ax_spectrum.plot(frequencies, np.abs(fft_data))
        self.ax_spectrum.set_xlabel('Frequency (Hz)')
        self.ax_spectrum.set_ylabel('Magnitude')
        self.ax_spectrum.set_title('Green Noise Spectrum')
        self.ax_spectrum.grid(True)
        self.ax_spectrum.set_xlim(0, min(self.sample_rate/2, 5000))  # Limit x-axis for better visualization
        self.canvas.draw()
            
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
            
            # Convert to 16-bit integers
            audio_data = (self.noise_data * 32767).astype(np.int16)
            
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
        
        root.mainloop()

if __name__ == "__main__":
    main()
