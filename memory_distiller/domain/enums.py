"""Domain enums for Memory Distiller."""

from enum import Enum


class MemoryType(Enum):
    """Types of memory entries in the distillation system."""

    RULE = "RULE"
    PREF = "PREF"
    FACT = "FACT"
    DECISION = "DECISION"
    AVOID = "AVOID"
    STYLE = "STYLE"
    SOURCE = "SOURCE"
    TERM = "TERM"
    TASK = "TASK"
    CONFLICT = "CONFLICT"


class Priority(Enum):
    """Priority levels for memory entries."""

    H = "H"
    M = "M"
    L = "L"


class Stability(Enum):
    """Stability levels indicating how fixed a memory is."""

    D = "D"
    M = "M"
    T = "T"


class CandidateAction(Enum):
    """Actions that can be taken on candidate memories."""

    ADD = "ADD"
    UPDATE = "UPDATE"
    DEPRECATE = "DEPRECATE"
    IGNORE = "IGNORE"
    CONFLICT = "CONFLICT"
    ASK = "ASK"


class ValidationVerdict(Enum):
    """Verdicts from validation of memory entries."""

    KEEP = "KEEP"
    EDIT = "EDIT"
    DROP = "DROP"
    ASK = "ASK"
    CONFLICT = "CONFLICT"
