from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QMenu

from pathlib import Path


class Header(QFrame):
    new_requested = Signal()
    export_requested = Signal()
    language_requested = Signal(str)
    theme_requested = Signal(str)
    close_requested = Signal()
    minimize_requested = Signal()
    fullscreen_requested = Signal()
    github_preview_requested = Signal()

    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setObjectName("title-bar")
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 10, 10)
        layout.setSpacing(8)

        self.logo_placeholder = QLabel()
        self.logo_placeholder.setObjectName("brand-logo")
        self.logo_placeholder.setFixedSize(40, 40)
        self.logo_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = Path(__file__).resolve().parents[3] / "assets" / "img" / "1.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_placeholder.setPixmap(
                pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        self.brand_title = QLabel("ReadMe Hero")
        self.brand_title.setObjectName("brand-title")
        layout.addWidget(self.logo_placeholder)
        layout.addWidget(self.brand_title)
        layout.addStretch()

        self.language_button = QPushButton("EN")
        self.language_button.setObjectName("header-control")
        self.language_button.clicked.connect(self._show_language_menu)
        self.theme_button = QPushButton("☀")
        self.theme_button.setObjectName("header-control")
        self.theme_button.clicked.connect(self._show_theme_menu)
        self.new_button = QPushButton()
        self.new_button.setObjectName("button--secondary")
        self.new_button.clicked.connect(self.new_requested.emit)
        self.export_button = QPushButton()
        self.github_preview_button = QPushButton()
        self.github_preview_button.setObjectName("button--secondary")
        self.github_preview_button.clicked.connect(self.github_preview_requested.emit)
        self.export_button.setObjectName("button--primary")
        self.export_button.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.language_button)
        layout.addWidget(self.theme_button)
        layout.addWidget(self.new_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.github_preview_button)

        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("window-button")
        self.minimize_button.clicked.connect(self.minimize_requested.emit)

        self.fullscreen_button = QPushButton("□")
        self.fullscreen_button.setObjectName("window-button--maximize")
        self.fullscreen_button.clicked.connect(self.fullscreen_requested.emit)

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("window-button--close")
        self.close_button.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.fullscreen_button)
        layout.addWidget(self.close_button)
        self.update_texts()

    def update_texts(self):
        self.new_button.setText(self.translator.get("header.new"))
        self.export_button.setText(self.translator.get("header.export"))
        self.github_preview_button.setText(self.translator.get("header.github_preview"))
        self.github_preview_button.setToolTip(self.translator.get("header.github_preview_tooltip"))
        self.language_button.setToolTip(self.translator.get("header.language"))
        self.theme_button.setToolTip(self.translator.get("header.theme"))
        self.fullscreen_button.setToolTip(self.translator.get("header.fullscreen"))

    def set_language_code(self, code):
        self.language_button.setText({"en":"EN", "pt-BR":"PT", "es":"ES", "zh":"中", "ja":"日"}.get(code, "EN"))

    def set_fullscreen(self, enabled):
        self.fullscreen_button.setText("❐" if enabled else "□")
        self.fullscreen_button.setToolTip(
            self.translator.get("header.exit_fullscreen" if enabled else "header.fullscreen")
        )

    def set_theme(self, theme):
        self.theme_button.setText("☀" if theme == "dark" else "☾")

    def _show_language_menu(self):
        menu = QMenu(self)
        for code, name in self.translator.SUPPORTED_LANGUAGES.items():
            action = menu.addAction(name)
            action.triggered.connect(lambda checked=False, value=code: self.language_requested.emit(value))
        menu.exec(self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()))

    def _show_theme_menu(self):
        menu = QMenu(self)
        dark = menu.addAction(f"☾  {self.translator.get('theme.dark')}")
        light = menu.addAction(f"☀  {self.translator.get('theme.light')}")
        dark.triggered.connect(lambda: self.theme_requested.emit("dark"))
        light.triggered.connect(lambda: self.theme_requested.emit("light"))
        menu.exec(self.theme_button.mapToGlobal(self.theme_button.rect().bottomLeft()))
