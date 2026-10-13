from dataclasses import dataclass
from html import escape


class MarkdownBlock:
    """Base class for every visual document block."""

    block_type = "block"

    def to_markdown(self) -> str:
        raise NotImplementedError

    def to_html(self) -> str:
        raise NotImplementedError


@dataclass
class HeadingBlock(MarkdownBlock):
    text: str
    level: int = 1

    block_type = "heading"

    def to_markdown(self) -> str:
        level = max(1, min(self.level, 6))
        return f'{"#" * level} {self.text.strip()}'

    def to_html(self) -> str:
        level = max(1, min(self.level, 6))
        return f"<h{level}>{escape(self.text.strip())}</h{level}>"


@dataclass
class ParagraphBlock(MarkdownBlock):
    text: str = ""

    block_type = "paragraph"

    def to_markdown(self) -> str:
        return self.text.strip()

    def to_html(self) -> str:
        text = escape(self.text.strip()).replace("\n", "<br>")
        return f"<p>{text}</p>"


@dataclass
class ImageBlock(MarkdownBlock):
    path: str
    alt_text: str = "Image"

    block_type = "image"

    def to_markdown(self) -> str:
        return f"![{self.alt_text.strip() or 'Image'}]({self.path})"

    def to_html(self) -> str:
        alt = escape(self.alt_text.strip() or "Image")
        path = escape(self.path)
        return (
            f'<div class="preview-image">'
            f'<img src="{path}" alt="{alt}">'
            f'<span>{alt}</span>'
            f'</div>'
        )


@dataclass
class CodeBlock(MarkdownBlock):
    code: str = ""
    language: str = ""

    block_type = "code"

    def to_markdown(self) -> str:
        return f"```{self.language.strip()}\n{self.code.rstrip()}\n```"

    def to_html(self) -> str:
        language = escape(self.language.strip() or "text")
        code = escape(self.code.rstrip())
        return (
            f'<pre><div class="code-language">{language}</div>'
            f'<code>{code}</code></pre>'
        )


@dataclass
class ListBlock(MarkdownBlock):
    items: list[str]
    ordered: bool = False

    block_type = "list"

    def to_markdown(self) -> str:
        if self.ordered:
            return "\n".join(
                f"{index}. {item.strip()}"
                for index, item in enumerate(self.items, start=1)
                if item.strip()
            )
        return "\n".join(
            f"- {item.strip()}" for item in self.items if item.strip()
        )

    def to_html(self) -> str:
        tag = "ol" if self.ordered else "ul"
        items = "".join(f"<li>{escape(item.strip())}</li>" for item in self.items if item.strip())
        return f"<{tag}>{items}</{tag}>"


@dataclass
class MermaidBlock(MarkdownBlock):
    code: str = "xychart-beta\n    title \"Example\"\n    x-axis [\"A\", \"B\", \"C\"]\n    y-axis \"Value\" 0 --> 100\n    bar [30, 65, 45]"

    block_type = "mermaid"

    def to_markdown(self) -> str:
        return f"```mermaid\n{self.code.rstrip()}\n```"

    def to_html(self) -> str:
        code = self.code.rstrip()
        chart = _render_xychart_preview(code)
        if chart:
            return chart

        escaped = escape(code)
        return (
            '<div class="mermaid-preview">'
            '<strong>Mermaid diagram</strong>'
            '<p class="mermaid-preview__note">This Mermaid diagram will render on GitHub. ' 'The live preview currently shows its source.</p>'
            '<pre><code>' + escaped + '</code></pre>'
            '</div>'
        )


