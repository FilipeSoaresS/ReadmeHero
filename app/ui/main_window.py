from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QFrame
from app.utils.app_icon import get_app_icon

from app.core.document import Document
from app.core.blocks import HeadingBlock, ParagraphBlock, CodeBlock, ListBlock, MermaidBlock, TechStackBlock, GitHubStatsBlock, SocialLinksBlock, CustomStatsBlock, GitHubContributionsBlock
from app.core.markdown import render_markdown
from app.services.export_service import export_document
from app.i18n.translator import Translator
from app.ui.themes.theme_manager import ThemeManager
from app.ui.components.header import Header
from app.ui.components.toolbar import Toolbar
from app.ui.components.editor import Editor
from app.ui.components.preview import Preview
from app.ui.components.status_bar import StatusBar
from app.ui.components.github_preview import GitHubPreviewWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.translator = Translator("en")
        self.theme_manager = ThemeManager(self)
        self._drag_position = None
        self._normal_geometry = None
        self._is_fullscreen = False
        self.document = Document()
        self.github_preview_window = None
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(90)
        self._refresh_timer.timeout.connect(self._sync_document_now)

        self.setWindowTitle("ReadMe Hero")
        self.setWindowIcon(get_app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(1320, 820)
        self.setMinimumSize(1000, 680)

        self._build_ui()
        self.theme_manager.set_theme("dark")
        self.header.set_theme("dark")
        self.preview.set_theme("dark")
        self._create_initial_document()
        self._refresh()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("app")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        self.shell = QFrame()
        self.shell.setObjectName("window-shell")

        shell_layout = QVBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.header = Header(self.translator)
        self.toolbar = Toolbar(self.translator)

        shell_layout.addWidget(self.header)
        shell_layout.addWidget(self.toolbar)

        content = QHBoxLayout()
        content.setContentsMargins(14, 14, 14, 14)
        content.setSpacing(14)

        self.editor = Editor(self.translator)
        self.preview = Preview(self.translator)

        content.addWidget(self.editor, 1)
        content.addWidget(self.preview, 1)
        shell_layout.addLayout(content, 1)

        self.status_bar = StatusBar(self.translator)
        shell_layout.addWidget(self.status_bar)

        root.addWidget(self.shell)

        self.toolbar.block_requested.connect(self._add_block)
        self.header.new_requested.connect(self._new_document)
        self.header.export_requested.connect(self._export)
        self.header.language_requested.connect(self._set_language)
        self.header.theme_requested.connect(self._set_theme)
        self.header.close_requested.connect(self.close)
        self.header.minimize_requested.connect(self.showMinimized)
        self.header.fullscreen_requested.connect(self._toggle_fullscreen)
        self.header.github_preview_requested.connect(self._open_github_preview)
        self.editor.changed.connect(self._schedule_sync)

        self.header.mousePressEvent = self._header_mouse_press
        self.header.mouseMoveEvent = self._header_mouse_move
        self.header.mouseReleaseEvent = self._header_mouse_release

    def _toggle_fullscreen(self):
        if self._is_fullscreen:
            self.showNormal()
            if self._normal_geometry is not None:
                self.setGeometry(self._normal_geometry)
            self._is_fullscreen = False
        else:
            self._normal_geometry = self.geometry()
            # Use the desktop work area instead of true fullscreen so Windows
            # keeps the taskbar visible.
            self.showMaximized()
            self._is_fullscreen = True

        self.header.set_fullscreen(self._is_fullscreen)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self._toggle_fullscreen()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape and self._is_fullscreen:
            self._toggle_fullscreen()
            event.accept()
            return
        super().keyPressEvent(event)

    def _header_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._is_fullscreen:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _header_mouse_move(self, event):
        if self._drag_position is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def _header_mouse_release(self, event):
        self._drag_position = None
        event.accept()

    def _create_initial_document(self):
        self.editor.clear()
        self.document = Document()

        initial_blocks = [
            HeadingBlock("My Project", 1),
            ParagraphBlock(
                "A short description of your project goes here. "
                "Edit this block or add new ones from the toolbar."
            ),
        ]

        for block in initial_blocks:
            self.document.add_block(block)
            self.editor.add_block(block)

    def _new_document(self):
        answer = QMessageBox.question(
            self,
            self.translator.get("dialog.new_title"),
            self.translator.get("dialog.new_message"),
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._create_initial_document()
            self._refresh()

    def _add_block(self, block_type):
        if block_type == "heading1":
            block = HeadingBlock("New heading", 1)
        elif block_type == "heading2":
            block = HeadingBlock("New section", 2)
        elif block_type == "paragraph":
            block = ParagraphBlock("Write something here...")
        elif block_type == "image":
            self.editor.add_image(
                self.translator.get("dialog.image_title"),
                self.translator.get("dialog.image_alt_title"),
                self.translator.get("dialog.image_alt"),
            )
            return
        elif block_type == "code":
            block = CodeBlock("# Write your code here", "python")
        elif block_type == "list":
            block = ListBlock(["First item", "Second item"])
        elif block_type == "ordered_list":
            block = ListBlock(["First step", "Second step"], ordered=True)
        elif block_type == "mermaid":
            block = MermaidBlock()
        elif block_type == "tech_stack":
            block = TechStackBlock()
        elif block_type == "github_stats":
            block = GitHubStatsBlock()
        elif block_type == "social_links":
            block = SocialLinksBlock()
        elif block_type == "custom_stats":
            block = CustomStatsBlock()
        elif block_type == "github_contributions":
            block = GitHubContributionsBlock()
        else:
            return

        self.document.add_block(block)
        self.editor.add_block(block)
        self._refresh()

    def _schedule_sync(self):
        # Coalesce rapid keystrokes so Markdown/HTML is not rebuilt on every key.
        self._refresh_timer.start()

    def _sync_document_now(self):
        self.document.blocks = self.editor.get_blocks()
        self._refresh()

    def _sync_document(self):
        self._schedule_sync()

    def _refresh(self):
        markdown_text = self.document.to_markdown()
        self.preview.set_html(render_markdown(markdown_text))
        if self.github_preview_window is not None:
            self.github_preview_window.set_markdown(markdown_text)
        self.status_bar.set_blocks(len(self.document.blocks))
        self.status_bar.set_status("status.ready")


    def _open_github_preview(self):
        if self.github_preview_window is None:
            self.github_preview_window = GitHubPreviewWindow(self.translator, self)
            self.github_preview_window.set_theme(self.theme_manager.current_theme)
        else:
            self.github_preview_window.translator = self.translator
            self.github_preview_window.update_texts()
            self.github_preview_window.set_theme(self.theme_manager.current_theme)

        self.github_preview_window.set_markdown(self.document.to_markdown())
        self.github_preview_window.show()
        self.github_preview_window.raise_()
        self.github_preview_window.activateWindow()

    def _set_language(self, language):
        self.translator.set_language(language)
        self.header.update_texts()
        self.header.set_language_code(language)
        self.toolbar.update_texts()
        self.editor.update_texts()
        self.preview.update_texts()
        self.status_bar.set_status("status.ready")
        self.status_bar.set_blocks(len(self.document.blocks))

    def _set_theme(self, theme):
        self.theme_manager.set_theme(theme)
        self.header.set_theme(theme)
        self.preview.set_theme(theme)
        if self.github_preview_window is not None:
            self.github_preview_window.set_theme(theme)
        self._refresh()

    def _export(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.translator.get("dialog.export_title"),
        )
        if not directory:
            return

        try:
            readme_path = export_document(self.document.to_markdown(), directory)
            QMessageBox.information(
                self,
                self.translator.get("dialog.export_success_title"),
                f"{self.translator.get('dialog.export_success_title')}:\n\n{readme_path}",
            )
            self.status_bar.set_status("status.exported")
        except OSError as error:
            QMessageBox.critical(
                self,
                self.translator.get("dialog.export_error_title"),
                str(error),
            )
