import json
import os
from pathlib import Path
import themes

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.aerominal'
        self.config_file = self.config_dir / 'config' / 'settings.json'
        self.default_config = {
            'window': {
                'opacity': 0.75,  # 75% opacity default
                'width': 800,
                'height': 600,
                'always_on_top': False
            },
            'appearance': {
                'theme': 'dark',
                'font_family': 'Consolas',
                'font_size': 11
            },
            'behavior': {
                'close_to_tray': False,
                'start_maximized': False,
                'shell_path': None, # Default shell path
                'show_system_info_on_startup': False # Display system info on startup
            },
            'auto_update': False,
            'first_run': True
        }
        
        self.load_config()
        
    def load_config(self):
        """Load configuration from file or create default"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True) # Ensure config directory exists
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with default config to pick up new settings
                self.config = {**self.default_config, **self.config}
                self.save_config() # Save merged config
            else:
                self.config = self.default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config
            self.save_config() # Save default config if loading fails
            
        # Load theme
        self.theme = themes.get_theme(self.get_setting('appearance', 'theme'))
        
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get_setting(self, *keys):
        """Get a setting value using a sequence of keys."""
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                # Return default from default_config if key not found in loaded config
                default_current = self.default_config
                for default_key in keys:
                    if isinstance(default_current, dict) and default_key in default_current:
                        default_current = default_current[default_key]
                    else:
                        return None # Should not happen if default_config is complete
                return default_current
        return current

    def set_setting(self, value, *keys):
        """Set a setting value using a sequence of keys."""
        current = self.config
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.save_config()
            
    def set_theme(self, theme_name):
        """Change theme and save configuration"""
        self.set_setting(theme_name, 'appearance', 'theme')
        self.theme = themes.get_theme(theme_name)
        
    def set_opacity(self, opacity):
        """Change opacity and save configuration"""
        self.set_setting(opacity, 'window', 'opacity')
        
    def set_font(self, font_family, font_size):
        """Change font and save configuration"""
        self.set_setting(font_family, 'appearance', 'font_family')
        self.set_setting(font_size, 'appearance', 'font_size')
