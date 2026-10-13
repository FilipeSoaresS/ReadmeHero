from app.core.markdown import render_markdown


def test_render_markdown_preserves_mermaid_as_visual_preview():
    source = '''# Demo\n\n```mermaid\nxychart-beta\n    title "Projects"\n    x-axis ["JS", "React", "Python"]\n    y-axis "Value" 0 --> 100\n    bar [30, 65, 45]\n```\n\nAfter chart.'''

    html = render_markdown(source)

    assert 'xychart-preview' in html
    assert 'Projects' in html
    assert 'After chart.' in html
    assert 'READMe_HERO_MERMAID' not in html
