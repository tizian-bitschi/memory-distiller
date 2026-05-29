"""Domain models for merge plan."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MergeDecision(Enum):
    """Merge decisions for applying a merge plan."""

    APPLY_ADD = "APPLY_ADD"
    APPLY_UPDATE = "APPLY_UPDATE"
    APPLY_DEPRECATE = "APPLY_DEPRECATE"
    SKIP_DROP = "SKIP_DROP"
    ADD_OPEN_QUESTION = "ADD_OPEN_QUESTION"


@dataclass(frozen=True)
class MergePlanEntry:
    """A single entry in a merge plan.

    Attributes:
        candidate_id: Identifier for the candidate being acted upon.
        decision: The merge decision to apply.
        target: For UPDATE/DEPRECATE, the statement to find; empty otherwise.
        scope: Logical grouping - 'G' for global, 'P:<project>' for project,
              'R:<repo>' for repository, 'T' for temporary.
        type: Category of memory entry (RULE, PREF, FACT, DECISION, etc.).
        priority: Relevance priority (H, M, L).
        stability: How fixed the memory is (D, M, T).
        statement: The distilled knowledge or rule itself.
        evidence: Source or justification for this memory entry.
        reason: For DEPRECATE/OPEN_QUESTION, the reason/question.
    """

    candidate_id: str
    decision: MergeDecision
    target: str
    scope: str
    type: str
    priority: str
    stability: str
    statement: str
    evidence: str
    reason: str


@dataclass(frozen=True)
class MergePlan:
    """A collection of merge plan entries to apply to existing memory.

    Attributes:
        entries: Tuple of merge plan entries to apply in order.
    """

    entries: tuple[MergePlanEntry, ...]
