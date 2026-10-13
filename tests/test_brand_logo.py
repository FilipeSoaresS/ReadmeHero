from pathlib import Path


def test_brand_logo_exists():
    root = Path(__file__).resolve().parents[1]
    logo = root / "assets" / "img" / "1.png"
    assert logo.exists()
    assert logo.stat().st_size > 0
