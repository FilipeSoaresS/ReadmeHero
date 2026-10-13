from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout,
    QHBoxLayout, QFileDialog, QInputDialog, QScrollArea, QWidget, QMessageBox, QComboBox
)

from app.core.blocks import (
    HeadingBlock, ParagraphBlock, ImageBlock, CodeBlock, ListBlock, MermaidBlock, TechStackBlock, GitHubStatsBlock, SocialLinksBlock, CustomStatsBlock, GitHubContributionsBlock
)
from app.services.image_service import is_image_file, copy_image_to_assets


class BlockWidget(QFrame):
    changed = Signal()
    remove_requested = Signal(object)

    def __init__(self, block, project_dir: str, translator):
        super().__init__()
        self.block = block
        self.project_dir = project_dir
        self.translator = translator
        self.setObjectName("editor__block")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(8)

        header = QHBoxLayout()
        self.label = QLabel()
        self.label.setObjectName("editor__block-label")

        self.remove = QPushButton()
        self.remove.setObjectName("button--ghost")
        self.remove.clicked.connect(lambda: self.remove_requested.emit(self))

        header.addWidget(self.label)
        header.addStretch()
        header.addWidget(self.remove)
        outer.addLayout(header)

        self._build_editor(outer)
        self.update_texts()

    def update_texts(self):
        labels = {
            "heading": "block.heading",
            "paragraph": "block.text",
            "image": "block.image",
            "code": "block.code",
            "list": "block.list",
            "mermaid": "block.mermaid",
            "tech_stack": "block.tech_stack",
            "github_stats": "block.github_stats",
            "social_links": "block.social_links",
            "custom_stats": "block.custom_stats",
            "github_contributions": "block.github_contributions",
        }
        self.label.setText(self.translator.get(labels.get(self.block.block_type, "block.text")))
        self.remove.setText(self.translator.get("block.remove"))

        if isinstance(self.block, HeadingBlock):
            self.input.setPlaceholderText(self.translator.get("block.heading_placeholder"))
            self.level_label.setText(self.translator.get("block.heading_level"))
        elif isinstance(self.block, ParagraphBlock):
            self.input.setPlaceholderText(self.translator.get("block.text_placeholder"))
        elif isinstance(self.block, ImageBlock):
            self.alt_input.setPlaceholderText(self.translator.get("block.alt_placeholder"))
        elif isinstance(self.block, CodeBlock):
            self.language_input.setPlaceholderText(self.translator.get("block.code_language"))
            self.input.setPlaceholderText(self.translator.get("block.code_placeholder"))
        elif isinstance(self.block, ListBlock):
            self.input.setPlaceholderText(self.translator.get("block.list_placeholder"))
        elif isinstance(self.block, GitHubContributionsBlock):
            self.contributions_username.setPlaceholderText(self.translator.get("block.github_contributions_username"))
            self.contributions_title.setPlaceholderText(self.translator.get("block.github_contributions_title"))
            self.contributions_color.setPlaceholderText(self.translator.get("block.github_contributions_color"))
            self.contributions_theme_label.setText(self.translator.get("block.github_contributions_theme"))
        elif isinstance(self.block, CustomStatsBlock):
            self.custom_title.setPlaceholderText(self.translator.get("block.custom_stats_title_placeholder"))
            self.custom_description.setPlaceholderText(self.translator.get("block.custom_stats_description_placeholder"))
            self.add_stat_button.setText("+ " + self.translator.get("block.custom_stats_add"))
            for i in range(self.stats_rows.count()):
                row = self.stats_rows.itemAt(i)
                placeholders = [
                    self.translator.get("block.custom_stats_label"),
                    self.translator.get("block.custom_stats_value"),
                    self.translator.get("block.custom_stats_icon"),
                    self.translator.get("block.custom_stats_link"),
                ]
                for j, placeholder in enumerate(placeholders):
                    field = row.itemAt(j).widget()
                    if field:
                        field.setPlaceholderText(placeholder)

    def _build_editor(self, layout):
        if isinstance(self.block, HeadingBlock):
            row = QHBoxLayout()
            row.setSpacing(10)

            self.input = QLineEdit(self.block.text)
            self.input.textChanged.connect(self._sync)

            level_box = QVBoxLayout()
            level_box.setContentsMargins(0, 0, 0, 0)
            level_box.setSpacing(3)
            level_box.setAlignment(Qt.AlignmentFlag.AlignTop)

            self.level_label = QLabel()
            self.level_label.setObjectName("editor__field-label")

            level_control = QHBoxLayout()
            level_control.setContentsMargins(0, 0, 0, 0)
            level_control.setSpacing(3)

            self.level_left = QPushButton("←")
            self.level_left.setObjectName("heading-level__button")
            self.level_left.setFixedSize(28, 30)
            self.level_left.setToolTip("Decrease heading level")
            self.level_left.clicked.connect(lambda: self._change_heading_level(-1))

            self.level = QLineEdit()
            self.level.setObjectName("heading-level__input")
            self.level.setText(f"H{max(1, min(6, int(self.block.level)))}")
            self.level.setFixedWidth(48)
            self.level.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.level.setMaxLength(2)
            self.level.editingFinished.connect(self._validate_heading_level)

            self.level_right = QPushButton("→")
            self.level_right.setObjectName("heading-level__button")
            self.level_right.setFixedSize(28, 30)
            self.level_right.setToolTip("Increase heading level")
            self.level_right.clicked.connect(lambda: self._change_heading_level(1))

            level_control.addWidget(self.level_left)
            level_control.addWidget(self.level)
            level_control.addWidget(self.level_right)

            level_box.addWidget(self.level_label)
            level_box.addLayout(level_control)

            row.addWidget(self.input, 1)
            row.addLayout(level_box)
            layout.addLayout(row)

        elif isinstance(self.block, ParagraphBlock):
            self.input = QTextEdit()
            self.input.setPlainText(self.block.text)
            self.input.setMinimumHeight(90)
            self.input.textChanged.connect(self._sync)
            layout.addWidget(self.input)

        elif isinstance(self.block, ImageBlock):
            row = QHBoxLayout()
            self.path_label = QLabel(self.block.path)
            self.path_label.setObjectName("editor__image-path")

            self.alt_input = QLineEdit(self.block.alt_text)
            self.alt_input.textChanged.connect(self._sync_image_alt)

            row.addWidget(self.path_label, 1)
            row.addWidget(self.alt_input)
            layout.addLayout(row)

        elif isinstance(self.block, CodeBlock):
            self.language_input = QLineEdit(self.block.language)
            self.language_input.textChanged.connect(self._sync_language)

            self.input = QTextEdit()
            self.input.setPlainText(self.block.code)
            self.input.setMinimumHeight(130)
            self.input.textChanged.connect(self._sync)

            layout.addWidget(self.language_input)
            layout.addWidget(self.input)

        elif isinstance(self.block, ListBlock):
            self.input = QTextEdit()
            self.input.setPlainText("\n".join(self.block.items))
            self.input.setMinimumHeight(90)
            self.input.textChanged.connect(self._sync_list)
            layout.addWidget(self.input)

        elif isinstance(self.block, MermaidBlock):
            self.input = QTextEdit()
            self.input.setPlainText(self.block.code)
            self.input.setMinimumHeight(160)
            self.input.textChanged.connect(self._sync_mermaid)
            layout.addWidget(self.input)

        elif isinstance(self.block, TechStackBlock):
            self.input = QTextEdit()
            self.input.setPlainText("\n".join(f"{name} | {url}" for name, url in self.block.items))
            self.input.setMinimumHeight(130)
            self.input.setPlaceholderText("Technology | icon URL")
            self.input.textChanged.connect(self._sync_tech_stack)
            layout.addWidget(self.input)

        elif isinstance(self.block, GitHubStatsBlock):
            self.username_input = QLineEdit(self.block.username)
            self.username_input.setPlaceholderText("GitHub username")
            self.username_input.textChanged.connect(self._sync_github_username)
            layout.addWidget(self.username_input)

        elif isinstance(self.block, SocialLinksBlock):
            self.input = QTextEdit()
            self.input.setPlainText("\n".join(f"{label} | {url}" for label, url in self.block.links))
            self.input.setMinimumHeight(100)
            self.input.setPlaceholderText("Label | URL")
            self.input.textChanged.connect(self._sync_social_links)
            layout.addWidget(self.input)

        elif isinstance(self.block, GitHubContributionsBlock):
            self.contributions_username = QLineEdit(self.block.username)
            self.contributions_username.setPlaceholderText("GitHub username")
            self.contributions_username.textChanged.connect(self._sync_github_contributions)
            layout.addWidget(self.contributions_username)

            self.contributions_title = QLineEdit(self.block.title)
            self.contributions_title.setPlaceholderText("Section title")
            self.contributions_title.textChanged.connect(self._sync_github_contributions)
            layout.addWidget(self.contributions_title)

            theme_row = QHBoxLayout()
            self.contributions_theme_label = QLabel()
            self.contributions_theme_label.setObjectName("editor__field-label")
            self.contributions_theme = QComboBox()
            self.contributions_theme.addItem("Dark", "dark")
            self.contributions_theme.addItem("Light", "light")
            self.contributions_theme.setCurrentIndex(0 if self.block.theme == "dark" else 1)
            self.contributions_theme.currentIndexChanged.connect(self._sync_github_contributions)
            theme_row.addWidget(self.contributions_theme_label)
            theme_row.addWidget(self.contributions_theme)
            theme_row.addStretch()
            layout.addLayout(theme_row)

            self.contributions_color = QLineEdit(self.block.color)
            self.contributions_color.setPlaceholderText("Color HEX (optional)")
            self.contributions_color.textChanged.connect(self._sync_github_contributions)
            layout.addWidget(self.contributions_color)

        elif isinstance(self.block, CustomStatsBlock):
            self.custom_title = QLineEdit(self.block.title)
            self.custom_title.setPlaceholderText("Section title")
            self.custom_title.textChanged.connect(self._sync_custom_stats)
            layout.addWidget(self.custom_title)

            self.custom_description = QLineEdit(self.block.description)
            self.custom_description.setPlaceholderText("Optional description")
            self.custom_description.textChanged.connect(self._sync_custom_stats)
            layout.addWidget(self.custom_description)

            self.stats_rows = QVBoxLayout()
            self.stats_rows.setSpacing(6)
            layout.addLayout(self.stats_rows)
            self.add_stat_button = QPushButton("+ Add stat")
            self.add_stat_button.setObjectName("button--ghost")
            self.add_stat_button.clicked.connect(lambda: self._add_stat_row())
            layout.addWidget(self.add_stat_button)
            for stat in self.block.stats:
                self._add_stat_row(stat)

    def _sync(self):
        if isinstance(self.block, HeadingBlock):
            self.block.text = self.input.text()
            self.block.level = self._current_heading_level()
        elif isinstance(self.block, ParagraphBlock):
            self.block.text = self.input.toPlainText()
        elif isinstance(self.block, CodeBlock):
            self.block.code = self.input.toPlainText()

        self.changed.emit()

    def _current_heading_level(self):
        text = self.level.text().strip().upper().replace("H", "", 1)
        try:
            value = int(text)
        except ValueError:
            return max(1, min(6, int(self.block.level)))
        return max(1, min(6, value))

    def _set_heading_level(self, value):
        value = max(1, min(6, int(value)))
        self.block.level = value
        self.level.setText(f"H{value}")
        self.changed.emit()

    def _change_heading_level(self, delta):
        current = self._current_heading_level()
        target = current + delta
        if target < 1 or target > 6:
            QMessageBox.warning(
                self,
                self.translator.get("dialog.heading_level_title"),
                self.translator.get("dialog.heading_level_invalid"),
            )
            self.level.setText(f"H{current}")
            return
        self._set_heading_level(target)

    def _validate_heading_level(self):
        raw = self.level.text().strip().upper()
        normalized = raw[1:] if raw.startswith("H") else raw
        try:
            value = int(normalized)
        except ValueError:
            QMessageBox.warning(
                self,
                self.translator.get("dialog.heading_level_title"),
                self.translator.get("dialog.heading_level_invalid"),
            )
            self.level.setText(f"H{self.block.level}")
            return

        if value < 1 or value > 6:
            QMessageBox.warning(
                self,
                self.translator.get("dialog.heading_level_title"),
                self.translator.get("dialog.heading_level_invalid"),
            )
            self.level.setText(f"H{self.block.level}")
            return

        self._set_heading_level(value)

    def _sync_image_alt(self, text):
        self.block.alt_text = text
        self.changed.emit()

    def _sync_language(self, text):
        self.block.language = text
        self.changed.emit()

    def _sync_list(self):
        self.block.items = self.input.toPlainText().splitlines()
        self.changed.emit()

    def _sync_mermaid(self):
        self.block.code = self.input.toPlainText()
        self.changed.emit()

    def _sync_tech_stack(self):
        items = []
        for line in self.input.toPlainText().splitlines():
            if "|" in line:
                name, url = line.split("|", 1)
                if name.strip() and url.strip():
                    items.append((name.strip(), url.strip()))
        self.block.items = items
        self.changed.emit()

    def _sync_github_username(self, text):
        self.block.username = text.strip()
        self.changed.emit()

    def _sync_social_links(self):
        links = []
        for line in self.input.toPlainText().splitlines():
            if "|" in line:
                label, url = line.split("|", 1)
                if label.strip() and url.strip():
                    links.append((label.strip(), url.strip()))
        self.block.links = links
        self.changed.emit()

    def _sync_github_contributions(self):
        self.block.username = self.contributions_username.text().strip()
        self.block.title = self.contributions_title.text().strip() or "GitHub Contributions"
        self.block.theme = self.contributions_theme.currentData() or "dark"
        self.block.color = self.contributions_color.text().strip().lstrip("#") or "40c463"
        self.changed.emit()

    def _add_stat_row(self, stat=("", "", "", "")):
        row = QHBoxLayout()
        row.setSpacing(5)
        fields = []
        placeholders = ["Label", "Value", "Icon URL (optional)", "Link URL (optional)"]
        for value, placeholder in zip(stat, placeholders):
            field = QLineEdit(value)
            field.setPlaceholderText(placeholder)
            field.textChanged.connect(self._sync_custom_stats)
            row.addWidget(field, 1)
            fields.append(field)
        remove = QPushButton("×")
        remove.setFixedWidth(30)
        remove.setObjectName("button--ghost")
        remove.clicked.connect(lambda: self._remove_stat_row(row))
        row.addWidget(remove)
        self.stats_rows.addLayout(row)
        self._sync_custom_stats()

    def _remove_stat_row(self, row):
        while row.count():
            item = row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.stats_rows.removeItem(row)
        self._sync_custom_stats()

    def _sync_custom_stats(self):
        if not hasattr(self, "stats_rows"):
            return
        self.block.title = self.custom_title.text().strip()
        self.block.description = self.custom_description.text().strip()
        stats=[]
        for i in range(self.stats_rows.count()):
            row=self.stats_rows.itemAt(i)
            fields=[row.itemAt(j).widget() for j in range(4)]
            if all(fields):
                values=tuple(f.text().strip() for f in fields)
                if values[0] or values[1]:
                    stats.append(values)
        self.block.stats=stats
        self.changed.emit()


