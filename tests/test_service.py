"""Tests for web service."""

from __future__ import annotations

import json
import urllib.error
from http.client import HTTPResponse
from pathlib import Path
from unittest.mock import MagicMock, patch

from business_assistant_web.config import WebSettings
from business_assistant_web.service import WebService


class TestValidateUrl:
    def test_accepts_http_url(self, service: WebService) -> None:
        assert service._validate_url("http://example.com/file.txt") is None

    def test_accepts_https_url(self, service: WebService) -> None:
        assert service._validate_url("https://example.com/file.txt") is None

    def test_rejects_ftp_url(self, service: WebService) -> None:
        result = service._validate_url("ftp://example.com/file.txt")
        assert result is not None
        assert "ftp" in result

    def test_rejects_file_url(self, service: WebService) -> None:
        result = service._validate_url("file:///etc/passwd")
        assert result is not None
        assert "file" in result

    def test_rejects_empty_scheme(self, service: WebService) -> None:
        result = service._validate_url("example.com/file.txt")
        assert result is not None

    def test_rejects_no_netloc(self, service: WebService) -> None:
        result = service._validate_url("http://")
        assert result is not None


class TestExtractFilename:
    def test_extracts_filename_from_path(self, service: WebService) -> None:
        result = service._extract_filename("https://example.com/files/report.pdf")
        assert result == "report.pdf"

    def test_extracts_with_query_params(self, service: WebService) -> None:
        result = service._extract_filename("https://example.com/file.pdf?token=abc")
        assert result == "file.pdf"

    def test_returns_default_for_root_url(self, service: WebService) -> None:
        result = service._extract_filename("https://example.com/")
        assert result == "download"

    def test_returns_default_for_empty_path(self, service: WebService) -> None:
        result = service._extract_filename("https://example.com")
        assert result == "download"

    def test_url_decodes_filename(self, service: WebService) -> None:
        result = service._extract_filename("https://example.com/my%20file.pdf")
        assert "my" in result
        assert "file.pdf" in result

    def test_sanitizes_unsafe_characters(self, service: WebService) -> None:
        result = service._extract_filename('https://example.com/file<name>.txt')
        assert "<" not in result
        assert ">" not in result

    def test_handles_long_filename(self, service: WebService) -> None:
        long_name = "a" * 300 + ".zip"
        result = service._extract_filename(f"https://example.com/{long_name}")
        assert len(result) <= 200


class TestDownloadUrl:
    def _make_mock_response(
        self, data: bytes, content_length: str | None = None
    ) -> MagicMock:
        """Create a mock urllib response."""
        mock_resp = MagicMock(spec=HTTPResponse)
        mock_resp.headers = MagicMock()
        mock_resp.headers.get.return_value = content_length

        chunks = [data[i : i + 65536] for i in range(0, len(data), 65536)]
        chunks.append(b"")
        mock_resp.read.side_effect = chunks

        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_successful_download(
        self, mock_urlopen: MagicMock, service: WebService, download_dir: Path
    ) -> None:
        data = b"Hello, World!"
        mock_urlopen.return_value = self._make_mock_response(data, str(len(data)))

        result = service.download_url("https://example.com/hello.txt")
        parsed = json.loads(result)

        assert parsed["status"] == "downloaded"
        assert parsed["filename"] == "hello.txt"
        assert parsed["size"] == len(data)

        dest = Path(parsed["path"])
        assert dest.exists()
        assert dest.read_bytes() == data

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_preserves_filename_from_url(
        self, mock_urlopen: MagicMock, service: WebService, download_dir: Path
    ) -> None:
        data = b"zip content"
        mock_urlopen.return_value = self._make_mock_response(data)

        result = service.download_url(
            "https://example.com/S22_260087_Platzierung.zip"
        )
        parsed = json.loads(result)
        assert parsed["filename"] == "S22_260087_Platzierung.zip"

    def test_rejects_invalid_url(self, service: WebService) -> None:
        result = service.download_url("ftp://example.com/file.txt")
        assert "ftp" in result
        assert "Invalid" in result or "invalid" in result

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_rejects_content_length_too_large(
        self, mock_urlopen: MagicMock, download_dir: Path
    ) -> None:
        small_service = WebService(
            WebSettings(download_path=str(download_dir), max_download_size=1000)
        )
        mock_urlopen.return_value = self._make_mock_response(b"", "5000")

        result = small_service.download_url("https://example.com/big.zip")
        assert "too large" in result.lower()

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_stops_streaming_when_too_large(
        self, mock_urlopen: MagicMock, download_dir: Path
    ) -> None:
        small_service = WebService(
            WebSettings(download_path=str(download_dir), max_download_size=10)
        )
        data = b"x" * 100
        mock_resp = self._make_mock_response(data, content_length=None)
        mock_urlopen.return_value = mock_resp

        result = small_service.download_url("https://example.com/big.bin")
        assert "too large" in result.lower()

        dest = download_dir / "big.bin"
        assert not dest.exists()

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_handles_network_error(
        self, mock_urlopen: MagicMock, service: WebService
    ) -> None:
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        result = service.download_url("https://example.com/file.txt")
        assert "failed" in result.lower()
        assert "Connection refused" in result

    @patch("business_assistant_web.service.urllib.request.urlopen")
    def test_cleans_up_partial_file_on_error(
        self, mock_urlopen: MagicMock, service: WebService, download_dir: Path
    ) -> None:
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        service.download_url("https://example.com/partial.zip")

        dest = download_dir / "partial.zip"
        assert not dest.exists()

    def test_creates_download_directory(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "new" / "nested" / "dir"
        settings = WebSettings(download_path=str(new_dir), max_download_size=1000)
        WebService(settings)
        assert new_dir.is_dir()
