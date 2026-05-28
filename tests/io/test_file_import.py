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


class TestValidateChatLogExtension:
    """Tests for validate_chat_log_extension function."""

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("document.html", True),
            ("document.htm", True),
            ("document.txt", True),
            ("document.md", True),
            ("document.markdown", True),
            ("DOCUMENT.HTML", True),
            ("DOCUMENT.HTM", True),
            ("Document.Html", True),
            ("Document.Htm", True),
        ],
    )
    def test_allowed_extensions_return_true(self, filename: str, expected: bool) -> None:
        from memory_distiller.io.file_import import validate_chat_log_extension

        result = validate_chat_log_extension(filename)
        assert result is expected

    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("document.pdf", False),
            ("document.py", False),
            ("document.docx", False),
            ("document", False),
            ("document.txt.gz", False),
            ("document.html.zip", False),
        ],
    )
    def test_disallowed_extensions_return_false(self, filename: str, expected: bool) -> None:
        from memory_distiller.io.file_import import validate_chat_log_extension

        result = validate_chat_log_extension(filename)
        assert result is expected


class TestReadChatLog:
    """Tests for read_chat_log function."""

    def test_html_file_calls_html_conversion(self) -> None:
        """HTML file content should be parsed via HTML conversion."""
        from memory_distiller.io.file_import import read_chat_log

        html_content = '<div class="message user-message">Hello</div>'
        data = html_content.encode("utf-8")
        result = read_chat_log(data, "chat.html")
        assert "User: Hello" in result

    def test_htm_file_calls_html_conversion(self) -> None:
        """HTM file content should be parsed via HTML conversion."""
        from memory_distiller.io.file_import import read_chat_log

        html_content = '<div class="message assistant-message">Hi there!</div>'
        data = html_content.encode("utf-8")
        result = read_chat_log(data, "chat.htm")
        assert "Assistant: Hi there!" in result

    def test_txt_file_behaves_as_before(self) -> None:
        """TXT file should be decoded directly like before."""
        from memory_distiller.io.file_import import read_chat_log

        content = "Plain text chat log"
        data = content.encode("utf-8")
        result = read_chat_log(data, "chat.txt")
        assert result == content

    def test_md_file_behaves_as_before(self) -> None:
        """MD file should be decoded directly like before."""
        from memory_distiller.io.file_import import read_chat_log

        content = "# Markdown chat log"
        data = content.encode("utf-8")
        result = read_chat_log(data, "chat.md")
        assert result == content

    def test_markdown_file_behaves_as_before(self) -> None:
        """Markdown file should be decoded directly like before."""
        from memory_distiller.io.file_import import read_chat_log

        content = "## Markdown content"
        data = content.encode("utf-8")
        result = read_chat_log(data, "chat.markdown")
        assert result == content

    def test_invalid_extension_raises_value_error(self) -> None:
        """Invalid extension should raise ValueError."""
        from memory_distiller.io.file_import import read_chat_log

        data = b"some content"
        with pytest.raises(ValueError, match="Invalid file extension"):
            read_chat_log(data, "document.pdf")

    def test_html_parse_error_raises_html_chat_import_error(self) -> None:
        """Malformed HTML should raise HtmlChatImportError."""
        from memory_distiller.io.file_import import read_chat_log
        from memory_distiller.io.html_chat_import import HtmlChatImportError

        html_content = "<div><p>No message structure here</p></div>"
        data = html_content.encode("utf-8")
        with pytest.raises(HtmlChatImportError, match="No supported message structure"):
            read_chat_log(data, "chat.html")
