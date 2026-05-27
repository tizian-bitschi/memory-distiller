"""Candidate domain models for Memory Distiller."""

from dataclasses import dataclass

from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)


@dataclass(frozen=True)
class MemoryCandidate:
    """A candidate memory extracted from a chat transcript.

    Attributes:
        id: Unique identifier for the candidate.
        action: The proposed action for this candidate.
        target: The target of the action (e.g., rule name, preference).
        scope: The scope of applicability (e.g., "global", "project-name").
        type: The type of memory entry.
        priority: The priority level of the candidate.
        stability: The stability level of the candidate.
        statement: The memory statement itself.
        evidence: Supporting evidence from the source.
        reason: Reasoning behind the candidate creation.
    """

    id: str
    action: CandidateAction
    target: str
    scope: str
    type: MemoryType
    priority: Priority
    stability: Stability
    statement: str
    evidence: str
    reason: str


@dataclass(frozen=True)
class ValidatedCandidate:
    """A memory candidate that has been validated.

    Attributes:
        id: Unique identifier (carried from original candidate).
        verdict: The validation verdict.
        action: The proposed action (may be modified during validation).
        target: The target of the action.
        scope: The scope of applicability.
        type: The type of memory entry.
        priority: The priority level.
        stability: The stability level.
        statement: The memory statement.
        evidence: Supporting evidence from the source.
        reason: Reasoning behind the candidate.
    """

    id: str
    verdict: ValidationVerdict
    action: CandidateAction
    target: str
    scope: str
    type: MemoryType
    priority: Priority
    stability: Stability
    statement: str
    evidence: str
    reason: str
