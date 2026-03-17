"""Test fixtures for web plugin tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from business_assistant_web.config import WebSettings
from business_assistant_web.service import WebService


@pytest.fixture
def download_dir(tmp_path: Path) -> Path:
    """Create a temporary download directory."""
    dl = tmp_path / "downloads"
    dl.mkdir()
    return dl


@pytest.fixture
def settings(download_dir: Path) -> WebSettings:
    """Create WebSettings pointing to the tmp download directory."""
    return WebSettings(download_path=str(download_dir), max_download_size=10_485_760)


@pytest.fixture
def service(settings: WebSettings) -> WebService:
    """Create a WebService from the test settings."""
    return WebService(settings)
