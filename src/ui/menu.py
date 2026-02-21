from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

class CustomMenu(QMenu):
    def __init__(self, master, theme, font=None):
        super().__init__(master)
        self.theme = theme
        self.update_theme(theme)

    def add_command(self, label=None, command=None, **kwargs):
        action = QAction(label, self)
        if command:
            action.triggered.connect(command)
        self.addAction(action)

    def add_separator(self, **kwargs):
        self.addSeparator()

    def add_cascade(self, label=None, menu=None, **kwargs):
        if menu:
            menu.setTitle(label)
            self.addMenu(menu)

    def update_theme(self, theme):
        self.theme = theme
        bg = theme['background']
        fg = theme['text_color']
        sel_bg = theme['selection_bg']
        
        # Apply style sheet for themed look
        self.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {theme.get('status_color', '#444444')};
            }}
            QMenu::item:selected {{
                background-color: {sel_bg};
            }}
        """)

    def post(self, x, y):
        self.exec(self.master.mapToGlobal(self.master.rect().topLeft()) + self.master.mapFromGlobal(self.master.cursor().pos()))

    def unpost(self):
        self.close()