def _render_xychart_preview(code: str) -> str:
    """Render a dependency-free, table-based Mermaid xychart preview.

    QTextDocument (used by the live preview) has limited CSS support and does
    not reliably implement flexbox. The chart is therefore built with HTML
    tables and fixed-height cells so bars keep their geometry inside Qt.
    """
    import re

    if not re.search(r"^\s*xychart-beta\b", code, re.MULTILINE):
        return ""

    title_match = re.search(r"^\s*title\s+[\"](.*?)[\"]\s*$", code, re.MULTILINE)
    x_match = re.search(r"^\s*x-axis\s*\[(.*?)\]\s*$", code, re.MULTILINE)
    y_match = re.search(
        r"^\s*y-axis(?:\s+[\"](.*?)[\"])?\s+(-?\d+(?:\.\d+)?)\s*-->\s*(-?\d+(?:\.\d+)?)\s*$",
        code,
        re.MULTILINE,
    )
    bar_match = re.search(r"^\s*bar\s*\[(.*?)\]\s*$", code, re.MULTILINE)
    line_match = re.search(r"^\s*line\s*\[(.*?)\]\s*$", code, re.MULTILINE)

    if not x_match or not (bar_match or line_match):
        return ""

    def parse_items(raw: str):
        return [item.strip().strip('"\'') for item in raw.split(',') if item.strip()]

    labels = parse_items(x_match.group(1))
    values_raw = (bar_match or line_match).group(1)
    try:
        values = [float(v.strip()) for v in values_raw.split(',') if v.strip()]
    except ValueError:
        return ""

    count = min(len(labels), len(values))
    if count == 0:
        return ""
    labels, values = labels[:count], values[:count]

    if y_match:
        y_min = float(y_match.group(2))
        y_max = float(y_match.group(3))
    else:
        y_min = min(0.0, min(values))
        y_max = max(values)
    if y_max <= y_min:
        y_max = y_min + 1

    title = title_match.group(1) if title_match else "Chart"
    y_label = y_match.group(1) if y_match and y_match.group(1) else ""
    is_line = bool(line_match)

    def fmt(value: float) -> str:
        return f"{value:g}"

    # Fixed five-step scale. Fixed rows are deliberate: QTextDocument renders
    # them consistently across Qt versions, unlike CSS flex/grid layouts.
    ticks = [y_min + (y_max - y_min) * i / 4 for i in range(4, -1, -1)]
    tick_rows = "".join(
        f'<tr><td class="xychart-y-label">{escape(fmt(tick))}</td>'
        f'<td class="xychart-grid-cell"></td></tr>'
        for tick in ticks
    )

    if is_line:
        points = []
        span = max(y_max - y_min, 1)
        for label, value in zip(labels, values):
            ratio = max(0.0, min(1.0, (value - y_min) / span))
            dot_offset = max(6, int(ratio * 130))
            points.append(
                '<td valign="bottom" align="center" class="xychart-column">'
                f'<div class="xychart-value">{escape(fmt(value))}</div>'
                f'<div style="height:{dot_offset}px;">'
                f'<span class="xychart-line-dot"></span>'
                '</div>'
                f'<div class="xychart-label">{escape(label)}</div>'
                '</td>'
            )
        plot = '<table width="100%" cellspacing="0" cellpadding="0"><tr>' + ''.join(points) + '</tr></table>'
    else:
        bars = []
        span = y_max - y_min
        for label, value in zip(labels, values):
            ratio = max(0.0, min(1.0, (value - y_min) / span))
            height = max(4, int(ratio * 145))
            bars.append(
                '<td valign="bottom" align="center" class="xychart-column">'
                f'<div class="xychart-value">{escape(fmt(value))}</div>'
                f'<table width="100%" height="145" cellspacing="0" cellpadding="0"><tr><td valign="bottom" align="center">'
                f'<div class="xychart-bar" style="height:{height}px;"></div>'
                '</td></tr></table>'
                f'<div class="xychart-label">{escape(label)}</div>'
                '</td>'
            )
        plot = '<table width="100%" cellspacing="0" cellpadding="0"><tr>' + ''.join(bars) + '</tr></table>'

    axis_title = f'<span class="xychart-axis-title">{escape(y_label)}</span>' if y_label else ''
    chart_kind = 'Line chart' if is_line else 'Bar chart'
    return (
        '<div class="mermaid-preview xychart-preview">'
        '<div style="margin-bottom:12px;">'
        f'<div class="xychart-title">{escape(title)}</div>'
        f'<div class="xychart-meta">{chart_kind} · Mermaid xychart-beta{axis_title}</div>'
        '</div>'
        '<table width="100%" cellspacing="0" cellpadding="0">'
        f'<tr><td width="42" valign="top"><table width="100%" cellspacing="0" cellpadding="0">{tick_rows}</table></td>'
        f'<td valign="top" class="xychart-plot-cell">{plot}</td></tr>'
        '</table>'
        '</div>'
    )


