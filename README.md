# greener-noise
Green noise generator

## Description

1. **Tkinter GUI Interface**:
   - Clean, user-friendly interface with input fields for all parameters
   - Checkboxes for enabling different features (play, save, plots)
   - Progress indicator and status messages
   - Responsive layout that adapts to window size

2. **Command-line Arguments**:
   - `--gui` flag to launch GUI mode (default is CLI mode)
   - All parameters have corresponding CLI arguments
   - Full backward compatibility with existing command-line usage

3. **Enhanced Error Handling**:
   - Input validation for all parameters
   - User-friendly error messages
   - Graceful handling of exceptions during generation

4. **Improved Functionality**:
   - Better filtering that handles edge cases
   - Proper parameter bounds checking
   - File dialog integration for saving audio files
   - Progress indicators during operations

5. **Usage Examples**:
   - **CLI mode (default)**: `uv run green-noise.py --low-freq 100 --high-freq 800 --save`
   - **GUI mode**: `uv run green-noise.py --gui`

The GUI provides a complete interface for setting all parameters and choosing which operations to perform, while the CLI mode maintains 
full backward compatibility with existing usage patterns.

## Functionality

This enhanced version of the green noise generator includes:

1. **Complete GUI functionality** with proper validation and error handling
2. **Command line interface** with comprehensive argument parsing
3. **Robust input validation** for all parameters
4. **Proper audio generation** with frequency filtering
5. **All requested features** including play, save, spectrum, and waveform display
6. **Error handling** throughout the application
7. **Clean separation of concerns** between GUI and audio generation logic

The code now properly handles:
- Input validation and error messages
- Audio file saving in WAV format
- Real-time playback using sounddevice
- Spectrum and waveform visualization
- Both GUI and command-line interfaces
- Proper normalization to prevent audio clipping
- Frequency filtering for true green noise characteristics

To use the application:
1. **GUI Mode**: Run with `python green_noise_generator.py --gui`
2. **Command Line**: Use various options like `--duration`, `--sample-rate`, `--play`, `--save`, etc.

