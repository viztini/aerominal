
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager
from src.ui.app import AerominalApp

def main():
    cfg = ConfigManager()
    pm = ProcessManager(cfg)
    app = AerominalApp(cfg, pm)
    app.run()

if __name__ == "__main__":
    main()
