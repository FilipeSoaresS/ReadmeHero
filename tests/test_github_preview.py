from pathlib import Path


def test_github_preview_component_exists():
    path = Path("app/ui/components/github_preview.py")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "class GitHubPreviewWindow" in text
    assert "set_markdown" in text
