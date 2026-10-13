from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.ui.components.remote_image_browser import RemoteImageBrowser


class Preview(QFrame):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setObjectName("preview")
        self.theme = "dark"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.title = QLabel()
        self.title.setObjectName("section-title")

        self.browser = RemoteImageBrowser()
        self.browser.setObjectName("preview__content")
        self.browser.setOpenExternalLinks(True)

        layout.addWidget(self.title)
        layout.addWidget(self.browser)

        self.update_texts()
        self.set_html("")

    def update_texts(self):
        self.title.setText(self.translator.get("preview.title"))

    def set_theme(self, theme):
        self.theme = theme
        # Re-render so the embedded README preview uses the selected theme.
        current_html = getattr(self, "_current_html", "")
        self.set_html(current_html)

    def set_html(self, html: str):
        self._current_html = html or ""

        if self.theme == "light":
            colors = {
                "body": "#174838",
                "heading": "#103d30",
                "paragraph": "#2c6a55",
                "code_bg": "#c8f2df",
                "pre_bg": "#b9ead4",
                "pre_border": "#7fc6a9",
                "link": "#16815a",
                "list": "#2c6a55",
                "image_bg": "#d5f7e7",
                "image_border": "#8dceb2",
                "muted": "#4b806c",
                "border": "#82c9aa",
            }
        else:
            colors = {
                "body": "#d6dde8",
                "heading": "#f3f6fb",
                "paragraph": "#b5bfce",
                "code_bg": "#171d26",
                "pre_bg": "#0b1016",
                "pre_border": "#2a3340",
                "link": "#8db0ff",
                "list": "#c0c9d7",
                "image_bg": "#141a22",
                "image_border": "#2a3340",
                "muted": "#7c899b",
                "border": "#303947",
            }

        fallback = (
            f'<p style="color:{colors["muted"]};">'
            f'{self.translator.get("preview.empty")}</p>'
        )

        document = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: Segoe UI, Arial, sans-serif;
                background: transparent;
                color: {colors["body"]};
                padding: 20px;
                line-height: 1.6;
            }}
            h1, h2, h3, h4, h5, h6 {{ color: {colors["heading"]}; }}
            h1 {{ font-size: 30px; border-bottom: 1px solid {colors["border"]}; padding-bottom: 10px; }}
            h2 {{ font-size: 24px; margin-top: 28px; }}
            p {{ color: {colors["paragraph"]}; }}
            code {{ background: {colors["code_bg"]}; padding: 2px 5px; border-radius: 4px; }}
            pre {{
                background: {colors["pre_bg"]};
                border: 1px solid {colors["pre_border"]};
                border-radius: 10px;
                padding: 16px;
                color: {colors["heading"]};
            }}
            a {{ color: {colors["link"]}; }}
            .social-links table {{ border-collapse: collapse; margin-top: 4px; }}
            .social-links td {{ padding-right: 8px; vertical-align: middle; }}
            .social-badge {{ display: inline-block; background: #0b83bd; color: white; padding: 7px 14px; font-weight: 700; font-size: 12px; border-radius: 2px; }}
            li {{ color: {colors["list"]}; margin: 4px 0; }}
            .preview-image {{
                margin: 18px 0; padding: 10px; background: {colors["image_bg"]};
                border: 1px solid {colors["image_border"]}; border-radius: 10px;
            }}
            .preview-image img {{ max-width: 100%; }}
            .preview-image span {{ display: block; color: {colors["muted"]}; margin-top: 6px; font-size: 12px; }}
            .mermaid-preview {{ border: 1px dashed {colors["border"]}; background: {colors["code_bg"]}; border-radius: 10px; padding: 14px; margin: 16px 0; }}
            .mermaid-preview strong, .xychart-title {{ color: {colors["heading"]}; }}
            .mermaid-preview pre {{ margin-top: 10px; }}
            .mermaid-preview__note {{ color: {colors["muted"]}; font-size: 12px; margin: 6px 0; }}
            .xychart-preview {{ padding: 18px; border-style: solid; }}
            .xychart-header {{ margin-bottom: 16px; }}
            .xychart-title {{ font-size: 19px; font-weight: 700; margin-bottom: 3px; }}
            .xychart-meta {{ color: {colors["muted"]}; font-size: 11px; }}
            .xychart-axis-title {{ margin-left: 8px; }}
            .xychart-frame {{ margin-top: 10px; }}
            .xychart-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
            .xychart-y-label {{ color: {colors["muted"]}; font-size: 10px; text-align: right; padding-right: 8px; height: 30px; vertical-align: middle; }}
            .xychart-grid-cell {{ border-top: 1px solid {colors["border"]}; height: 30px; }}
            .xychart-plot-cell {{ border-left: 1px solid {colors["border"]}; border-bottom: 1px solid {colors["border"]}; }}
            .xychart-column {{ width: 33%; text-align: center; vertical-align: bottom; padding: 0 8px; height: 150px; }}
            .xychart-value {{ color: {colors["heading"]}; font-size: 11px; font-weight: 700; margin-bottom: 5px; }}
            .xychart-bar {{ display: block; width: 70%; max-width: 46px; min-width: 18px; margin: 0 auto; background: {colors["link"]}; border-radius: 6px 6px 2px 2px; }}
            .xychart-label {{ color: {colors["paragraph"]}; font-size: 10px; margin-top: 6px; text-align: center; }}
            .xychart-line-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 5px; background: {colors["link"]}; }}
            .xychart-axis-title {{ color: {colors["muted"]}; font-size: 10px; margin-left: 8px; }}
        </style>
        </head>
        <body>{html or fallback}</body>
        </html>
        """
        self.browser.setHtml(document)
