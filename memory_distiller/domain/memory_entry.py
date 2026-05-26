"""Domain models for memory entries."""

from __future__ import annotations

from dataclasses import dataclass, field

from memory_distiller.domain.enums import MemoryType, Priority, Stability


@dataclass(frozen=True)
class MemoryEntry:
    """A single memory entry representing a unit of distilled knowledge.

    Attributes:
        scope: Logical grouping - 'G' for global, 'P:<project>' for project,
              'R:<repo>' for repository, 'T' for temporary.
        type: Category of memory entry (RULE, PREF, FACT, DECISION, etc.).
        priority: Relevance priority (H, M, L).
        stability: How fixed the memory is (D, M, T).
        statement: The distilled knowledge or rule itself.
        evidence: Source or justification for this memory entry.

    Example:
        >>> entry = MemoryEntry(
        ...     scope='G',
        ...     type=MemoryType.RULE,
        ...     priority=Priority.H,
        ...     stability=Stability.D,
        ...     statement='User prefers critical feedback over blind agreement.',
        ...     evidence='2026-05-26 Chat'
        ... )
    """

    scope: str
    type: MemoryType
    priority: Priority
    stability: Stability
    statement: str
    evidence: str


@dataclass(frozen=True)
class DeprecatedMemoryEntry:
    """A memory entry that has been deprecated.

    Wraps a MemoryEntry that is no longer valid, along with a reason
    for its deprecation.

    Attributes:
        entry: The original memory entry that is now deprecated.
        deprecation_reason: Human-readable explanation of why this entry
            was deprecated and what should be used instead (if applicable).
    """

    entry: MemoryEntry
    deprecation_reason: str


@dataclass
class MemoryDocument:
    """Container for all memory entries organized by scope and state.

    This is the root aggregate for the memory domain. It holds the complete
    set of memory entries categorized by their scope (global, project, repo,
    temporary) and state (active, deprecated). It also tracks open questions
    that need clarification.

    Attributes:
        global_entries: Memory entries applying across all projects.
        project_entries: Project-specific memory entries (scope prefixed 'P:').
        repo_entries: Repository or codebase-specific entries (scope prefixed 'R:').
        temporary_entries: Ephemeral entries not meant for long-term storage.
        deprecated_entries: Entries that are no longer valid but kept for history.
        open_questions: Pairs of (question, why_it_matters) for items needing clarification.
    """

    global_entries: list[MemoryEntry] = field(default_factory=list)
    project_entries: list[MemoryEntry] = field(default_factory=list)
    repo_entries: list[MemoryEntry] = field(default_factory=list)
    temporary_entries: list[MemoryEntry] = field(default_factory=list)
    deprecated_entries: list[DeprecatedMemoryEntry] = field(default_factory=list)
    open_questions: list[tuple[str, str]] = field(
        default_factory=list,
        metadata={
            "description": "List of (question, why_it_matters) tuples "
            "representing open items needing clarification"
        },
    )
