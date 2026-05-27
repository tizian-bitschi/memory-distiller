"""Parser for candidate and validated candidate lines."""

from __future__ import annotations

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)
from memory_distiller.domain.errors import ParseError, ParseErrorCollection


def _validate_scope(scope: str) -> None:
    """Validate scope string format."""
    if not scope:
        raise ValueError("Scope cannot be empty")
    if scope in ("G", "T"):
        return
    if scope.startswith("P:") and len(scope) > 2:
        return
    if scope.startswith("R:") and len(scope) > 2:
        return
    raise ValueError(f"Invalid scope: {scope!r}")


def parse_candidates(text: str) -> list[MemoryCandidate]:
    """Parse candidate lines into MemoryCandidate objects.

    Args:
        text: Multi-line text containing candidate lines.

    Returns:
        List of MemoryCandidate objects.

    Raises:
        ParseErrorCollection: If any parsing errors occur.
    """
    lines = text.splitlines()
    errors: list[ParseError] = []
    candidates: list[MemoryCandidate] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("ID|ACTION|TARGET"):
            continue

        parts = stripped.split("|")
        if len(parts) != 10:
            errors.append(ParseError(line_num, line, f"Expected 10 columns, got {len(parts)}"))
            continue

        id, action, target, scope, type_str, prio, stability, statement, evidence, reason = parts
        id = id.strip()
        action = action.strip()
        target = target.strip()
        scope = scope.strip()
        type_str = type_str.strip()
        prio = prio.strip()
        stability = stability.strip()
        statement = statement.strip()
        evidence = evidence.strip()
        reason = reason.strip()

        try:
            action_enum = CandidateAction(action)
        except ValueError:
            valid_actions = ", ".join(a.value for a in CandidateAction)
            errors.append(
                ParseError(line_num, line, f"Invalid action: {action!r}. Valid: {valid_actions}")
            )
            continue

        try:
            type_enum = MemoryType(type_str)
        except ValueError:
            valid_types = ", ".join(t.value for t in MemoryType)
            errors.append(
                ParseError(line_num, line, f"Invalid type: {type_str!r}. Valid: {valid_types}")
            )
            continue

        try:
            priority_enum = Priority(prio)
        except ValueError:
            valid_priorities = ", ".join(p.value for p in Priority)
            errors.append(
                ParseError(line_num, line, f"Invalid priority: {prio!r}. Valid: {valid_priorities}")
            )
            continue

        try:
            stability_enum = Stability(stability)
        except ValueError:
            valid_stabilities = ", ".join(s.value for s in Stability)
            errors.append(
                ParseError(
                    line_num, line, f"Invalid stability: {stability!r}. Valid: {valid_stabilities}"
                )
            )
            continue

        try:
            _validate_scope(scope)
        except ValueError as e:
            errors.append(ParseError(line_num, line, str(e)))
            continue

        candidates.append(
            MemoryCandidate(
                id=id,
                action=action_enum,
                target=target,
                scope=scope,
                type=type_enum,
                priority=priority_enum,
                stability=stability_enum,
                statement=statement,
                evidence=evidence,
                reason=reason,
            )
        )

    if errors:
        raise ParseErrorCollection(errors)

    return candidates


def parse_validated_candidates(text: str) -> list[ValidatedCandidate]:
    """Parse validated candidate lines into ValidatedCandidate objects.

    Args:
        text: Multi-line text containing validated candidate lines.

    Returns:
        List of ValidatedCandidate objects.

    Raises:
        ParseErrorCollection: If any parsing errors occur.
    """
    lines = text.splitlines()
    errors: list[ParseError] = []
    candidates: list[ValidatedCandidate] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("ID|VERDICT|ACTION"):
            continue

        parts = stripped.split("|")
        if len(parts) != 11:
            errors.append(ParseError(line_num, line, f"Expected 11 columns, got {len(parts)}"))
            continue

        (
            id,
            verdict,
            action,
            target,
            scope,
            type_str,
            prio,
            stability,
            statement,
            evidence,
            reason,
        ) = parts
        id = id.strip()
        verdict = verdict.strip()
        action = action.strip()
        target = target.strip()
        scope = scope.strip()
        type_str = type_str.strip()
        prio = prio.strip()
        stability = stability.strip()
        statement = statement.strip()
        evidence = evidence.strip()
        reason = reason.strip()

        try:
            verdict_enum = ValidationVerdict(verdict)
        except ValueError:
            valid_verdicts = ", ".join(v.value for v in ValidationVerdict)
            errors.append(
                ParseError(line_num, line, f"Invalid verdict: {verdict!r}. Valid: {valid_verdicts}")
            )
            continue

        try:
            action_enum = CandidateAction(action)
        except ValueError:
            valid_actions = ", ".join(a.value for a in CandidateAction)
            errors.append(
                ParseError(line_num, line, f"Invalid action: {action!r}. Valid: {valid_actions}")
            )
            continue

        try:
            type_enum = MemoryType(type_str)
        except ValueError:
            valid_types = ", ".join(t.value for t in MemoryType)
            errors.append(
                ParseError(line_num, line, f"Invalid type: {type_str!r}. Valid: {valid_types}")
            )
            continue

        try:
            priority_enum = Priority(prio)
        except ValueError:
            valid_priorities = ", ".join(p.value for p in Priority)
            errors.append(
                ParseError(line_num, line, f"Invalid priority: {prio!r}. Valid: {valid_priorities}")
            )
            continue

        try:
            stability_enum = Stability(stability)
        except ValueError:
            valid_stabilities = ", ".join(s.value for s in Stability)
            errors.append(
                ParseError(
                    line_num, line, f"Invalid stability: {stability!r}. Valid: {valid_stabilities}"
                )
            )
            continue

        try:
            _validate_scope(scope)
        except ValueError as e:
            errors.append(ParseError(line_num, line, str(e)))
            continue

        candidates.append(
            ValidatedCandidate(
                id=id,
                verdict=verdict_enum,
                action=action_enum,
                target=target,
                scope=scope,
                type=type_enum,
                priority=priority_enum,
                stability=stability_enum,
                statement=statement,
                evidence=evidence,
                reason=reason,
            )
        )

    if errors:
        raise ParseErrorCollection(errors)

    return candidates
