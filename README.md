# aerominal

![aerominal Banner](./banner.png)

# aerominal Terminal [STILL IN DEVELOPMENT]

## Development Status

**Alpha Build** - This is an early development version of aerominal. Features may be incomplete and stability is not guaranteed. Please report any issues you encounter.

A Modern, Transparent Terminal Emulator for Windows

## Overview

A lightweight, customizable terminal emulator built with Python and Tkinter. Features a clean, transparent interface with theme support and modern aesthetics.

## Features

- **Transparent Background** - Adjustable opacity with acrylic-style effects
- **Custom Themes** - Multiple built-in color schemes with easy customization
- **Lightweight** - Minimal resource usage using Python and Tkinter
- **Hidden CMD Process** - Runs Windows commands in background without showing console window
- **Theme-Based Title Bar** - Title bar colors that match your selected theme
- **Clean Interface** - No visible scrollbar (mouse wheel scrolling only)
- **Right-Click Context Menu** - Quick access to settings and themes

## Current Keyboard Shortcuts

- `Ctrl + L` - Clear terminal output
- `Ctrl + C` - Copy selected text
- `Ctrl + V` - Paste text into input
- `Ctrl + Q` - Exit application
- `Up/Down` - Navigate command history
- `Enter` - Execute command

*Additional keyboard shortcuts are planned for future updates*

## Installation

### Run from Source
```bash
python aerominal.py
```

### Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name aerominal aerominal.py
```

## Customization

### Creating Custom Themes

Edit `themes.py` to add your own color schemes:

```python
'my_theme': {
    'background': '#1a1a1a',        # Main background
    'text_color': '#ffffff',        # Text color
    'input_bg': '#2a2a2a',         # Input field background
    'prompt_color': '#ff6b6b',     # Prompt symbol color
    'status_color': '#888888',     # Status bar text
    'selection_bg': '#3a3a3a',     # Selected text background
    'accent_color': '#ff6b6b',     # Accent color for highlights
    'titlebar_bg': '#2a2a2a'       # Title bar color (Windows 10/11)
}
```

Your custom theme will automatically appear in the right-click context menu under Themes.

### Modifying Settings

Configuration is stored in `~/.aerominal/config.json` and includes:
- Window opacity (0.5 to 1.0)
- Theme preferences
- Font settings
- Window size and position

## Built-in Themes

- **Dark** - Pure black with blue accents
- **Light** - Light gray with blue highlights
- **Blue** - Dark blue with cyan accents
- **Green** - Dark green with bright green accents
- **Purple** - Dark purple with lavender accents
- **Matrix** - Classic black with green text

## Usage

- **Right-click** anywhere in the terminal for the context menu
- **Mouse wheel** scrolls through output (no visible scrollbar)
- **Change themes** instantly via right-click -> Themes
- **Adjust opacity** via right-click -> Opacity
- **Command history** is maintained during session

## Project Structure

```
aerominal/
├── aerominal.py          # Main application logic
├── config.py            # Configuration management
├── themes.py            # Theme definitions and colors
├── build.py             # Build script for executable
└── requirements.txt     # Python dependencies
```

## Technical Details

- Built with Python's Tkinter for cross-platform compatibility
- Uses subprocess with CREATE_NO_WINDOW flag to hide CMD windows
- Implements custom transparency and theme system
- Thread-safe output handling for smooth performance
- Grid-based layout for stable window resizing

## Requirements

- Python 3.7+
- Windows 10/11 (for best transparency effects)
- Tkinter (usually included with Python)

## Building from Source

The included `build.py` script provides a GUI interface for creating executables, or use the command line:

```bash
pyinstaller --onefile --windowed --name aerominal --add-data "config.py;." --add-data "themes.py;." aerominal.py
```

## Open Source

This project is open source. You're encouraged to:
- Modify the code to suit your needs
- Create and share custom themes
- Improve the functionality
- Fix bugs and issues

The code is structured to be easily modifiable, particularly the theme system in `themes.py` and the main application logic in `aerominal.py`.

---

aerominal Terminal - Clean, customizable terminal emulator for Windows
