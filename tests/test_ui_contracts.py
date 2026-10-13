from pathlib import Path

from app.i18n.translator import Translator


def test_translator_languages():
    translator = Translator("pt-BR")
    assert translator.get("header.new") == "Novo"

    translator.set_language("ja")
    assert translator.get("header.new") == "新規"


def test_header_has_fullscreen_signal():
    from app.ui.components.header import Header
    assert hasattr(Header, "fullscreen_requested")


def test_heading_level_control_contract():
    editor = Path("app/ui/components/editor.py").read_text(encoding="utf-8")
    assert 'QPushButton("←")' in editor
    assert 'QPushButton("→")' in editor
    assert 'self.level.setText(f"H' in editor
    assert '_validate_heading_level' in editor
    assert 'dialog.heading_level_invalid' in editor
