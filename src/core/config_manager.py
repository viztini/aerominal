
import json, os
from pathlib import Path
from .theme_manager import ThemeManager

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.aerominal'
        self.config_file = self.config_dir / 'config' / 'settings.json'
        self.default_config = {
            'window': {'opacity': 0.75, 'width': 950, 'height': 600, 'always_on_top': False, 'start_maximized': False},
            'appearance': {'theme': 'dark', 'font_family': 'Consolas', 'font_size': 11, 'show_ansi_colors': True},
            'behavior': {'close_to_tray': False, 'shell_path': None, 'show_system_info_on_startup': False},
            'auto_update': False, 'first_run': True
        }
        self.load_config()

    def load_config(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = {**self.default_config, **json.load(f)}
            else:
                self.config = self.default_config
            self.save_config()
        except:
            self.config = self.default_config
        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_theme(self.get_setting('appearance', 'theme'))

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_setting(self, *keys):
        curr = self.config
        for k in keys:
            if isinstance(curr, dict) and k in curr: curr = curr[k]
            else:
                curr = self.default_config
                for dk in keys:
                    if isinstance(curr, dict) and dk in curr: curr = curr[dk]
                    else: return None
                return curr
        return curr

    def set_setting(self, val, *keys):
        curr = self.config
        for k in keys[:-1]: curr = curr.setdefault(k, {})
        curr[keys[-1]] = val
        self.save_config()

    def set_theme(self, name):
        self.set_setting(name, 'appearance', 'theme')
        self.theme = self.theme_manager.get_theme(name)

    def set_opacity(self, val):
        self.set_setting(val, 'window', 'opacity')
