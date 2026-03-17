# Business Assistant Web Plugin

Web operations plugin for Business Assistant v2. Downloads files from URLs to a local directory.

## Setup

1. Set `WEB_DOWNLOAD_PATH` environment variable to the directory where files should be saved
2. Optionally set `WEB_MAX_DOWNLOAD_SIZE` (bytes, default: 104857600 = 100 MB)
3. Add `business_assistant_web` to the `PLUGINS` variable in your `.env`
4. Run `uv sync` in the business-assistant-v2 directory

## Tools

### web_download_url

Downloads a file from a URL (http/https) to the configured download directory.

**Parameters:**
- `url` (str) — Full URL including scheme (e.g., `https://example.com/file.zip`)

**Returns:** JSON with `path`, `filename`, `size`, `status`

## Development

```bash
uv sync --all-extras
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/
```
