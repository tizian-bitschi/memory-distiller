"""Domain package for Memory Distiller."""

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)
from memory_distiller.domain.errors import ParseError, ParseErrorCollection
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)
from memory_distiller.domain.merge_plan import MergeDecision, MergePlan, MergePlanEntry

__all__ = [
    "CandidateAction",
    "DeprecatedMemoryEntry",
    "MemoryCandidate",
    "MemoryDocument",
    "MemoryEntry",
    "MergeDecision",
    "MergePlan",
    "MergePlanEntry",
    "MemoryType",
    "ParseError",
    "ParseErrorCollection",
    "Priority",
    "Stability",
    "ValidatedCandidate",
    "ValidationVerdict",
]
