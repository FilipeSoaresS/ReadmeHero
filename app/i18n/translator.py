import json
from pathlib import Path


class Translator:
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "pt-BR": "Português (Brasil)",
        "es": "Español",
        "zh": "中文",
        "ja": "日本語",
    }

    def __init__(self, language="en"):
        self.language = language
        self._strings = {}
        self._load()

    def _load(self):
        path = Path(__file__).parent / "locales" / f"{self.language}.json"
        if not path.exists():
            path = Path(__file__).parent / "locales" / "en.json"
        self._strings = json.loads(path.read_text(encoding="utf-8"))

    def set_language(self, language):
        if language in self.SUPPORTED_LANGUAGES:
            self.language = language
            self._load()

    def get(self, key, default=None):
        return self._strings.get(key, default or key)
