"""Tests for plugin registration."""

from __future__ import annotations

import pytest
from business_assistant.plugins.registry import PluginRegistry

from business_assistant_web.constants import PLUGIN_DATA_WEB_SERVICE
from business_assistant_web.plugin import register
from business_assistant_web.service import WebService


class TestPluginRegistration:
    def test_skips_when_unconfigured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("WEB_DOWNLOAD_PATH", raising=False)
        registry = PluginRegistry()
        register(registry)
        assert len(registry.plugins) == 0

    def test_registers_when_configured(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: object
    ) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", str(tmp_path))
        registry = PluginRegistry()
        register(registry)
        assert len(registry.plugins) == 1
        assert registry.plugins[0].name == "web"

    def test_registers_one_tool(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: object
    ) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", str(tmp_path))
        registry = PluginRegistry()
        register(registry)
        tools = registry.all_tools()
        assert len(tools) == 1
        assert tools[0].name == "web_download_url"

    def test_stores_service_in_plugin_data(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: object
    ) -> None:
        monkeypatch.setenv("WEB_DOWNLOAD_PATH", str(tmp_path))
        registry = PluginRegistry()
        register(registry)
        assert PLUGIN_DATA_WEB_SERVICE in registry.plugin_data
        assert isinstance(registry.plugin_data[PLUGIN_DATA_WEB_SERVICE], WebService)
