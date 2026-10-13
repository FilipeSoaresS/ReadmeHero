from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout


class StatusBar(QFrame):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setObjectName("status-bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 7, 14, 7)

        self.status = QLabel()
        self.stats = QLabel()

        layout.addWidget(self.status)
        layout.addStretch()
        layout.addWidget(self.stats)

        self.set_status("status.ready")
        self.set_blocks(0)

    def set_status(self, key):
        self.status.setText(self.translator.get(key))

    def set_blocks(self, count):
        if self.translator.language == "pt-BR":
            word = "bloco" if count == 1 else "blocos"
        elif self.translator.language == "es":
            word = "bloque" if count == 1 else "bloques"
        elif self.translator.language == "zh":
            word = "区块"
        elif self.translator.language == "ja":
            word = "ブロック"
        else:
            word = "block" if count == 1 else "blocks"
        self.stats.setText(f"{count} {word}")
