import os, sys
if os.name == 'nt':
    import ctypes
    hWnd = ctypes.WinDLL('kernel32').GetConsoleWindow()
    if hWnd: ctypes.WinDLL('user32').ShowWindow(hWnd, 0)

from src.main import main
if __name__ == "__main__":
    main()
