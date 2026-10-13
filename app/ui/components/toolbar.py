from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout


class Toolbar(QFrame):
    block_requested = Signal(str)

    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setObjectName("toolbar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)
        self.layout.setSpacing(6)
        self.buttons = []
        self.actions = [("toolbar.heading1","heading1"),("toolbar.heading2","heading2"),("toolbar.paragraph","paragraph"),("toolbar.image","image"),("toolbar.code","code"),("toolbar.list","list"),("toolbar.ordered_list","ordered_list"),("toolbar.mermaid","mermaid"),("toolbar.tech_stack","tech_stack"),("toolbar.github_stats","github_stats"),("toolbar.social_links","social_links"),("toolbar.custom_stats","custom_stats"),("toolbar.github_contributions","github_contributions")]
        for key, block_type in self.actions:
            button = QPushButton()
            button.setObjectName("toolbar__button")
            button.clicked.connect(lambda checked=False, value=block_type: self.block_requested.emit(value))
            self.layout.addWidget(button)
            self.buttons.append((button, key))
        self.layout.addStretch()
        self.update_texts()

    def update_texts(self):
        for button, key in self.buttons:
            button.setText(self.translator.get(key))
