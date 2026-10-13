from app.i18n.translator import Translator


def test_supported_languages():
    translator = Translator("pt-BR")
    assert translator.get("header.new") == "Novo"
