"""Parser for merge plan format into MergePlan."""

from __future__ import annotations

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.errors import ParseError, ParseErrorCollection
from memory_distiller.domain.merge_plan import MergeDecision, MergePlan, MergePlanEntry
from memory_distiller.io.memory_parser import validate_scope

# Placeholder texts that must not be silently accepted
_PLACEHOLDER_TEXTS = frozenset(
    [
        "no entries",
        "none",
        "keine einträge",
        "n/a",
        "—",
        "-",
        ".",
        "",
    ]
)


def _is_placeholder(value: str) -> bool:
    """Check if a value is a placeholder text that should not be accepted."""
    return value.strip().lower() in _PLACEHOLDER_TEXTS


def _parse_merge_decision(
    decision_str: str, line_number: int, errors: list[ParseError]
) -> MergeDecision | None:
    """Parse and validate a MergeDecision enum value.

    Args:
        decision_str: The decision string to parse.
        line_number: Current line number for error reporting.
        errors: List to collect errors.

    Returns:
        The parsed MergeDecision or None if invalid.
    """
    try:
        return MergeDecision(decision_str)
    except ValueError:
        valid_decisions = [d.value for d in MergeDecision]
        msg = f"Unknown merge decision {decision_str!r}. Valid values: {valid_decisions}"
        errors.append(ParseError(line_number, decision_str, msg))
        return None


def _parse_memory_type(
    type_str: str, line_number: int, errors: list[ParseError]
) -> MemoryType | None:
    """Parse and validate a MemoryType enum value.

    Args:
        type_str: The type string to parse.
        line_number: Current line number for error reporting.
        errors: List to collect errors.

    Returns:
        The parsed MemoryType or None if invalid.
    """
    try:
        return MemoryType(type_str)
    except ValueError:
        valid_types = [t.value for t in MemoryType]
        msg = f"Unknown memory type {type_str!r}. Valid values: {valid_types}"
        errors.append(ParseError(line_number, type_str, msg))
        return None


def _parse_priority(prio_str: str, line_number: int, errors: list[ParseError]) -> Priority | None:
    """Parse and validate a Priority enum value.

    Args:
        prio_str: The priority string to parse.
        line_number: Current line number for error reporting.
        errors: List to collect errors.

    Returns:
        The parsed Priority or None if invalid.
    """
    try:
        return Priority(prio_str)
    except ValueError:
        valid_priorities = [p.value for p in Priority]
        msg = f"Unknown priority {prio_str!r}. Valid values: {valid_priorities}"
        errors.append(ParseError(line_number, prio_str, msg))
        return None


def _parse_stability(
    stability_str: str, line_number: int, errors: list[ParseError]
) -> Stability | None:
    """Parse and validate a Stability enum value.

    Args:
        stability_str: The stability string to parse.
        line_number: Current line number for error reporting.
        errors: List to collect errors.

    Returns:
        The parsed Stability or None if invalid.
    """
    try:
        return Stability(stability_str)
    except ValueError:
        valid_stabilities = [s.value for s in Stability]
        msg = f"Unknown stability {stability_str!r}. Valid values: {valid_stabilities}"
        errors.append(ParseError(line_number, stability_str, msg))
        return None


def _validate_entry(entry: MergePlanEntry, line_number: int, errors: list[ParseError]) -> None:
    """Validate a merge plan entry based on decision-specific rules.

    Args:
        entry: The merge plan entry to validate.
        line_number: Current line number for error reporting.
        errors: List to collect errors.
    """
    decision = entry.decision

    if decision == MergeDecision.APPLY_ADD:
        if _is_placeholder(entry.statement):
            errors.append(
                ParseError(
                    line_number,
                    entry.statement,
                    "APPLY_ADD requires non-empty statement",
                )
            )

    elif decision == MergeDecision.APPLY_UPDATE:
        if _is_placeholder(entry.target) or entry.target == "-":
            errors.append(
                ParseError(
                    line_number,
                    entry.target,
                    "APPLY_UPDATE requires non-empty, non-placeholder target",
                )
            )

    elif decision == MergeDecision.APPLY_DEPRECATE:
        if _is_placeholder(entry.target) or entry.target == "-":
            errors.append(
                ParseError(
                    line_number,
                    entry.target,
                    "APPLY_DEPRECATE requires non-empty, non-placeholder target",
                )
            )
        if _is_placeholder(entry.reason):
            errors.append(
                ParseError(
                    line_number,
                    entry.reason,
                    "APPLY_DEPRECATE requires non-empty reason",
                )
            )

    elif decision == MergeDecision.ADD_OPEN_QUESTION:
        if _is_placeholder(entry.statement):
            errors.append(
                ParseError(
                    line_number,
                    entry.statement,
                    "ADD_OPEN_QUESTION requires non-empty statement",
                )
            )

    # SKIP_DROP: no extra validation needed


def parse_merge_plan(text: str) -> MergePlan:
    """Parse a merge plan text into a MergePlan object.

    Args:
        text: The raw merge plan text to parse.

    Returns:
        A MergePlan containing all parsed entries.

    Raises:
        ParseErrorCollection: If any parsing errors occurred.
    """
    errors: list[ParseError] = []
    lines = text.splitlines()

    entries: list[MergePlanEntry] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Ignore empty lines
        if not stripped:
            continue

        parts = [p.strip() for p in stripped.split("|")]

        if len(parts) != 10:
            errors.append(
                ParseError(
                    line_num,
                    line,
                    f"Expected exactly 10 columns, got {len(parts)}",
                )
            )
            continue

        candidate_id = parts[0]
        decision_str = parts[1]
        target = parts[2]
        scope = parts[3]
        type_str = parts[4]
        priority_str = parts[5]
        stability_str = parts[6]
        statement = parts[7]
        evidence = parts[8]
        reason = parts[9]

        # Parse decision
        decision = _parse_merge_decision(decision_str, line_num, errors)
        if decision is None:
            continue

        # Parse scope
        try:
            validate_scope(scope)
        except ValueError:
            errors.append(ParseError(line_num, scope, f"Invalid scope: {scope!r}"))

        # Parse type
        mem_type = _parse_memory_type(type_str, line_num, errors)

        # Parse priority
        priority = _parse_priority(priority_str, line_num, errors)

        # Parse stability
        stability = _parse_stability(stability_str, line_num, errors)

        # Skip if any enum parsing failed
        if mem_type is None or priority is None or stability is None:
            continue

        entry = MergePlanEntry(
            candidate_id=candidate_id,
            decision=decision,
            target=target,
            scope=scope,
            type=type_str,
            priority=priority_str,
            stability=stability_str,
            statement=statement,
            evidence=evidence,
            reason=reason,
        )

        # Decision-specific validation
        _validate_entry(entry, line_num, errors)

        entries.append(entry)

    if errors:
        raise ParseErrorCollection(errors)

    return MergePlan(entries=tuple(entries))
