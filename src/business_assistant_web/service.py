"""Web service -- URL downloading and web operations."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .config import WebSettings
from .constants import (
    DOWNLOAD_CHUNK_SIZE,
    DOWNLOAD_TIMEOUT,
    ERR_CONTENT_LENGTH_TOO_LARGE,
    ERR_DOWNLOAD_FAILED,
    ERR_FILE_TOO_LARGE,
    ERR_INVALID_URL,
    ERR_INVALID_URL_SCHEME,
    MAX_FILENAME_LEN,
)

logger = logging.getLogger(__name__)

_UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_ALLOWED_SCHEMES = frozenset({"http", "https"})


class WebService:
    """Web operations service."""

    def __init__(self, settings: WebSettings) -> None:
        self._download_path = Path(settings.download_path)
        self._download_path.mkdir(parents=True, exist_ok=True)
        self._max_download_size = settings.max_download_size

    def download_url(self, url: str) -> str:
        """Download a file from a URL to the configured download directory."""
        error = self._validate_url(url)
        if error:
            return error

        filename = self._extract_filename(url)
        dest = self._download_path / filename

        try:
            with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT) as resp:  # noqa: S310
                content_length = resp.headers.get("Content-Length")
                if content_length:
                    try:
                        size = int(content_length)
                        if size > self._max_download_size:
                            return ERR_CONTENT_LENGTH_TOO_LARGE.format(
                                size=size, max_size=self._max_download_size
                            )
                    except ValueError:
                        pass

                bytes_written = 0
                with open(dest, "wb") as f:
                    while True:
                        chunk = resp.read(DOWNLOAD_CHUNK_SIZE)
                        if not chunk:
                            break
                        bytes_written += len(chunk)
                        if bytes_written > self._max_download_size:
                            f.close()
                            dest.unlink(missing_ok=True)
                            return ERR_FILE_TOO_LARGE.format(
                                size=bytes_written, max_size=self._max_download_size
                            )
                        f.write(chunk)

            logger.info("Downloaded %s (%d bytes) to %s", url, bytes_written, dest)
            return json.dumps({
                "path": str(dest),
                "filename": filename,
                "size": bytes_written,
                "status": "downloaded",
            })

        except (urllib.error.URLError, OSError, ValueError) as exc:
            dest.unlink(missing_ok=True)
            logger.error("Download failed for %s: %s", url, exc)
            return ERR_DOWNLOAD_FAILED.format(error=str(exc))

    def _validate_url(self, url: str) -> str | None:
        """Validate URL. Returns error string or None if valid."""
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            return ERR_INVALID_URL.format(url=url)

        if parsed.scheme not in _ALLOWED_SCHEMES:
            return ERR_INVALID_URL_SCHEME.format(scheme=parsed.scheme or "(empty)")
        if not parsed.netloc:
            return ERR_INVALID_URL.format(url=url)
        return None

    def _extract_filename(self, url: str) -> str:
        """Extract and sanitize filename from URL."""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.rstrip("/")
        name = path.split("/")[-1] if path else ""

        name = urllib.parse.unquote(name)
        return self._sanitize_filename(name) if name else "download"

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Remove unsafe characters and limit length."""
        name = name.replace("/", "_").replace("\\", "_")
        name = _UNSAFE_CHARS.sub("_", name)
        if len(name) > MAX_FILENAME_LEN:
            name = name[-MAX_FILENAME_LEN:]
        return name or "download"
