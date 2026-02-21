
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import QApplication
from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager
from src.ui.app import AerominalApp

def main():
    app = QApplication(sys.argv)
    cfg = ConfigManager()
    pm = ProcessManager(cfg)
    window = AerominalApp(cfg, pm)
    window.run()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
