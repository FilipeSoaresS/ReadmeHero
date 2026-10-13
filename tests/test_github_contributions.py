from app.core.blocks import GitHubContributionsBlock

def test_contribution_markdown():
    b=GitHubContributionsBlock(username="octocat", theme="dark", color="40c463")
    md=b.to_markdown()
    assert "ghchart.xqsit94.in/dark:40c463/octocat" in md
    assert "github.com/octocat" in md

def test_contribution_html():
    b=GitHubContributionsBlock(username="octocat", theme="light", color="#2f81f7")
    html=b.to_html()
    assert "light:2f81f7/octocat" in html
