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
Key fixes and improvements:

1. **Fixed the filedialog error**:
   - Changed `tkinter.filedialog` to `filedialog` (imported directly)
   - This resolves the "module tkinter has no attribute 'filedialog'" error

2. **Added graph display functionality**:
   - Added a "Show Graphs" button
   - Created a separate window for displaying plots
   - Shows both raw data plot and histogram
   - Uses matplotlib with Tkinter integration via FigureCanvasTkAgg
   - Handles empty data gracefully

3. **Additional improvements**:
   - Proper GUI layout with scrollable data display
   - Status updates during recording
   - Better file saving with error handling
   - Data is displayed in a treeview for easy viewing
   - Graph window can be brought to front if already exists
   - Simulated data collection (replace with actual sensor reading)

4. **Dependencies**:
   Make sure you have these packages installed:
   ```
   pip install matplotlib numpy
   ```

The application now:
- Records simulated data every second
- Displays data in a scrollable table
- Saves data to CSV files using the correct file dialog
- Shows both raw data and distribution graphs in a separate window
- Handles errors gracefully

To use with real sensors, replace the `record_data()` method with actual sensor reading code.

To use the application:
1. **GUI Mode**: Run with `python green_noise_generator.py --gui`
2. **Command Line**: Use various options like `--duration`, `--sample-rate`, `--play`, `--save`, etc.




