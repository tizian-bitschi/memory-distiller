"""Memory renderer: serializes MemoryDocument to deterministic memory_full.md format."""

from __future__ import annotations

from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.io.memory_writer import write_memory_document


def render_memory_document(document: MemoryDocument) -> str:
    """Serialize a MemoryDocument to deterministic memory_full.md format.

    This is a thin wrapper around write_memory_document that provides
    a semantic name for the rendering operation in the merge pipeline.

    Args:
        document: The MemoryDocument to serialize.

    Returns:
        Formatted text representation in memory_full.md format.
    """
    return write_memory_document(document)
