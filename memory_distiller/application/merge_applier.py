"""Merge applier: applies a MergePlan to existing memory."""

from __future__ import annotations

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)
from memory_distiller.domain.merge_plan import MergeDecision, MergePlan, MergePlanEntry
from memory_distiller.io.memory_parser import parse_memory_document


def apply_merge_plan(existing_memory: str, plan: MergePlan) -> MemoryDocument:
    """Apply a merge plan to existing memory and produce a new MemoryDocument.

    Args:
        existing_memory: The existing memory text in memory_full.md format.
        plan: The MergePlan containing entries to apply.

    Returns:
        A new MemoryDocument with all merge plan entries applied.

    Raises:
        ValueError: If an APPLY_UPDATE or APPLY_DEPRECATE targets an entry
            that does not exist in the existing memory.
    """
    # Parse existing memory
    doc = parse_memory_document(existing_memory)

    # Create copies of the entry lists to modify
    global_entries = list(doc.global_entries)
    project_entries = list(doc.project_entries)
    repo_entries = list(doc.repo_entries)
    temporary_entries = list(doc.temporary_entries)
    deprecated_entries = list(doc.deprecated_entries)
    open_questions = list(doc.open_questions)

    for entry in plan.entries:
        if entry.decision == MergeDecision.APPLY_ADD:
            _apply_add(
                entry,
                global_entries,
                project_entries,
                repo_entries,
                temporary_entries,
            )

        elif entry.decision == MergeDecision.APPLY_UPDATE:
            _apply_update(
                entry,
                global_entries,
                project_entries,
                repo_entries,
                temporary_entries,
            )

        elif entry.decision == MergeDecision.APPLY_DEPRECATE:
            _apply_deprecate(
                entry,
                global_entries,
                project_entries,
                repo_entries,
                temporary_entries,
                deprecated_entries,
            )

        elif entry.decision == MergeDecision.SKIP_DROP:
            # Do nothing
            pass

        elif entry.decision == MergeDecision.ADD_OPEN_QUESTION:
            open_questions.append((entry.statement, entry.reason))

    return MemoryDocument(
        global_entries=global_entries,
        project_entries=project_entries,
        repo_entries=repo_entries,
        temporary_entries=temporary_entries,
        deprecated_entries=deprecated_entries,
        open_questions=open_questions,
    )


def _find_entry_by_statement(
    target_statement: str,
    global_entries: list[MemoryEntry],
    project_entries: list[MemoryEntry],
    repo_entries: list[MemoryEntry],
    temporary_entries: list[MemoryEntry],
) -> tuple[MemoryEntry, list[MemoryEntry]] | None:
    """Find an entry by exact statement match.

    Args:
        target_statement: The statement to search for.
        global_entries: Global entries list.
        project_entries: Project entries list.
        repo_entries: Repo entries list.
        temporary_entries: Temporary entries list.

    Returns:
        Tuple of (found_entry, containing_list) or None if not found.
    """
    for entry in global_entries:
        if entry.statement == target_statement:
            return entry, global_entries
    for entry in project_entries:
        if entry.statement == target_statement:
            return entry, project_entries
    for entry in repo_entries:
        if entry.statement == target_statement:
            return entry, repo_entries
    for entry in temporary_entries:
        if entry.statement == target_statement:
            return entry, temporary_entries
    return None


def _entry_exists_with_statement(
    statement: str,
    global_entries: list[MemoryEntry],
    project_entries: list[MemoryEntry],
    repo_entries: list[MemoryEntry],
    temporary_entries: list[MemoryEntry],
) -> bool:
    """Check if an entry with the given statement already exists.

    Args:
        statement: The statement to check for.
        global_entries: Global entries list.
        project_entries: Project entries list.
        repo_entries: Repo entries list.
        temporary_entries: Temporary entries list.

    Returns:
        True if an entry with the statement exists, False otherwise.
    """
    return (
        _find_entry_by_statement(
            statement,
            global_entries,
            project_entries,
            repo_entries,
            temporary_entries,
        )
        is not None
    )


