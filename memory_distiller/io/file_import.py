"""File import utilities for uploaded text files."""

from __future__ import annotations

from typing import Final

from memory_distiller.io.html_chat_import import parse_chatgpt_html_export

_ALLOWED_EXTENSIONS: Final[tuple[str, ...]] = (".txt", ".md", ".markdown")
_CHAT_LOG_EXTENSIONS: Final[tuple[str, ...]] = (".txt", ".md", ".markdown", ".html", ".htm")


def decode_uploaded_text(data: bytes, *, filename: str | None = None) -> str:
    """Decode UTF-8 bytes to text.

    Args:
        data: Raw bytes from uploaded file.
        filename: Optional filename for error messages.

    Returns:
        Decoded text string. Empty bytes yields empty string.

    Raises:
        ValueError: If bytes cannot be decoded as UTF-8.
    """
    if not data:
        return ""

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as e:
        filename_part = f" (file: {filename!r})" if filename else ""
        raise ValueError(f"Failed to decode{filename_part} as UTF-8: {e}") from None


def validate_text_file_extension(filename: str) -> bool:
    """Validate filename has an allowed text file extension.

    Args:
        filename: Name of the file to check.

    Returns:
        True if extension is .txt, .md, or .markdown (case-insensitive).
    """
    return filename.lower().endswith(_ALLOWED_EXTENSIONS)


def read_uploaded_text(data: bytes, filename: str) -> str:
    """Read and decode an uploaded text file.

    Args:
        data: Raw bytes from uploaded file.
        filename: Name of the file to validate extension.

    Returns:
        Decoded text string.

    Raises:
        ValueError: If extension is not allowed or decoding fails.
    """
    if not validate_text_file_extension(filename):
        allowed = ", ".join(sorted(_ALLOWED_EXTENSIONS))
        raise ValueError(f"Invalid file extension for {filename!r}. Allowed: {allowed}")
    return decode_uploaded_text(data, filename=filename)


def validate_chat_log_extension(filename: str) -> bool:
    """Validate filename has an allowed chat log file extension.

    Args:
        filename: Name of the file to check.

    Returns:
        True if extension is .txt, .md, .markdown, .html, or .htm (case-insensitive).
    """
    return filename.lower().endswith(_CHAT_LOG_EXTENSIONS)


def read_chat_log(data: bytes, filename: str) -> str:
    """Read and decode an uploaded chat log file.

    For .html and .htm files, the content is parsed as ChatGPT HTML export
    and converted to plain text format.

    Args:
        data: Raw bytes from uploaded file.
        filename: Name of the file to validate extension.

    Returns:
        Decoded text string, or parsed HTML content for .html/.htm files.

    Raises:
        ValueError: If extension is not allowed.
        HtmlChatImportError: If HTML parsing fails.
    """
    if not validate_chat_log_extension(filename):
        allowed = ", ".join(sorted(_CHAT_LOG_EXTENSIONS))
        raise ValueError(f"Invalid file extension for {filename!r}. Allowed: {allowed}")

    decoded = decode_uploaded_text(data, filename=filename)
    lower_name = filename.lower()

    if lower_name.endswith(".html") or lower_name.endswith(".htm"):
        return parse_chatgpt_html_export(decoded)

    return decoded
