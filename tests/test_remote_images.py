from pathlib import Path


def test_remote_image_browser_is_async():
    source = Path("app/ui/components/remote_image_browser.py").read_text(encoding="utf-8")
    assert "ThreadPoolExecutor" in source
    assert "_schedule_download" in source
    assert "timeout=self.TIMEOUT" in source
    assert "placeholder_path" in source
