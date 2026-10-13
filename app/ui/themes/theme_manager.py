from pathlib import Path


class ThemeManager:
    THEMES = ("dark", "light")

    def __init__(self, window):
        self.window = window
        self.current_theme = "dark"

    def set_theme(self, theme):
        if theme not in self.THEMES:
            return
        path = Path(__file__).parent / f"{theme}.qss"
        self.window.setStyleSheet(path.read_text(encoding="utf-8"))
        self.current_theme = theme
