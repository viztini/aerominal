# aerominal

![aerominal Banner](./banner.png)

# aerominal Terminal Emulator [ALPHA]

## Development Status

**Alpha Build** — This is an early development version of **aerominal**.
Features may be incomplete and stability is not guaranteed.
Please report any issues you encounter.

A modern, transparent terminal emulator for **Windows** and **Linux**
(macOS support is possible but currently untested).

---

## Overview

aerominal is a lightweight and customizable terminal emulator built with **Python** and **Tkinter**.
It features a clean, transparent interface with theme support and modern UI aesthetics.

---

## Features

* **Transparent Background** — Adjustable opacity with acrylic-style blur effects
* **Custom Themes** — Multiple built-in color schemes, easily extendable with your own
* **Lightweight** — Minimal resource usage, powered by Python and Tkinter
* **Hidden CMD Process (Windows)** — Executes commands without showing a console window
* **Themed Title Bar** — Title bar colors adapt to the selected theme
* **Clean Interface** — No visible scrollbar (scroll with mouse wheel)
* **Right-Click Context Menu** — Quick access to themes, settings, and opacity controls

---

## Keyboard Shortcuts

* `Ctrl + L` — Clear terminal output
* `Ctrl + C` — Copy selected text
* `Ctrl + V` — Paste into input
* `Ctrl + Q` — Exit application
* `Up / Down` — Navigate command history
* `Enter` — Execute command

*More shortcuts planned for future updates.*

---

## Installation

### Download Latest Release

(Windows only at the moment)

### Run from Source (Linux / Cross-Platform)

```bash
python aerominal.py
```

### Build an Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name aerominal aerominal.py
```

---

## Customization

### Creating Custom Themes

Add your theme to `themes.py`:

```python
'my_theme': {
    'background': '#1a1a1a',
    'text_color': '#ffffff',
    'input_bg': '#2a2a2a',
    'prompt_color': '#ff6b6b',
    'status_color': '#888888',
    'selection_bg': '#3a3a3a',
    'accent_color': '#ff6b6b',
    'titlebar_bg': '#2a2a2a'
}
```

Your theme will automatically appear under **Right-Click → Themes**.

---

### Modifying Settings

User settings are stored in:

```
~/.aerominal/config.json
```

Options include:

* Window opacity (0.5–1.0)
* Theme selection
* Font settings
* Window size & position

---

## Built-In Themes

* **Dark** — Pure black with blue accents
* **Light** — Soft gray with blue highlights
* **Blue** — Deep blue with cyan accents
* **Green** — Classic terminal-green style
* **Purple** — Dark purple with lavender tones
* **Matrix** — Black with neon-green text

---

## Usage

* **Right-click** anywhere for settings and themes
* **Mouse wheel** scrolls through output
* **Themes** can be switched instantly
* **Opacity** adjusts from the right-click menu
* **Command history** persists during session

---

## Project Structure

```
aerominal/
├── aerominal.py      # Main application logic
├── config.py         # Configuration management
├── themes.py         # Theme definitions
├── build.py          # Build script
└── requirements.txt  # Dependencies
```

---

## Technical Details

* Built entirely with **Tkinter** for cross-platform compatibility
* Uses `subprocess` with `CREATE_NO_WINDOW` on Windows to hide the CMD window
* Custom transparency and theme system
* Thread-safe output handling
* Grid-based UI layout for stable resizing

---

## Requirements

* Python 3.7+
* Windows 10/11 or Linux
* Tkinter (usually included)

*Note: The project is written in Python and **may run on macOS**,
but it is not currently supported or tested.*

---

## Building from Source (Advanced)

Using PyInstaller manually:

```bash
pyinstaller --onefile --windowed --name aerominal \
  --add-data "config.py;." \
  --add-data "themes.py;." \
  aerominal.py
```

---

## Open Source

You are encouraged to:

* Modify and extend the code
* Create and share custom themes
* Improve the functionality
* Report and fix bugs
* Port to additional operating systems

The project is designed to be easy to extend, especially `themes.py` and `aerominal.py`.

---

**aerominal terminal — clean, modern, customizable.**

---
