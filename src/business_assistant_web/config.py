"""Web plugin settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import DEFAULT_MAX_DOWNLOAD_SIZE, ENV_WEB_DOWNLOAD_PATH, ENV_WEB_MAX_DOWNLOAD_SIZE


@dataclass(frozen=True)
class WebSettings:
    """Web plugin settings."""

    download_path: str
    max_download_size: int


def load_web_settings() -> WebSettings | None:
    """Load web settings from environment variables.

    Returns None if WEB_DOWNLOAD_PATH is not configured.
    """
    download_path = os.environ.get(ENV_WEB_DOWNLOAD_PATH, "").strip()
    if not download_path:
        return None

    max_size_raw = os.environ.get(ENV_WEB_MAX_DOWNLOAD_SIZE, "").strip()
    if max_size_raw:
        try:
            max_size = int(max_size_raw)
        except ValueError:
            max_size = DEFAULT_MAX_DOWNLOAD_SIZE
    else:
        max_size = DEFAULT_MAX_DOWNLOAD_SIZE

    return WebSettings(download_path=download_path, max_download_size=max_size)