def _apply_add(
    entry: MergePlanEntry,
    global_entries: list[MemoryEntry],
    project_entries: list[MemoryEntry],
    repo_entries: list[MemoryEntry],
    temporary_entries: list[MemoryEntry],
) -> None:
    """Apply an APPLY_ADD decision.

    Args:
        entry: The merge plan entry to apply.
        global_entries: Global entries list to modify.
        project_entries: Project entries list to modify.
        repo_entries: Repo entries list to modify.
        temporary_entries: Temporary entries list to modify.
    """
    # Check for duplicates
    if _entry_exists_with_statement(
        entry.statement,
        global_entries,
        project_entries,
        repo_entries,
        temporary_entries,
    ):
        return  # Skip adding duplicate

    # Parse enum values
    mem_type = MemoryType(entry.type)
    priority = Priority(entry.priority)
    stability = Stability(entry.stability)

    new_entry = MemoryEntry(
        scope=entry.scope,
        type=mem_type,
        priority=priority,
        stability=stability,
        statement=entry.statement,
        evidence=entry.evidence,
    )

    # Add to correct section
    if entry.scope == "G":
        global_entries.append(new_entry)
    elif entry.scope.startswith("P:"):
        project_entries.append(new_entry)
    elif entry.scope.startswith("R:"):
        repo_entries.append(new_entry)
    elif entry.scope == "T":
        temporary_entries.append(new_entry)


def _apply_update(
    entry: MergePlanEntry,
    global_entries: list[MemoryEntry],
    project_entries: list[MemoryEntry],
    repo_entries: list[MemoryEntry],
    temporary_entries: list[MemoryEntry],
) -> None:
    """Apply an APPLY_UPDATE decision.

    Args:
        entry: The merge plan entry to apply.
        global_entries: Global entries list to modify.
        project_entries: Project entries list to modify.
        repo_entries: Repo entries list to modify.
        temporary_entries: Temporary entries list to modify.

    Raises:
        ValueError: If the target entry is not found.
    """
    # Parse enum values for new entry
    mem_type = MemoryType(entry.type)
    priority = Priority(entry.priority)
    stability = Stability(entry.stability)

    new_entry = MemoryEntry(
        scope=entry.scope,
        type=mem_type,
        priority=priority,
        stability=stability,
        statement=entry.statement,
        evidence=entry.evidence,
    )

    # Find existing entry by target statement
    result = _find_entry_by_statement(
        entry.target,
        global_entries,
        project_entries,
        repo_entries,
        temporary_entries,
    )

    if result is None:
        raise ValueError(f"APPLY_UPDATE failed: No entry found with statement: {entry.target!r}")

    found_entry, containing_list = result

    # Replace in the containing list
    index = containing_list.index(found_entry)
    containing_list[index] = new_entry


def _apply_deprecate(
    entry: MergePlanEntry,
    global_entries: list[MemoryEntry],
    project_entries: list[MemoryEntry],
    repo_entries: list[MemoryEntry],
    temporary_entries: list[MemoryEntry],
    deprecated_entries: list[DeprecatedMemoryEntry],
) -> None:
    """Apply an APPLY_DEPRECATE decision.

    Args:
        entry: The merge plan entry to apply.
        global_entries: Global entries list to modify.
        project_entries: Project entries list to modify.
        repo_entries: Repo entries list to modify.
        temporary_entries: Temporary entries list to modify.
        deprecated_entries: Deprecated entries list to modify.

    Raises:
        ValueError: If the target entry is not found.
    """
    # Find existing entry by target statement
    result = _find_entry_by_statement(
        entry.target,
        global_entries,
        project_entries,
        repo_entries,
        temporary_entries,
    )

    if result is None:
        raise ValueError(f"APPLY_DEPRECATE failed: No entry found with statement: {entry.target!r}")

    found_entry, containing_list = result

    # Remove from original section
    containing_list.remove(found_entry)

    # Add to deprecated entries
    deprecated_entry = DeprecatedMemoryEntry(
        entry=found_entry,
        deprecation_reason=entry.reason,
    )
    deprecated_entries.append(deprecated_entry)
