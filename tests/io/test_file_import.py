"""Tests for file_import module."""

from __future__ import annotations

import pytest

from memory_distiller.io.file_import import (
    decode_uploaded_text,
    read_uploaded_text,
    validate_text_file_extension,
)


class TestDecodeUploadedText:
    def test_valid_utf8_bytes_decode_to_text(self) -> None:
        data = "Hello, world!".encode("utf-8")
        result = decode_uploaded_text(data)
        assert result == "Hello, world!"

    def test_valid_utf8_with_unicode_chars(self) -> None:
        data = "Hëllö, wörld!".encode("utf-8")
        result = decode_uploaded_text(data)
        assert result == "Hëllö, wörld!"

    def test_empty_bytes_returns_empty_string(self) -> None:
        result = decode_uploaded_text(b"")
        assert result == ""

    def test_empty_bytes_with_filename_returns_empty_string(self) -> None:
        result = decode_uploaded_text(b"", filename="test.txt")
        assert result == ""

    def test_invalid_utf8_raises_value_error(self) -> None:
        data = b"\xff\xfe"
        with pytest.raises(ValueError, match="Failed to decode.*as UTF-8"):
            decode_uploaded_text(data)

    def test_invalid_utf8_with_filename_in_error(self) -> None:
        data = b"\xff\xfe"
        with pytest.raises(ValueError, match=r"file: .*test\.txt"):
            decode_uploaded_text(data, filename="test.txt")


class TestValidateTextFileExtension:
    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("document.txt", True),
            ("document.md", True),
            ("document.markdown", True),
            ("DOCUMENT.TXT", True),
            ("DOCUMENT.MD", True),
            ("DOCUMENT.MARKDOWN", True),
            ("Document.Txt", True),
            ("Document.Md", True),
            ("Document.Markdown", True),
        ],
    )
    def test_allowed_extensions_return_true(self, filename: str, expected: bool) -> None:
        result = validate_text_file_extension(filename)
        assert result is expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("document.pdf", False),
            ("document.py", False),
            ("document.docx", False),
            ("document", False),
            ("document.txt.gz", False),
        ],
    )
    def test_disallowed_extensions_return_false(self, filename: str, expected: bool) -> None:
        result = validate_text_file_extension(filename)
        assert result is expected


class TestReadUploadedText:
    def test_valid_file_reads_successfully(self) -> None:
        data = "Test content".encode("utf-8")
        result = read_uploaded_text(data, "document.txt")
        assert result == "Test content"

    def test_valid_markdown_file_reads_successfully(self) -> None:
        data = "# Header".encode("utf-8")
        result = read_uploaded_text(data, "readme.md")
        assert result == "# Header"

    def test_valid_markdown_extension_file_reads_successfully(self) -> None:
        data = "# Header".encode("utf-8")
        result = read_uploaded_text(data, "readme.markdown")
        assert result == "# Header"

    def test_invalid_extension_raises_value_error(self) -> None:
        data = b"some content"
        with pytest.raises(ValueError, match="Invalid file extension"):
            read_uploaded_text(data, "document.pdf")

    def test_invalid_extension_with_filename_in_error(self) -> None:
        data = b"some content"
        with pytest.raises(ValueError, match=r"document\.pdf"):
            read_uploaded_text(data, "document.pdf")

    def test_invalid_utf8_raises_value_error(self) -> None:
        data = b"\xff\xfe"
        with pytest.raises(ValueError, match="Failed to decode.*as UTF-8"):
            read_uploaded_text(data, "document.txt")
