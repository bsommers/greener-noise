## Installation Requirements:

```bash
pip install numpy sounddevice scipy matplotlib
```

## Usage Examples:

1. **Generate 5-second green noise with default settings:**
```bash
python green_noise.py
```

2. **Generate 10-second green noise with custom frequency range:**
```bash
python green_noise.py --duration 10 --low_freq 100 --high_freq 1000 --amplitude 0.7
```

3. **Generate and play green noise:**
```bash
python green_noise.py --play --low_freq 50 --high_freq 1500
```

4. **Generate, save, and plot:**
```bash
python green_noise.py --save --plot --low_freq 20 --high_freq 500
```

## Features:

- **Tunable Parameters**: Adjust frequency range, amplitude, and duration
- **Multiple Output Options**: Play directly, save to WAV file, or plot spectrum
- **Band-pass Filtering**: Creates true green noise characteristics
- **Flexible Frequency Range**: Customizable low and high frequency limits
- **Audio Quality**: Uses proper sample rate and normalization
- **Spectrum Analysis**: Visualize the frequency content of generated noise

## Green Noise Characteristics:

Green noise has a power spectrum that decreases at 6 dB per octave, making it sound more balanced to human hearing compared 
to white noise. This implementation creates a band-pass filtered version that emphasizes mid-range frequencies while 
attenuating extremes.

The program allows you to adjust:
- **Duration**: How long the noise lasts
- **Frequency Range**: Low and high frequency limits (50Hz to 2000Hz by default)
- **Amplitude**: Volume level (0.0 to 1.0)
- **Sample Rate**: Audio quality (44.1kHz default)
