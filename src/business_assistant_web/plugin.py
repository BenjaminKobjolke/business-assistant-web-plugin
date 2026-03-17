"""Plugin registration -- defines PydanticAI tools for web operations."""

from __future__ import annotations

import logging

from business_assistant.agent.deps import Deps
from business_assistant.plugins.registry import PluginInfo, PluginRegistry
from pydantic_ai import RunContext, Tool

from .config import load_web_settings
from .constants import (
    PLUGIN_CATEGORY,
    PLUGIN_DATA_WEB_SERVICE,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    SYSTEM_PROMPT_WEB,
)
from .service import WebService

logger = logging.getLogger(__name__)


def _get_service(ctx: RunContext[Deps]) -> WebService:
    """Retrieve the WebService from plugin_data."""
    return ctx.deps.plugin_data[PLUGIN_DATA_WEB_SERVICE]


def _web_download_url(ctx: RunContext[Deps], url: str) -> str:
    """Download a file from a URL to the local download directory.

    Provide the full URL including http:// or https://.
    The file is saved with its original filename from the URL.
    Returns JSON with: path, filename, size, status.
    """
    logger.info("web_download_url: url=%r", url)
    return _get_service(ctx).download_url(url)


def register(registry: PluginRegistry) -> None:
    """Register the web plugin with the plugin registry.

    Reads WEB_DOWNLOAD_PATH from environment. Skips registration
    if not configured.
    """
    from business_assistant.config.log_setup import add_plugin_logging

    add_plugin_logging("web", "business_assistant_web")

    settings = load_web_settings()
    if settings is None:
        logger.info("Web plugin: WEB_DOWNLOAD_PATH not configured, skipping")
        return

    service = WebService(settings)

    tools = [
        Tool(_web_download_url, name="web_download_url"),
    ]

    info = PluginInfo(
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        system_prompt_extra=SYSTEM_PROMPT_WEB,
        category=PLUGIN_CATEGORY,
    )

    registry.register(info, tools)
    registry.plugin_data[PLUGIN_DATA_WEB_SERVICE] = service

    logger.info("Web plugin registered with %d tools", len(tools))
