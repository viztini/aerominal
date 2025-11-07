THEMES = {
    'dark': {
        'background': '#000000',  # Pure black
        'text_color': '#dcdcdc',
        'input_bg': '#1a1a1a',
        'prompt_color': '#569cd6',
        'status_color': '#808080',
        'selection_bg': '#264f78',
        'accent_color': '#569cd6'
    },
    'light': {
        'background': '#f8f8f8',
        'text_color': '#2e2e2e',
        'input_bg': '#ffffff',
        'prompt_color': '#007acc',
        'status_color': '#666666',
        'selection_bg': '#b5d5ff',
        'accent_color': '#007acc'
    },
    'blue': {
        'background': '#0a1428',
        'text_color': '#b4d0fd',
        'input_bg': '#0f1c36',
        'prompt_color': '#4fc1ff',
        'status_color': '#6b8cae',
        'selection_bg': '#1e3a5f',
        'accent_color': '#4fc1ff'
    },
    'green': {
        'background': '#0c160c',
        'text_color': '#c8e6c8',
        'input_bg': '#142114',
        'prompt_color': '#4caf50',
        'status_color': '#6b8c6b',
        'selection_bg': '#1b3a1b',
        'accent_color': '#4caf50'
    },
    'purple': {
        'background': '#140c1c',
        'text_color': '#e6d4ff',
        'input_bg': '#1e1429',
        'prompt_color': '#ba68c8',
        'status_color': '#8b7b9c',
        'selection_bg': '#3d2a4d',
        'accent_color': '#ba68c8'
    },
    'matrix': {
        'background': '#001100',
        'text_color': '#00ff00',
        'input_bg': '#002200',
        'prompt_color': '#00ff00',
        'status_color': '#008800',
        'selection_bg': '#004400',
        'accent_color': '#00ff00'
    }
}

def get_theme(theme_name):
    """Get theme by name, fallback to dark if not found"""
    return THEMES.get(theme_name, THEMES['dark'])

def get_available_themes():
    """Get list of available theme names"""
    return list(THEMES.keys())