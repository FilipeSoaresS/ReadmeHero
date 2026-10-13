from app.core.blocks import CustomStatsBlock, TechStackBlock, GitHubStatsBlock, SocialLinksBlock

def test_special_blocks_markdown():
    assert "<div style=\"display: inline_block\"><br>" in TechStackBlock().to_markdown()
    assert "github-readme-stats.vercel.app" in GitHubStatsBlock(username="FilipeSoaresS").to_markdown()
    assert "Connect With Me" in SocialLinksBlock().to_markdown()


def test_custom_stats_block_generates_editable_cards():
    block = CustomStatsBlock(stats=[("Projects", "12", "", "https://example.com")])
    markdown = block.to_markdown()
    assert "## 📊 My Stats" in markdown
    assert "Projects" in markdown
    assert "12" in markdown
    assert "https://example.com" in markdown
