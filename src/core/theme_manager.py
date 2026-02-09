
import json, os
from pathlib import Path

class ThemeManager:
    def __init__(self):
        self.base_dir = Path.home() / '.aerominal'
        self.official_dir = self.base_dir / 'themes' / 'official'
        self.user_dir = self.base_dir / 'themes' / 'user'
        for d in [self.official_dir, self.user_dir]: d.mkdir(parents=True, exist_ok=True)
        self.defaults = {
            'dark': {'background': '#000000', 'text_color': '#dcdcdc', 'input_bg': '#1a1a1a', 'prompt_color': '#569cd6', 'status_color': '#808080', 'selection_bg': '#264f78', 'accent_color': '#569cd6', 'titlebar_bg': '#000000'},
            'light': {'background': '#f8f8f8', 'text_color': '#2e2e2e', 'input_bg': '#ffffff', 'prompt_color': '#007acc', 'status_color': '#666666', 'selection_bg': '#b5d5ff', 'accent_color': '#007acc', 'titlebar_bg': '#f8f8f8'},
            'blue': {'background': '#0a1428', 'text_color': '#b4d0fd', 'input_bg': '#0f1c36', 'prompt_color': '#4fc1ff', 'status_color': '#6b8cae', 'selection_bg': '#1e3a5f', 'accent_color': '#4fc1ff', 'titlebar_bg': '#0a1428'},
            'green': {'background': '#0c160c', 'text_color': '#c8e6c8', 'input_bg': '#142114', 'prompt_color': '#4caf50', 'status_color': '#6b8c6b', 'selection_bg': '#1b3a1b', 'accent_color': '#4caf50', 'titlebar_bg': '#0c160c'},
            'purple': {'background': '#140c1c', 'text_color': '#e6d4ff', 'input_bg': '#1e1429', 'prompt_color': '#ba68c8', 'status_color': '#8b7b9c', 'selection_bg': '#3d2a4d', 'accent_color': '#ba68c8', 'titlebar_bg': '#140c1c'},
            'matrix': {'background': '#001100', 'text_color': '#00ff00', 'input_bg': '#002200', 'prompt_color': '#00ff00', 'status_color': '#008800', 'selection_bg': '#004400', 'accent_color': '#00ff00', 'titlebar_bg': '#001100'},
            'cat_mocha': {'background': '#1e1e2e', 'text_color': '#cdd6f4', 'input_bg': '#302d41', 'prompt_color': '#f38ba8', 'status_color': '#6c7086', 'selection_bg': '#45475a', 'accent_color': '#89b4fa', 'titlebar_bg': '#1e1e2e'},
            'cat_macchiato': {'background': '#1e2030', 'text_color': '#cad3f5', 'input_bg': '#363a4f', 'prompt_color': '#f4b8e4', 'status_color': '#6e738d', 'selection_bg': '#494d64', 'accent_color': '#8aadf4', 'titlebar_bg': '#1e2030'},
            'cat_frappe': {'background': '#303446', 'text_color': '#c6d0f5', 'input_bg': '#414559', 'prompt_color': '#f2d5cf', 'status_color': '#838ba7', 'selection_bg': '#51576d', 'accent_color': '#8caaee', 'titlebar_bg': '#303446'},
            'cat_latte': {'background': '#eff1f5', 'text_color': '#4c4f69', 'input_bg': '#e6e9ef', 'prompt_color': '#dc8a78', 'status_color': '#8c8fa1', 'selection_bg': '#ccd0da', 'accent_color': '#1e66f5', 'titlebar_bg': '#eff1f5'},
            'solarized_dark': {'background': '#002b36', 'text_color': '#93a1a1', 'input_bg': '#073642', 'prompt_color': '#b58900', 'status_color': '#586e75', 'selection_bg': '#073642', 'accent_color': '#268bd2', 'titlebar_bg': '#002b36'},
            'solarized_light': {'background': '#fdf6e3', 'text_color': '#657b83', 'input_bg': '#eee8d5', 'prompt_color': '#b58900', 'status_color': '#93a1a1', 'selection_bg': '#eee8d5', 'accent_color': '#268bd2', 'titlebar_bg': '#fdf6e3'},
            'dracula': {'background': '#282a36', 'text_color': '#f8f8f2', 'input_bg': '#1e1f29', 'prompt_color': '#ff79c6', 'status_color': '#6272a4', 'selection_bg': '#44475a', 'accent_color': '#bd93f9', 'titlebar_bg': '#282a36'},
            'nord': {'background': '#2e3440', 'text_color': '#d8dee9', 'input_bg': '#3b4252', 'prompt_color': '#88c0d0', 'status_color': '#81a1c1', 'selection_bg': '#434c5e', 'accent_color': '#5e81ac', 'titlebar_bg': '#2e3440'},
            'gruvbox_dark': {'background': '#282828', 'text_color': '#ebdbb2', 'input_bg': '#32302f', 'prompt_color': '#fabd2f', 'status_color': '#a89984', 'selection_bg': '#504945', 'accent_color': '#d79921', 'titlebar_bg': '#282828'},
            'gruvbox_light': {'background': '#fbf1c7', 'text_color': '#3c3836', 'input_bg': '#ebdbb2', 'prompt_color': '#d79921', 'status_color': '#7c6f64', 'selection_bg': '#d5c4a1', 'accent_color': '#b57614', 'titlebar_bg': '#fbf1c7'},
            'monokai': {'background': '#272822', 'text_color': '#f8f8f2', 'input_bg': '#32332a', 'prompt_color': '#f92672', 'status_color': '#75715e', 'selection_bg': '#49483e', 'accent_color': '#a6e22e', 'titlebar_bg': '#272822'},
            'amber': {'background': '#1a1300', 'text_color': '#ffdd99', 'input_bg': '#261d00', 'prompt_color': '#ffb300', 'status_color': '#cc9900', 'selection_bg': '#4d3900', 'accent_color': '#ffb300', 'titlebar_bg': '#1a1300'},
            'cyberpunk': {'background': '#0a0014', 'text_color': '#f2f2f2', 'input_bg': '#160028', 'prompt_color': '#ff00e6', 'status_color': '#00eaff', 'selection_bg': '#32004f', 'accent_color': '#00eaff', 'titlebar_bg': '#0a0014'},
            'cappuccino': {'background': '#1e1e28', 'text_color': '#dce0e8', 'input_bg': '#302d41', 'prompt_color': '#f5c2e7', 'status_color': '#6e6c7e', 'selection_bg': '#45475a', 'accent_color': '#f5c2e7', 'titlebar_bg': '#1e1e28'},
            'nge_unit01': {'background': '#2D003D', 'text_color': '#00FF00', 'input_bg': '#1A0024', 'prompt_color': '#FFD700', 'selection_bg': '#5A007A', 'status_color': '#CCCCCC', 'accent_color': '#00FF00', 'titlebar_bg': '#100015'},
            'nge_retro_computer': {'background': '#1A1A1A', 'text_color': '#FFA500', 'input_bg': '#2A2A2A', 'prompt_color': '#00FF00', 'selection_bg': '#CC8400', 'status_color': '#90EE90', 'accent_color': '#00FF00', 'titlebar_bg': '#000000'}
        }
        self._init_defaults()

    def _init_defaults(self):
        for name, data in self.defaults.items():
            with open(self.official_dir / f"{name}.json", 'w') as f: json.dump(data, f, indent=4)

    def get_theme(self, name):
        themes = {}
        for d in [self.official_dir, self.user_dir]:
            for f in d.glob('*.json'):
                try:
                    with open(f, 'r') as tf: themes[f.stem] = json.load(tf)
                except: pass
        return themes.get(name, themes.get('dark', self.defaults['dark']))

    def get_available_themes(self):
        themes = set(self.defaults.keys())
        for d in [self.official_dir, self.user_dir]: themes.update(f.stem for f in d.glob('*.json'))
        return sorted(list(themes))
