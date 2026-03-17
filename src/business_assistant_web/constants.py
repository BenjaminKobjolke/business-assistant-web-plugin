"""Plugin-specific string constants."""

# Environment variable names
ENV_WEB_DOWNLOAD_PATH = "WEB_DOWNLOAD_PATH"
ENV_WEB_MAX_DOWNLOAD_SIZE = "WEB_MAX_DOWNLOAD_SIZE"

# Plugin name and category
PLUGIN_NAME = "web"
PLUGIN_CATEGORY = "web"
PLUGIN_DESCRIPTION = "Web operations (download files from URLs)"

# Plugin data keys
PLUGIN_DATA_WEB_SERVICE = "web_service"

# Limits
DEFAULT_MAX_DOWNLOAD_SIZE = 104_857_600  # 100 MB
DOWNLOAD_CHUNK_SIZE = 65_536  # 64 KB
MAX_FILENAME_LEN = 200
DOWNLOAD_TIMEOUT = 60

# Error messages
ERR_INVALID_URL_SCHEME = (
    "Invalid URL: only http:// and https:// URLs are supported. Got: '{scheme}'"
)
ERR_INVALID_URL = "Invalid URL: '{url}'"
ERR_DOWNLOAD_FAILED = "Download failed: {error}"
ERR_FILE_TOO_LARGE = "File too large: {size} bytes exceeds maximum {max_size} bytes"
ERR_CONTENT_LENGTH_TOO_LARGE = (
    "Remote file too large: Content-Length {size} bytes exceeds maximum {max_size} bytes"
)

# System prompt extra
SYSTEM_PROMPT_WEB = """You have access to web tools:
- web_download_url: Download a file from a URL to the local download directory. \
Provide the full URL (http:// or https://). The file is saved with its original \
filename from the URL. Returns the local file path, filename, and size. \
Maximum download size is 100 MB by default.

When the user asks to download a file from the internet or save a URL to disk, \
use this tool.

After downloading, you can chain with other tools:
- pm_store_file_in_project: copy the downloaded file into a project's Source folder
- fs_extract_zip: extract if the download is a zip archive"""