@dataclass
class TechStackBlock(MarkdownBlock):
    title: str = "🛠️ Tech Stack"
    items: list[tuple[str, str]] = None

    block_type = "tech_stack"

    def __post_init__(self):
        if self.items is None:
            self.items = [
                ("JavaScript", "https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-plain.svg"),
                ("React", "https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg"),
                ("HTML", "https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg"),
                ("CSS", "https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg"),
            ]

    def to_markdown(self) -> str:
        lines = [f"## {self.title}", "", '<div style="display: inline_block"><br>']
        for name, url in self.items:
            if name.strip() and url.strip():
                safe_name = name.replace('"', '&quot;')
                lines.append(f'  <img align="center" alt="{safe_name}" height="30" width="40" src="{url.strip()}">')
        lines += ['</div>']
        return "\n".join(lines)

    def to_html(self) -> str:
        imgs = "".join(
            f'<img src="{escape(url.strip())}" alt="{escape(name.strip())}" width="40" height="30" style="object-fit:contain;margin-right:8px;">'
            for name, url in self.items if name.strip() and url.strip()
        )
        return f'<section class="widget tech-stack"><h2>{escape(self.title)}</h2><div>{imgs}</div></section>'


@dataclass
class GitHubStatsBlock(MarkdownBlock):
    username: str = ""
    theme: str = "dark"
    include_all_commits: bool = True
    count_private: bool = True
    show_top_languages: bool = True

    block_type = "github_stats"

    def _base(self) -> str:
        return "https://github-readme-stats.vercel.app/api"

    def to_markdown(self) -> str:
        user = self.username.strip()
        stats = (
            f"![GitHub Stats]({self._base()}?username={user}"
            f"&show_icons=true&theme={self.theme}"
            f"&include_all_commits={'true' if self.include_all_commits else 'false'}"
            f"&count_private={'true' if self.count_private else 'false'})"
        )
        lines = ["## 📊 GitHub Stats", "", stats]
        if self.show_top_languages:
            lines += ["", f"![Top Langs]({self._base()}/top-langs/?username={user}&layout=compact&langs_count=7&theme={self.theme})"]
        return "\n".join(lines)

    def to_html(self) -> str:
        user = escape(self.username.strip())
        theme = escape(self.theme)
        if not user:
            return '<section class="widget github-stats"><h2>📊 GitHub Stats</h2><p>Set a GitHub username to preview these widgets.</p></section>'
        src = f'{self._base()}?username={user}&show_icons=true&theme={theme}&include_all_commits={str(self.include_all_commits).lower()}&count_private={str(self.count_private).lower()}'
        html = f'<section class="widget github-stats"><h2>📊 GitHub Stats</h2><img src="{src}" alt="GitHub Stats">'
        if self.show_top_languages:
            lang_src = f'{self._base()}/top-langs/?username={user}&layout=compact&langs_count=7&theme={theme}'
            html += f'<img src="{lang_src}" alt="Top Languages">'
        return html + '</section>'


@dataclass
class SocialLinksBlock(MarkdownBlock):
    title: str = "🔗 Connect With Me"
    links: list[tuple[str, str]] = None

    block_type = "social_links"

    def __post_init__(self):
        if self.links is None:
            self.links = [("LinkedIn", "https://www.linkedin.com/")]

    def to_markdown(self) -> str:
        badges = []
        for label, url in self.links:
            label = label.strip()
            url = url.strip()
            if not label or not url:
                continue
            badge_label = label.replace(" ", "_")
            badge = (
                f'<a href="{url}" target="_blank">'
                f'<img src="https://img.shields.io/badge/-{badge_label}-%230077B5?style=for-the-badge&logo={label.lower()}&logoColor=white">'
                f'</a>'
            )
            badges.append(badge)

        lines = [f"## {self.title}", ""]
        if badges:
            # Keeping the anchors on the same HTML line lets GitHub render
            # the badges horizontally instead of treating each one as a row.
            lines.append('<div>' + ' '.join(badges) + '</div>')
        return "\n".join(lines)

    def to_html(self) -> str:
        cells = []
        for label, url in self.links:
            label = label.strip()
            url = url.strip()
            if not label or not url:
                continue
            cells.append(
                '<td style="padding-right:8px; vertical-align:middle;">'
                f'<a href="{escape(url)}"><span class="social-badge">{escape(label)}</span></a>'
                '</td>'
            )
        links = '<table cellspacing="0" cellpadding="0"><tr>' + ''.join(cells) + '</tr></table>'
        return f'<section class="widget social-links"><h2>{escape(self.title)}</h2>{links}</section>'



