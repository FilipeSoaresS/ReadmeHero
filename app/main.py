import sys
import ctypes

from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.utils.app_icon import get_app_icon


def main():
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ReadMeHero.App")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setWindowIcon(get_app_icon())
    app.setApplicationName("ReadMe Hero")
    app.setOrganizationName("ReadMe Hero")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
