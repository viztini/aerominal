### aerominal

aerominal is a customizable terminal emulator built with Python and Tkinter.

## Features

*   Customizable themes (including new Neon Genesis Evangelion inspired themes!)
*   Adjustable opacity
*   Configurable font family and size
*   Adjustable window dimensions (width, height)
*   Option to start maximized
*   Configurable default shell path
*   First-run setup for auto-update preference (auto-update feature is currently non-functional)
*   Displays basic system information (configurable to show on startup)
*   **Scrollable Settings Window:** All settings are now accessible via a scrollable window.
*   **Improved Context Menu:** The right-click context menu now dismisses automatically when clicking outside of it.
*   **Live Time Display:** The bottom right of the status bar now displays the current time, updated every second.
*   **Persistent Input Focus:** The input bar automatically regains focus when the application window is reactivated, so you don't have to click it to type commands.

## Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/viztini/aerominal.git
    cd aerominal
    ```
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

Or just downlood the Windows executables.

## Usage

Run aerominal using the Windows executables.

To run aerominal:
```bash
source venv/bin/activate
python3 aerominal.py
```

## Building Executables

### Linux

To build a standalone executable for Linux:
```bash
source venv/bin/activate
pyinstaller --onefile --windowed --icon=logo.png aerominal.py
```
The executable will be found in the `dist` directory.

### Windows

To build a standalone executable for Windows (requires a Windows environment):
```bash
pyinstaller --onefile --windowed --icon=aerominal.ico aerominal.py
```
The executable will be found in the `dist` directory.

## Configuration

Aerominal stores its configuration in `~/.aerominal/config/settings.json`.
Themes are stored in `~/.aerominal/themes/official/` and `~/.aerominal/themes/user/`.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests.
