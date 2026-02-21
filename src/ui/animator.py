from PyQt6.QtCore import QVariantAnimation, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor

class ThemeAnimator:
    def __init__(self, app):
        self.app = app
        self.duration = 300

    def animate_theme_change(self, old_theme, new_theme):
        self.anim = QVariantAnimation()
        self.anim.setDuration(self.duration)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        
        def update_colors(value):
            current_theme = {}
            for key in ['background', 'text_color', 'input_bg', 'prompt_color', 'selection_bg']:
                start_color = QColor(old_theme[key])
                end_color = QColor(new_theme[key])
                
                r = start_color.red() + (end_color.red() - start_color.red()) * value
                g = start_color.green() + (end_color.green() - start_color.green()) * value
                b = start_color.blue() + (end_color.blue() - start_color.blue()) * value
                
                current_theme[key] = QColor(int(r), int(g), int(b)).name()
            
            self.app.apply_theme_colors(current_theme)

        self.anim.valueChanged.connect(update_colors)
        self.anim.start()

    def animate_opacity_change(self, start_opacity, end_opacity):
        self.opacity_anim = QPropertyAnimation(self.app, b"windowOpacity")
        self.opacity_anim.setDuration(self.duration)
        self.opacity_anim.setStartValue(start_opacity)
        self.opacity_anim.setEndValue(end_opacity)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_anim.finished.connect(lambda: self.app.config.set_opacity(end_opacity))
        self.opacity_anim.start()

