from app.core.blocks import SocialLinksBlock

def test_social_links_are_horizontal_in_markdown():
    block = SocialLinksBlock(links=[
        ('LinkedIn', 'https://linkedin.com'),
        ('GitHub', 'https://github.com'),
        ('Instagram', 'https://instagram.com'),
    ])
    md = block.to_markdown()
    assert '<div><a href="https://linkedin.com"' in md
    assert 'https://github.com' in md
    assert md.count('<a href=') == 3
    assert '</a> <a href=' in md

def test_social_links_preview_uses_single_row_table():
    block = SocialLinksBlock(links=[('LinkedIn', 'https://linkedin.com'), ('GitHub', 'https://github.com')])
    html = block.to_html()
    assert '<table' in html
    assert html.count('<td') == 2
