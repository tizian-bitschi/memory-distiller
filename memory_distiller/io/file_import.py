"""File import utilities for uploaded text files."""

from __future__ import annotations

from typing import Final

_ALLOWED_EXTENSIONS: Final[tuple[str, ...]] = (".txt", ".md", ".markdown")


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
