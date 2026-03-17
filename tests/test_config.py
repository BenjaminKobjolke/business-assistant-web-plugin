"""Tests for web plugin configuration loading."""

from __future__ import annotations

import pytest

from business_assistant_web.config import load_web_settings
from business_assistant_web.constants import DEFAULT_MAX_DOWNLOAD_SIZE


class TestLoadWebSettings:
    def test_returns_none_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WEB_DOWNLOAD_PATH", raising=False)
        assert load_web_settings() is None

    def test_returns_none_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "")
        assert load_web_settings() is None

    def test_returns_none_when_whitespace_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "   ")
        assert load_web_settings() is None

    def test_loads_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "D:/Downloads")
        settings = load_web_settings()
        assert settings is not None
        assert settings.download_path == "D:/Downloads"

    def test_default_max_download_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "D:/Downloads")
        monkeypatch.delenv("WEB_MAX_DOWNLOAD_SIZE", raising=False)
        settings = load_web_settings()
        assert settings is not None
        assert settings.max_download_size == DEFAULT_MAX_DOWNLOAD_SIZE

    def test_custom_max_download_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "D:/Downloads")
        monkeypatch.setenv("WEB_MAX_DOWNLOAD_SIZE", "5000000")
        settings = load_web_settings()
        assert settings is not None
        assert settings.max_download_size == 5_000_000

    def test_invalid_max_download_size_uses_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "D:/Downloads")
        monkeypatch.setenv("WEB_MAX_DOWNLOAD_SIZE", "not_a_number")
        settings = load_web_settings()
        assert settings is not None
        assert settings.max_download_size == DEFAULT_MAX_DOWNLOAD_SIZE

    def test_settings_is_frozen(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", "D:/Downloads")
        settings = load_web_settings()
        assert settings is not None
        with pytest.raises(AttributeError):
            settings.download_path = "other"  # type: ignore[misc]
