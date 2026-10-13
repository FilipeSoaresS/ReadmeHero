from __future__ import annotations

import base64
import hashlib
import re
import urllib.error
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QStandardPaths, QUrl, QObject, Signal
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QTextBrowser
from PySide6.QtGui import QTextDocument


class _DownloadSignals(QObject):
    finished = Signal(str, bytes, str)
    failed = Signal(str)


class RemoteImageBrowser(QTextBrowser):
    """Non-blocking QTextBrowser with cached remote image support.

    Remote images are never downloaded on the GUI thread. The HTML is first
    rendered with a tiny transparent placeholder, while downloads happen in a
    worker thread. Once a resource arrives, the document is rendered again
    using the cached local resource.
    """

    USER_AGENT = "ReadMe-Hero/0.2.24"
    TIMEOUT = 6
    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="readme-image")
    _shared_memory_cache: dict[str, QImage] = {}
    _shared_pending: set[str] = set()
    _placeholder_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
        "+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_cache: dict[str, QImage] = {}
        self._current_source_html = ""
        self._render_generation = 0
        self._signals = _DownloadSignals()
        self._signals.finished.connect(self._download_finished)
        self._signals.failed.connect(self._download_failed)

        cache_root = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        if not cache_root:
            cache_root = str(Path.home() / ".cache")
        self.cache_dir = Path(cache_root) / "ReadMeHero" / "external-images"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.placeholder_path = self.cache_dir / "placeholder.png"
        if not self.placeholder_path.exists():
            self.placeholder_path.write_bytes(self._placeholder_data)

    def setHtml(self, html: str):  # noqa: N802 - Qt API
        self._current_source_html = html or ""
        self._render_generation += 1
        rendered_html = self._prepare_remote_images(self._current_source_html)
        super().setHtml(rendered_html)

    def _prepare_remote_images(self, html: str) -> str:
        urls = set(re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)[\"']", html, flags=re.I))
        replacements = {}

        for url in urls:
            local = self._cached_file(url)
            if local:
                replacements[url] = QUrl.fromLocalFile(str(local)).toString()
                continue

            image = self._image_cache.get(url) or self._shared_memory_cache.get(url)
            if image is not None and not image.isNull():
                local = self._write_qimage_cache(url, image)
                replacements[url] = QUrl.fromLocalFile(str(local)).toString()
                continue

            replacements[url] = QUrl.fromLocalFile(str(self.placeholder_path)).toString()
            self._schedule_download(url)

        for remote, local in replacements.items():
            html = html.replace(remote, local)
        return html

    def _schedule_download(self, url: str):
        if url in self._shared_pending:
            return
        self._shared_pending.add(url)
        self._executor.submit(self._download_worker, url)

    def _download_worker(self, url: str):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.USER_AGENT,
                    "Accept": "image/avif,image/webp,image/svg+xml,image/png,image/jpeg,image/*,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(request, timeout=self.TIMEOUT) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
            self._signals.finished.emit(url, data, content_type)
        except (OSError, urllib.error.URLError, ValueError) as exc:
            self._signals.failed.emit(url)

    def _download_finished(self, url: str, data: bytes, content_type: str):
        self._shared_pending.discard(url)
        image = self._decode_image(data, url, content_type)
        if image is None or image.isNull():
            return

        self._image_cache[url] = image
        self._shared_memory_cache[url] = image
        self._write_qimage_cache(url, image)
        self.setHtml(self._current_source_html)

    def _download_failed(self, url: str):
        self._shared_pending.discard(url)

    def _cached_file(self, url: str) -> Path | None:
        path = self.cache_dir / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.png"
        return path if path.exists() and path.stat().st_size > 0 else None

    def _write_qimage_cache(self, url: str, image: QImage) -> Path:
        path = self.cache_dir / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.png"
        if not path.exists():
            image.save(str(path), "PNG")
        return path

    @staticmethod
    def _decode_image(data: bytes, url: str, content_type: str) -> QImage | None:
        is_svg = "svg" in content_type.lower() or url.lower().split("?", 1)[0].endswith(".svg") or b"<svg" in data[:2048].lower()
        if is_svg:
            renderer = QSvgRenderer(data)
            if not renderer.isValid():
                return None
            size = renderer.defaultSize()
            if not size.isValid() or size.width() <= 0 or size.height() <= 0:
                size.setWidth(128)
                size.setHeight(128)
            scale = min(256 / max(size.width(), 1), 256 / max(size.height(), 1), 1.0)
            target = size.__class__(
                max(1, int(size.width() * scale)),
                max(1, int(size.height() * scale)),
            )
            image = QImage(target, QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            return image

        image = QImage()
        return image if image.loadFromData(data) else None

    def clear_remote_cache(self):
        self._image_cache.clear()
        self._shared_memory_cache.clear()
