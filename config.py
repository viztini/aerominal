import json
import os
from pathlib import Path
import themes

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.aerominal'
        self.config_file = self.config_dir / 'config.json'
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
                'start_maximized': False
            }
        }
        
        self.load_config()
        
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config
                self.save_config()
        except:
            self.config = self.default_config
            
        # Apply loaded config
        self.opacity = self.config['window']['opacity']
        self.theme_name = self.config['appearance']['theme']
        self.font_family = self.config['appearance']['font_family']
        self.font_size = self.config['appearance']['font_size']
        self.always_on_top = self.config['window']['always_on_top']
        
        # Load theme
        self.theme = themes.get_theme(self.theme_name)
        
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def set_theme(self, theme_name):
        """Change theme and save configuration"""
        self.theme_name = theme_name
        self.theme = themes.get_theme(theme_name)
        self.config['appearance']['theme'] = theme_name
        self.save_config()
        
    def set_opacity(self, opacity):
        """Change opacity and save configuration"""
        self.opacity = opacity
        self.config['window']['opacity'] = opacity
        self.save_config()
        
    def set_font(self, font_family, font_size):
        """Change font and save configuration"""
        self.font_family = font_family
        self.font_size = font_size
        self.config['appearance']['font_family'] = font_family
        self.config['appearance']['font_size'] = font_size
        self.save_config()