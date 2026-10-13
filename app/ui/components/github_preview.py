from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

from app.ui.components.remote_image_browser import RemoteImageBrowser

from app.core.markdown import render_markdown


class GitHubPreviewWindow(QDialog):
    """Detached preview styled to resemble a GitHub README page."""

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.theme = "light"
        self._markdown = ""
        self.setObjectName("github-preview-window")
        self.setWindowTitle("GitHub README Preview")
        self.setMinimumSize(900, 650)
        self.resize(1100, 760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("github-preview-title")
        layout.addWidget(self.title)

        self.browser = RemoteImageBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setOpenLinks(True)
        self.browser.setObjectName("github-preview-browser")
        self.browser.setSearchPaths(["."])
        layout.addWidget(self.browser, 1)

        self.update_texts()
        self.set_markdown("")

    def update_texts(self):
        self.title.setText(self.translator.get("github_preview.title"))
        self.setWindowTitle(self.translator.get("github_preview.window_title"))
        if self._markdown:
            self.set_markdown(self._markdown)

    def set_theme(self, theme):
        self.theme = theme
        self.set_markdown(self._markdown)

    def set_markdown(self, markdown_text):
        self._markdown = markdown_text or ""
        html = render_markdown(self._markdown)
        self.browser.setHtml(self._build_document(html))

    def _build_document(self, html):
        if self.theme == "dark":
            colors = {
                "page": "#0d1117",
                "card": "#0d1117",
                "border": "#30363d",
                "text": "#e6edf3",
                "muted": "#8b949e",
                "heading": "#f0f6fc",
                "link": "#58a6ff",
                "code": "#161b22",
                "code_border": "#30363d",
                "quote": "#8b949e",
                "quote_border": "#3b434b",
                "table_alt": "#161b22",
            }
        else:
            colors = {
                "page": "#ffffff",
                "card": "#ffffff",
                "border": "#d0d7de",
                "text": "#1f2328",
                "muted": "#656d76",
                "heading": "#1f2328",
                "link": "#0969da",
                "code": "#f6f8fa",
                "code_border": "#d0d7de",
                "quote": "#656d76",
                "quote_border": "#d0d7de",
                "table_alt": "#f6f8fa",
            }

        if not html.strip():
            html = f'<p class="empty">{self.translator.get("github_preview.empty")}</p>'

        return f"""
        <html>
        <head>
        <style>
            body {{
                background: {colors['page']};
                color: {colors['text']};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                line-height: 1.55;
                padding: 34px 42px 60px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {colors['heading']};
                font-weight: 600;
                line-height: 1.25;
                margin-top: 24px;
                margin-bottom: 16px;
            }}
            h1 {{ font-size: 32px; padding-bottom: 10px; border-bottom: 1px solid {colors['border']}; }}
            h2 {{ font-size: 24px; padding-bottom: 8px; border-bottom: 1px solid {colors['border']}; }}
            h3 {{ font-size: 20px; }}
            h4 {{ font-size: 16px; }}
            p {{ margin: 0 0 16px; }}
            a {{ color: {colors['link']}; text-decoration: none; }}
            .social-links table {{ border-collapse: collapse; margin-top: 4px; }}
            .social-links td {{ padding-right: 8px; vertical-align: middle; }}
            .social-badge {{ display: inline-block; background: #0b83bd; color: white; padding: 7px 14px; font-weight: 700; font-size: 12px; border-radius: 2px; }}
            code {{
                background: {colors['code']};
                border: 1px solid {colors['code_border']};
                border-radius: 6px;
                padding: 2px 5px;
                font-family: "Cascadia Code", Consolas, monospace;
                font-size: 90%;
            }}
            pre {{
                background: {colors['code']};
                border: 1px solid {colors['code_border']};
                border-radius: 6px;
                padding: 16px;
                overflow-x: auto;
                margin: 0 0 16px;
            }}
            pre code {{ background: transparent; border: none; padding: 0; }}
            blockquote {{
                color: {colors['quote']};
                border-left: 4px solid {colors['quote_border']};
                margin: 0 0 16px;
                padding: 0 16px;
            }}
            ul, ol {{ padding-left: 30px; margin-bottom: 16px; }}
            li {{ margin: 4px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 0 0 16px; }}
            th, td {{ border: 1px solid {colors['border']}; padding: 6px 13px; }}
            th {{ font-weight: 600; }}
            tr:nth-child(even) {{ background: {colors['table_alt']}; }}
            img {{ max-width: 100%; height: auto; }}
            hr {{ border: 0; border-top: 1px solid {colors['border']}; margin: 24px 0; }}
            .empty {{ color: {colors['muted']}; text-align: center; padding: 80px 20px; }}
        </style>
        </head>
        <body>{html}</body>
        </html>
        """

    def closeEvent(self, event):
        self.hide()
        event.ignore()
