"""File export utilities for Memory Distiller."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

# Characters dangerous in filenames on Windows (and most filesystems)
_DANGEROUS_CHARS_PATTERN = re.compile(r'[?<>:"\\|*\x00-\x1f]')


@dataclass(frozen=True)
class ExportArtifact:
    """Artifact ready for download or storage.

    Attributes:
        filename: Safe filename without path components.
        content: File content as bytes.
        mime_type: MIME type of the content (default: text/plain).
    """

    filename: str
    content: bytes
    mime_type: str = "text/plain"


def build_text_download_payload(content: str) -> bytes:
    """Convert text content to UTF-8 encoded bytes.

    Args:
        content: Text string to encode.

    Returns:
        UTF-8 encoded bytes of the content. Empty string returns empty bytes.
    """
    return content.encode("utf-8")


def safe_export_filename(name: str, default: str = "export.txt") -> str:
    """Return a safe filename only (no paths) from user input.

    Strips path traversal components (e.g. "../secret.env" -> "secret.env").
    Replaces or removes dangerous characters.
    Preserves `.md` and `.txt` extensions if present.
    Returns default if the result would be empty.

    Args:
        name: The raw filename provided by the user.
        default: Fallback filename if sanitization yields empty result.

    Returns:
        A safe filename suitable for export without any path components.
    """
    if not name:
        return default

    # Extract just the basename to remove path traversal attempts
    normalized_name = name.replace("\\", "/")
    basename = os.path.basename(normalized_name)

    # If basename is empty (e.g. name was "/" or just ".."), use default
    if not basename:
        return default

    # Remove dangerous characters
    safe_name = _DANGEROUS_CHARS_PATTERN.sub("_", basename)

    # Remove any remaining path separators (shouldn't be any after basename extraction
    # but be defensive)
    safe_name = safe_name.replace("/", "_").replace("\\", "_")

    # Strip leading/trailing whitespace and dots (Windows reserved names)
    safe_name = safe_name.strip().strip(".")

    # Avoid empty result
    if not safe_name:
        return default

    return safe_name