@dataclass
class GitHubContributionsBlock(MarkdownBlock):
    username: str = ""
    title: str = "GitHub Contributions"
    theme: str = "dark"
    color: str = "40c463"

    block_type = "github_contributions"

    def _url(self) -> str:
        user = self.username.strip()
        if not user:
            return ""
        theme = (self.theme or "dark").strip().lower()
        color = (self.color or "").strip().lstrip("#")
        if not color:
            color = "40c463"
        if theme == "light":
            return f"https://ghchart.xqsit94.in/light:{color}/{user}"
        return f"https://ghchart.xqsit94.in/dark:{color}/{user}"

    def to_markdown(self) -> str:
        url = self._url()
        title = self.title.strip() or "GitHub Contributions"
        if not url:
            return f"## {title}\n\n<!-- Add a GitHub username to generate the contribution graph. -->"
        return f"## {title}\n\n[![GitHub Contributions](https://ghchart.xqsit94.in/{'light' if self.theme == 'light' else 'dark'}:{(self.color or '40c463').strip().lstrip('#')}/{self.username.strip()})](https://github.com/{self.username.strip()})"

    def to_html(self) -> str:
        title = escape(self.title.strip() or "GitHub Contributions")
        url = escape(self._url())
        user = escape(self.username.strip())
        if not user or not url:
            return (
                '<section class="widget github-contributions">'
                f'<h2>{title}</h2>'
                '<p>Set a GitHub username to preview the contribution graph.</p>'
                '</section>'
            )
        return (
            '<section class="widget github-contributions">'
            f'<h2>{title}</h2>'
            f'<a href="https://github.com/{user}">'
            f'<img src="{url}" alt="GitHub contributions for {user}" style="max-width:100%;height:auto;">'
            '</a></section>'
        )


@dataclass
class CustomStatsBlock(MarkdownBlock):
    title: str = "📊 My Stats"
    description: str = ""
    stats: list[tuple[str, str, str, str]] = None

    block_type = "custom_stats"

    def __post_init__(self):
        if self.stats is None:
            self.stats = [("Projects", "12", "", ""), ("Commits", "245", "", ""), ("Followers", "86", "", "")]

    def to_markdown(self) -> str:
        lines = [f"## {self.title}", ""]
        if self.description.strip():
            lines += [self.description.strip(), ""]
        lines.append('<div style="display:flex;flex-wrap:wrap;gap:10px;">')
        for label, value, icon, link in self.stats:
            if not label.strip() and not value.strip():
                continue
            content = f'<strong>{value.strip()}</strong><br><sub>{label.strip()}</sub>'
            if icon.strip():
                content = f'<img src="{icon.strip()}" width="24" height="24" alt=""> {content}'
            card = f'<div style="padding:12px 16px;border:1px solid #30363d;border-radius:8px;min-width:110px;text-align:center;">{content}</div>'
            if link.strip():
                card = f'<a href="{link.strip()}" target="_blank">{card}</a>'
            lines.append(card)
        lines.append('</div>')
        return "\n".join(lines)

    def to_html(self) -> str:
        cards=[]
        for label, value, icon, link in self.stats:
            if not label.strip() and not value.strip():
                continue
            icon_html = f'<img src="{escape(icon.strip())}" width="24" height="24" alt="">' if icon.strip() else ''
            card = (f'<div class="custom-stat-card">{icon_html}'
                    f'<strong>{escape(value.strip())}</strong>'
                    f'<small>{escape(label.strip())}</small></div>')
            if link.strip():
                card = f'<a href="{escape(link.strip())}">{card}</a>'
            cards.append(card)
        description = f'<p>{escape(self.description.strip())}</p>' if self.description.strip() else ''
        return (f'<section class="widget custom-stats"><h2>{escape(self.title)}</h2>'
                f'{description}<div class="custom-stats-grid">{"".join(cards)}</div></section>')


def block_to_html(block: MarkdownBlock) -> str:
    return block.to_html()
