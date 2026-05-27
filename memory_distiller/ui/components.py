"""UI components for Streamlit MVP - pure helper functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.llm.errors import LlmError

if TYPE_CHECKING:
    pass


def estimate_tokens(text: str) -> int:
    """Estimate token count using simple heuristic.

    Args:
        text: Input text to estimate tokens for.

    Returns:
        Estimated token count (len(text) // 4).
    """
    return len(text) // 4


def render_candidate_table(candidates: list[MemoryCandidate]) -> list[dict[str, str]]:
    """Render memory candidates as table-ready list of dicts.

    Args:
        candidates: List of MemoryCandidate objects.

    Returns:
        List of dicts with keys: id, action, target, scope, type,
        priority, stability, statement, evidence, reason.
    """
    result = []
    for candidate in candidates:
        result.append(
            {
                "id": candidate.id,
                "action": candidate.action.value,
                "target": candidate.target,
                "scope": candidate.scope,
                "type": candidate.type.value,
                "priority": candidate.priority.value,
                "stability": candidate.stability.value,
                "statement": candidate.statement,
                "evidence": candidate.evidence,
                "reason": candidate.reason,
            }
        )
    return result


def render_validated_candidate_table(
    validated_candidates: list[ValidatedCandidate],
) -> list[dict[str, str]]:
    """Render validated candidates as table-ready list of dicts.

    Args:
        validated_candidates: List of ValidatedCandidate objects.

    Returns:
        List of dicts with keys: id, verdict, action, target, scope,
        type, priority, stability, statement, evidence, reason.
    """
    result = []
    for candidate in validated_candidates:
        result.append(
            {
                "id": candidate.id,
                "verdict": candidate.verdict.value,
                "action": candidate.action.value,
                "target": candidate.target,
                "scope": candidate.scope,
                "type": candidate.type.value,
                "priority": candidate.priority.value,
                "stability": candidate.stability.value,
                "statement": candidate.statement,
                "evidence": candidate.evidence,
                "reason": candidate.reason,
            }
        )
    return result


def render_memory_summary(memory_document: MemoryDocument) -> dict[str, int]:
    """Render memory document summary with counts per category.

    Args:
        memory_document: The MemoryDocument to summarize.

    Returns:
        Dict with keys: global_entries, project_entries, repo_entries,
        temporary_entries, deprecated_entries, open_questions.
    """
    return {
        "global_entries": len(memory_document.global_entries),
        "project_entries": len(memory_document.project_entries),
        "repo_entries": len(memory_document.repo_entries),
        "temporary_entries": len(memory_document.temporary_entries),
        "deprecated_entries": len(memory_document.deprecated_entries),
        "open_questions": len(memory_document.open_questions),
    }


def render_error(error: Exception) -> str:
    """Render error as human-readable string.

    Handles:
    - ParseErrorCollection: shows each error with line number
    - ValueError: shows message
    - LlmError subclasses: shows message
    - generic Exception: shows class name and message

    Args:
        error: The exception to render.

    Returns:
        Human-readable error string.
    """
    if isinstance(error, ParseErrorCollection):
        if not error.errors:
            return "Parse error: no errors recorded"
        lines = []
        for e in error.errors:
            lines.append(f"Line {e.line_number}: {e.message}")
        return "\n".join(lines)

    if isinstance(error, ValueError):
        return str(error)

    if isinstance(error, LlmError):
        return str(error)

    # Generic Exception
    return f"{type(error).__name__}: {error}"
