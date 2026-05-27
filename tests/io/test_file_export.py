"""Tests for file export utilities."""

from memory_distiller.io.file_export import (
    ExportArtifact,
    build_text_download_payload,
    safe_export_filename,
)


class TestBuildTextDownloadPayload:
    """Tests for UTF-8 bytes generation."""

    def test_encodes_to_utf8_bytes(self):
        """Plain text encodes to UTF-8 bytes."""
        content = "Hello, world!"
        result = build_text_download_payload(content)
        assert result == b"Hello, world!"

    def test_empty_string_returns_empty_bytes(self):
        """Empty string returns empty bytes."""
        result = build_text_download_payload("")
        assert result == b""

    def test_unicode_content_encodes_properly(self):
        """Unicode characters encode to correct UTF-8 bytes."""
        content = "München\n東京"
        result = build_text_download_payload(content)
        assert result == "München\n東京".encode("utf-8")


class TestSafeExportFilename:
    """Tests for safe filename generation."""

    def test_normal_filename_kept(self):
        """Normal filename is preserved."""
        assert safe_export_filename("report.txt") == "report.txt"
        assert safe_export_filename("readme.md") == "readme.md"
        assert safe_export_filename("memory-export.txt") == "memory-export.txt"

    def test_path_traversal_stripped(self):
        """Path traversal components are stripped."""
        assert safe_export_filename("../secret.env") == "secret.env"
        assert safe_export_filename("subfolder/../../password.txt") == "password.txt"
        assert safe_export_filename("C:\\Users\\hacker\\file.txt") == "file.txt"
        assert safe_export_filename("/etc/passwd") == "passwd"
        assert safe_export_filename("..\\windows\\system32\\config.sys") == "config.sys"

    def test_empty_input_falls_back_to_default(self):
        """Empty input returns default filename."""
        assert safe_export_filename("") == "export.txt"
        assert safe_export_filename("", default="custom.txt") == "custom.txt"

    def test_dangerous_characters_replaced(self):
        """Dangerous characters are replaced with underscore."""
        assert safe_export_filename("fi<le>.txt") == "fi_le_.txt"
        assert safe_export_filename("fi>le?.txt") == "fi_le_.txt"
        assert safe_export_filename('fi"le:.txt') == "fi_le_.txt"
        assert safe_export_filename("file|.txt") == "file_.txt"
        assert safe_export_filename("file*.txt") == "file_.txt"
        assert safe_export_filename("file?.txt") == "file_.txt"

    def test_whitespace_and_dots_stripped(self):
        """Leading/trailing whitespace and dots are stripped."""
        assert safe_export_filename("  file.txt  ") == "file.txt"
        assert safe_export_filename(".file.txt.") == "file.txt"

    def test_extension_preserved(self):
        """Extensions are preserved."""
        assert safe_export_filename("../attack.md") == "attack.md"
        assert safe_export_filename("script.txt") == "script.txt"

    def test_only_path_separators_returns_default(self):
        """Input that reduces to empty after sanitization uses default."""
        assert safe_export_filename("/") == "export.txt"
        assert safe_export_filename("..") == "export.txt"
        assert safe_export_filename(".") == "export.txt"

    def test_export_artifact_dataclass(self):
        """ExportArtifact frozen dataclass works correctly."""
        artifact = ExportArtifact(
            filename="test.md",
            content=b"# Memory",
            mime_type="text/markdown",
        )
        assert artifact.filename == "test.md"
        assert artifact.content == b"# Memory"
        assert artifact.mime_type == "text/markdown"

    def test_export_artifact_default_mime_type(self):
        """ExportArtifact defaults to text/plain mime type."""
        artifact = ExportArtifact(filename="log.txt", content=b"data")
        assert artifact.mime_type == "text/plain"
