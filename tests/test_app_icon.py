from pathlib import Path


def test_taskbar_icon_exists():
    root = Path(__file__).resolve().parents[1]
    icon = root / "assets" / "img" / "1.ico"
    assert icon.exists()
    assert icon.stat().st_size > 0
