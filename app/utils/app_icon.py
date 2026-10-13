from pathlib import Path
from PySide6.QtGui import QIcon


def get_app_icon() -> QIcon:
    """Return the application icon from the shared brand asset."""
    icon_path = Path(__file__).resolve().parents[2] / "assets" / "img" / "1.ico"
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()