class Editor(QFrame):
    changed = Signal()

    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setObjectName("editor")

        self.project_dir = str(Path.cwd())
        self.blocks = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 14, 14, 14)
        self.layout.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("section-title")
        self.layout.addWidget(self.title)

        # Keep the editor blocks at their natural height. When the document
        # becomes taller than the available panel, the scroll area takes over
        # instead of forcing widgets to compress vertically.
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("editor__scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("editor__scroll-content")
        self.blocks_container = QVBoxLayout(self.scroll_content)
        self.blocks_container.setContentsMargins(0, 0, 4, 0)
        self.blocks_container.setSpacing(10)

        self.drop_zone = QLabel()
        self.drop_zone.setObjectName("editor__drop-zone")
        self.drop_zone.setMinimumHeight(120)
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.dragEnterEvent = self._drag_enter
        self.drop_zone.dropEvent = self._drop
        self.blocks_container.addWidget(self.drop_zone)
        self.blocks_container.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area, 1)
        self.update_texts()

    def update_texts(self):
        self.title.setText(self.translator.get("editor.title"))
        self.drop_zone.setText(self.translator.get("editor.drop_image"))
        for _, widget in self.blocks:
            widget.update_texts()

    def add_block(self, block):
        widget = BlockWidget(block, self.project_dir, self.translator)
        widget.changed.connect(self.changed.emit)
        widget.remove_requested.connect(self.remove_widget)
        self.blocks.append((block, widget))
        # Insert blocks before the drop zone and trailing stretch.
        self.blocks_container.insertWidget(len(self.blocks) - 1, widget)
        self.changed.emit()

    def remove_widget(self, widget):
        for index, (block, current) in enumerate(self.blocks):
            if current is widget:
                self.blocks.pop(index)
                current.deleteLater()
                self.changed.emit()
                break

    def add_image(self, dialog_title=None, alt_title=None, alt_label=None):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            dialog_title or self.translator.get("dialog.image_title"),
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp *.svg)"
        )

        for path in paths:
            self._add_image_path(path, alt_title, alt_label)

    def _add_image_path(self, path, alt_title=None, alt_label=None):
        if not is_image_file(path):
            return

        relative_path = copy_image_to_assets(path, self.project_dir)

        alt, ok = QInputDialog.getText(
            self,
            alt_title or self.translator.get("dialog.image_alt_title"),
            alt_label or self.translator.get("dialog.image_alt"),
            text=Path(path).stem.replace("_", " ").replace("-", " ").title()
        )

        if ok:
            self.add_block(ImageBlock(relative_path, alt or "Image"))

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            self._add_image_path(path)
        event.acceptProposedAction()

    def clear(self):
        for _, widget in self.blocks:
            widget.deleteLater()
        self.blocks.clear()
        self.changed.emit()

    def get_blocks(self):
        return [block for block, _ in self.blocks]
