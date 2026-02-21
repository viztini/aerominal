import os, sys, ctypes, re
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QLabel, QApplication, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QIcon, QAction

from ..core.ansi_parser import ANSIParser
from .animator import ThemeAnimator
from .menu import CustomMenu

class AerominalApp(QMainWindow):
    def __init__(self, config, process_mgr):
        super().__init__()
        self.config = config
        self.pm = process_mgr
        self.animator = ThemeAnimator(self)
        self.setWindowTitle("aerominal")
        
        self.history = []
        self.history_idx = -1
        self.temp_input = ""
        
        self.setup_ui()
        self.set_window_icon()
        self.update_title_bar_color()
        self.pm.start()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_output)
        self.timer.start(10)

    def setup_ui(self):
        width = int(self.config.get_setting('window', 'width'))
        height = int(self.config.get_setting('window', 'height'))
        self.resize(width, height)
        self.setWindowOpacity(self.config.get_setting('window', 'opacity'))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        theme = self.config.theme
        font_family = self.config.get_setting('appearance', 'font_family')
        font_size = int(self.config.get_setting('appearance', 'font_size'))
        self.app_font = QFont(font_family, font_size)

        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.txt.setFont(self.app_font)
        self.txt.setFrameStyle(0)
        self.txt.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.txt.customContextMenuRequested.connect(self.show_context_menu)
        self.txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.input_container = QWidget()
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(10, 5, 10, 5)

        self.prompt = QLabel(self.get_pwd())
        self.prompt.setFont(self.app_font)
        
        self.input = QLineEdit()
        self.input.setFont(self.app_font)
        self.input.setFrame(False)
        self.input.returnPressed.connect(self.send_cmd)
        
        self.input_layout.addWidget(self.prompt)
        self.input_layout.addWidget(self.input)

        self.layout.addWidget(self.txt)
        self.layout.addWidget(self.input_container)

        self.apply_theme_colors(theme)
        self.input.setFocus()

        # Scrollbar Fade Setup
        self.sb = self.txt.verticalScrollBar()
        self.sb_effect = QGraphicsOpacityEffect(self.sb)
        self.sb.setGraphicsEffect(self.sb_effect)
        self.sb_effect.setOpacity(0.0)
        self.sb_anim = QPropertyAnimation(self.sb_effect, b"opacity")
        self.sb_anim.setDuration(200)
        
        self.setMouseTracking(True)
        central_widget.setMouseTracking(True)
        self.txt.setMouseTracking(True)
        self.txt.viewport().setMouseTracking(True)
        self.txt.viewport().installEventFilter(self)
        self.txt.installEventFilter(self)

        # Shortcuts
        self.clear_action = QAction(self)
        self.clear_action.setShortcut("Ctrl+L")
        self.clear_action.triggered.connect(self.clear_screen)
        self.addAction(self.clear_action)

    def set_window_icon(self):
        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            ico_path = os.path.join(base_dir, 'src', 'assets', 'aerominal.ico')
            if os.path.exists(ico_path):
                self.setWindowIcon(QIcon(ico_path))
        except Exception as e:
            print(f"Icon loading error: {e}")

    def update_title_bar_color(self):
        if os.name != 'nt': return
        try:
            bg_color = self.config.theme.get('titlebar_bg', self.config.theme['background']).lstrip('#')
            r, g, b = int(bg_color[:2], 16), int(bg_color[2:4], 16), int(bg_color[4:], 16)
            colorref = (b << 16) | (g << 8) | r
            
            hwnd = self.winId().as_shard_ptr().get() if hasattr(self.winId(), 'as_shard_ptr') else int(self.winId())
            
            DWMWA_CAPTION_COLOR = 35
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_CAPTION_COLOR, 
                ctypes.byref(ctypes.c_int(colorref)), 
                4
            )
        except Exception as e:
            print(f"Failed to update title bar: {e}")

    def get_pwd(self):
        cwd = getattr(self.pm, 'cwd', os.getcwd())
        if os.name == 'nt':
            return cwd + ">"
        return cwd.replace(os.path.expanduser('~'), '~') + " ❯"

    def apply_theme_colors(self, theme):
        bg = theme['background']
        fg = theme['text_color']
        input_bg = theme['input_bg']
        prompt_fg = theme['prompt_color']
        sel_bg = theme['selection_bg']

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {fg};
            }}
            QTextEdit {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {sel_bg};
            }}
            QLineEdit {{
                background-color: {input_bg};
                color: {fg};
            }}
            QLabel {{
                color: {prompt_fg};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {bg};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {sel_bg};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                border: none;
                background: none;
                color: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.update_title_bar_color()

    def show_context_menu(self, pos):
        menu = CustomMenu(self, self.config.theme)
        menu.add_command("Copy", self.txt.copy)
        menu.add_command("Paste", self.input.paste)
        menu.add_separator()
        menu.add_command("Clear", self.clear_screen)
        
        tm = CustomMenu(self, self.config.theme)
        for t in self.config.theme_manager.get_available_themes():
            tm.add_command(t, lambda _, name=t: self.change_theme(name))
        menu.add_cascade("Themes", tm)
        
        om = CustomMenu(self, self.config.theme)
        for o in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            om.add_command(f"{int(o*100)}%", lambda _, val=o: self.change_opacity(val))
        menu.add_cascade("Opacity", om)
        
        menu.add_separator()
        menu.add_command("Exit", QApplication.quit)
        
        menu.exec(self.txt.mapToGlobal(pos))

    def change_theme(self, name):
        old_theme = self.config.theme
        self.config.set_theme(name)
        new_theme = self.config.theme
        self.animator.animate_theme_change(old_theme, new_theme)

    def change_opacity(self, val):
        self.animator.animate_opacity_change(self.windowOpacity(), val)

    def clear_screen(self):
        self.txt.clear()

    def send_cmd(self):
        cmd = self.input.text()
        if cmd in ['clear', 'cls']:
            self.clear_screen()
        elif cmd:
            if not self.history or self.history[-1] != cmd:
                self.history.append(cmd)
            self.history_idx = -1
            self.pm.write(cmd)
        self.input.clear()
        self.prompt.setText(self.get_pwd())

    def update_output(self):
        show_colors = self.config.get_setting('appearance', 'show_ansi_colors')
        while not self.pm.output_queue.empty():
            line = self.pm.output_queue.get()
            if '\f' in line:
                self.clear_screen()
                line = line.split('\f')[-1]
            
            line = re.sub(r' & echo\.? & echo __CWD__:[^\s\n]*', '', line)

            if "__CWD__:" in line:
                line = line.split("__CWD__:", 1)[0]
                self.prompt.setText(self.get_pwd())
            
            if not line: continue
            
            if show_colors:
                self.insert_ansi(line)
            else:
                self.txt.insertPlainText(ANSIParser.strip(line))
            
            self.txt.moveCursor(QTextCursor.MoveOperation.End)
        
        # Only show scrollbar after 250 lines
        if self.txt.document().blockCount() > 250:
            self.txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            self.txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def eventFilter(self, obj, event):
        if (obj == self.txt or obj == self.txt.viewport()) and event.type() == QEvent.Type.MouseMove:
            pos = event.pos()
            if obj == self.txt.viewport():
                # Map viewport pos to text edit pos if needed, but width check is enough
                x = pos.x()
                distance_from_right = self.txt.viewport().width() - x
            else:
                distance_from_right = self.txt.width() - pos.x()
            
            if distance_from_right < 60 and self.txt.document().blockCount() > 250:
                if self.sb_anim.endValue() != 1.0 or self.sb_anim.state() == QPropertyAnimation.State.Stopped:
                    self.sb_anim.stop()
                    self.sb_anim.setEndValue(1.0)
                    self.sb_anim.start()
                    self.sb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            else:
                if self.sb_anim.endValue() != 0.0 or self.sb_anim.state() == QPropertyAnimation.State.Stopped:
                    self.sb_anim.stop()
                    self.sb_anim.setEndValue(0.0)
                    self.sb_anim.start()
                    self.sb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        return super().eventFilter(obj, event)

    def insert_ansi(self, text):
        cursor = self.txt.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        for type, val in ANSIParser.parse(text):
            if type == 'text':
                cursor.insertText(val, self.current_format if hasattr(self, 'current_format') else QTextCharFormat())
            elif type == 'color':
                self.current_format = QTextCharFormat()
                self.current_format.setForeground(QColor(self.get_contrast_color(val)))
            elif type == 'reset':
                self.current_format = QTextCharFormat()
                
        self.txt.setTextCursor(cursor)

    def get_contrast_color(self, color):
        try:
            bg = self.config.theme['background'].lstrip('#')
            bg_lum = int(bg[:2],16)*0.299 + int(bg[2:4],16)*0.587 + int(bg[4:],16)*0.114
            return 'white' if bg_lum < 40 and color == 'black' else color
        except: return color

    def run(self):
        self.show()

