"""Memory writer: serializes MemoryDocument back to memory_full.md format."""

from memory_distiller.domain.memory_entry import (
    MemoryDocument,
    MemoryEntry,
)


def _entry_to_line(entry: MemoryEntry) -> str:
    """Convert a MemoryEntry to a pipe-delimited line."""
    return "|".join(
        [
            entry.scope,
            entry.type.value,
            entry.priority.value,
            entry.stability.value,
            entry.statement,
            entry.evidence,
        ]
    )


def write_memory_document(doc: MemoryDocument) -> str:
    """Serialize a MemoryDocument back to memory_full.md formatted text.

    Args:
        doc: The MemoryDocument to serialize.

    Returns:
        Formatted text representation in memory_full.md format.
    """
    lines = ["# MEMORY_FULL", ""]

    # GLOBAL
    lines.append("## GLOBAL")
    lines.append("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE")
    for entry in doc.global_entries:
        lines.append(_entry_to_line(entry))
    lines.append("")

    # PROJECTS
    lines.append("## PROJECTS")
    lines.append("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE")
    for entry in doc.project_entries:
        lines.append(_entry_to_line(entry))
    lines.append("")

    # REPOS
    lines.append("## REPOS")
    lines.append("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE")
    for entry in doc.repo_entries:
        lines.append(_entry_to_line(entry))
    lines.append("")

    # TEMPORARY
    lines.append("## TEMPORARY")
    lines.append("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE")
    for entry in doc.temporary_entries:
        lines.append(_entry_to_line(entry))
    lines.append("")

    # DEPRECATED
    lines.append("## DEPRECATED")
    lines.append("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON")
    for deprecated in doc.deprecated_entries:
        entry = deprecated.entry
        deprecation_reason = deprecated.deprecation_reason
        lines.append(
            "|".join(
                [
                    entry.scope,
                    entry.type.value,
                    entry.priority.value,
                    entry.stability.value,
                    entry.statement,
                    entry.evidence,
                    deprecation_reason,
                ]
            )
        )
    lines.append("")

    # OFFENE_KLÄRUNGEN
    lines.append("## OFFENE_KLÄRUNGEN")
    lines.append("QUESTION|WHY_IT_MATTERS")
    for question, why_it_matters in doc.open_questions:
        lines.append(f"{question}|{why_it_matters}")

    return "\n".join(lines)
