from app.core.blocks import MermaidBlock


def test_xychart_mermaid_renders_as_visual_preview():
    block = MermaidBlock(
        '''xychart-beta\n        title "Projects"\n        x-axis ["JS", "React", "Python"]\n        y-axis "Value" 0 --> 100\n        bar [30, 65, 45]'''
    )
    html = block.to_html()
    assert 'xychart-preview' in html
    assert 'Projects' in html
    assert 'JS' in html
    assert '65' in html
    assert '<div class="xychart-bar"' in html


def test_unsupported_mermaid_keeps_source_preview():
    block = MermaidBlock('flowchart TD\nA --> B')
    html = block.to_html()
    assert 'mermaid-preview__note' in html
    assert 'flowchart TD' in html


def test_xychart_preview_avoids_flex_layout():
    block = MermaidBlock()
    html = block.to_html()
    assert "display:flex" not in html
    assert "xychart-bar" in html
    assert "xychart-grid-cell" in html
