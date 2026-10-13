import re

import markdown

from app.core.blocks import MermaidBlock


_MERMAID_FENCE_RE = re.compile(
    r"```mermaid\s*\n(?P<code>.*?)(?:\n)?```",
    re.IGNORECASE | re.DOTALL,
)


def render_markdown(source: str) -> str:
    """Render Markdown while preserving Mermaid blocks for the visual preview.

    Mermaid is not rendered by Python-Markdown itself. We temporarily replace
    Mermaid fenced blocks with HTML comments, render the remaining Markdown,
    then inject the ReadMe Hero Mermaid preview HTML back into the result.
    """
    mermaid_html: list[str] = []

    def _extract_mermaid(match: re.Match[str]) -> str:
        index = len(mermaid_html)
        mermaid_html.append(MermaidBlock(match.group("code")).to_html())
        return f"<!-- README_HERO_MERMAID_{index} -->"

    protected = _MERMAID_FENCE_RE.sub(_extract_mermaid, source or "")

    rendered = markdown.markdown(
        protected,
        extensions=["fenced_code", "tables", "nl2br"],
    )

    for index, html in enumerate(mermaid_html):
        marker = f"<!-- README_HERO_MERMAID_{index} -->"
        rendered = rendered.replace(marker, html)

    return rendered
