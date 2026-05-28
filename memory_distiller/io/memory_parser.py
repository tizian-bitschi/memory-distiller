"""Parser for memory_full.md format into MemoryDocument."""

from __future__ import annotations

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.errors import ParseError, ParseErrorCollection
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)
from memory_distiller.io.enum_aliases import (
    suggest_priority_alias,
    suggest_scope_alias,
    suggest_stability_alias,
    suggest_type_alias,
)


def validate_scope(scope: str) -> None:
    """Validate a scope string.

    Args:
        scope: The scope string to validate.

    Raises:
        ValueError: If the scope is invalid.
    """
    if not scope:
        raise ValueError("Scope cannot be empty")
    if scope in ("G", "T"):
        return
    if scope.startswith("P:") and len(scope) > 2:
        return
    if scope.startswith("R:") and len(scope) > 2:
        return
    raise ValueError(f"Invalid scope: {scope!r}")


def _parse_scope(scope: str, line_number: int, errors: list[ParseError]) -> str | None:
    """Parse and validate a scope string.

    Args:
        scope: The scope string to validate.
        line_number: Current line number for error reporting.
        errors: List to collect errors.

    Returns:
        The validated scope string or None if invalid.
    """
    try:
        validate_scope(scope)
        return scope
    except ValueError as e:
        suggestion = suggest_scope_alias(scope)
        err_msg = str(e)
        if suggestion:
            err_msg = f"{err_msg} Did you mean {suggestion!r}?"
        errors.append(ParseError(line_number, scope, err_msg))
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
        suggestion = suggest_type_alias(type_str)
        if suggestion:
            msg = (
                f"Unknown memory type {type_str!r}."
                f" Did you mean {suggestion!r}? Valid values: {valid_types}"
            )
        else:
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
        suggestion = suggest_priority_alias(prio_str)
        if suggestion:
            msg = (
                f"Unknown priority {prio_str!r}."
                f" Did you mean {suggestion!r}? Valid values: {valid_priorities}"
            )
        else:
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
        suggestion = suggest_stability_alias(stability_str)
        if suggestion:
            msg = (
                f"Unknown stability {stability_str!r}."
                f" Did you mean {suggestion!r}? Valid values: {valid_stabilities}"
            )
        else:
            msg = f"Unknown stability {stability_str!r}. Valid values: {valid_stabilities}"
        errors.append(ParseError(line_number, stability_str, msg))
        return None


def parse_memory_document(text: str) -> MemoryDocument:
    """Parse a memory_full.md format string into a MemoryDocument.

    Args:
        text: The raw markdown text to parse.

    Returns:
        A MemoryDocument containing all parsed entries.

    Raises:
        ParseErrorCollection: If any parsing errors occurred.
    """
    errors: list[ParseError] = []
    lines = text.splitlines()

    # Track current section
    current_section: str | None = None
    section_mapping = {
        "## GLOBAL": "global",
        "## PROJECTS": "projects",
        "## REPOS": "repos",
        "## TEMPORARY": "temporary",
        "## DEPRECATED": "deprecated",
        "## OFFENE_KLÄRUNGEN": "open_questions",
    }

    # Results
    global_entries: list[MemoryEntry] = []
    project_entries: list[MemoryEntry] = []
    repo_entries: list[MemoryEntry] = []
    temporary_entries: list[MemoryEntry] = []
    deprecated_entries: list[DeprecatedMemoryEntry] = []
    open_questions: list[tuple[str, str]] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Ignore empty lines
        if not stripped:
            continue

        # Ignore top-level heading
        if stripped == "# MEMORY_FULL":
            continue

        # Ignore header lines
        if stripped in (
            "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE",
            "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON",
            "QUESTION|WHY_IT_MATTERS",
        ):
            continue

        # Check if it's a section heading
        if stripped in section_mapping:
            current_section = section_mapping[stripped]
            continue

        # Parse based on current section
        if current_section is None:
            # Before any section, skip lines
            continue

        if current_section == "global":
            entry, errs = _parse_normal_entry(stripped, line_num)
            errors.extend(errs)
            if entry:
                global_entries.append(entry)

        elif current_section == "projects":
            entry, errs = _parse_normal_entry(stripped, line_num)
            errors.extend(errs)
            if entry:
                project_entries.append(entry)

        elif current_section == "repos":
            entry, errs = _parse_normal_entry(stripped, line_num)
            errors.extend(errs)
            if entry:
                repo_entries.append(entry)

        elif current_section == "temporary":
            entry, errs = _parse_normal_entry(stripped, line_num)
            errors.extend(errs)
            if entry:
                temporary_entries.append(entry)

        elif current_section == "deprecated":
            deprecated_entry, errs = _parse_deprecated_entry(stripped, line_num)
            errors.extend(errs)
            if deprecated_entry:
                deprecated_entries.append(deprecated_entry)

        elif current_section == "open_questions":
            question, why, errs = _parse_open_question(stripped, line_num)
            errors.extend(errs)
            if question is not None and why is not None:
                open_questions.append((question, why))

    if errors:
        raise ParseErrorCollection(errors)

    return MemoryDocument(
        global_entries=global_entries,
        project_entries=project_entries,
        repo_entries=repo_entries,
        temporary_entries=temporary_entries,
        deprecated_entries=deprecated_entries,
        open_questions=open_questions,
    )


def _parse_normal_entry(line: str, line_num: int) -> tuple[MemoryEntry | None, list[ParseError]]:
    """Parse a normal memory entry line (6 columns).

    Args:
        line: The line to parse.
        line_num: The line number for error reporting.

    Returns:
        Tuple of (MemoryEntry or None, list of errors).
    """
    errors: list[ParseError] = []
    parts = [p.strip() for p in line.split("|")]

    if len(parts) != 6:
        errors.append(
            ParseError(
                line_num,
                line,
                f"Expected 6 columns for normal entry, got {len(parts)}",
            )
        )
        return None, errors

    scope = _parse_scope(parts[0], line_num, errors)
    mem_type = _parse_memory_type(parts[1], line_num, errors)
    priority = _parse_priority(parts[2], line_num, errors)
    stability = _parse_stability(parts[3], line_num, errors)

    if len(errors) > 0:
        return None, errors

    entry = MemoryEntry(
        scope=scope,  # type: ignore
        type=mem_type,  # type: ignore
        priority=priority,  # type: ignore
        stability=stability,  # type: ignore
        statement=parts[4],
        evidence=parts[5],
    )
    return entry, errors


def _parse_deprecated_entry(
    line: str, line_num: int
) -> tuple[DeprecatedMemoryEntry | None, list[ParseError]]:
    """Parse a deprecated memory entry line (7 columns).

    Args:
        line: The line to parse.
        line_num: The line number for error reporting.

    Returns:
        Tuple of (DeprecatedMemoryEntry or None, list of errors).
    """
    errors: list[ParseError] = []
    parts = [p.strip() for p in line.split("|")]

    if len(parts) != 7:
        errors.append(
            ParseError(
                line_num,
                line,
                f"Expected 7 columns for deprecated entry, got {len(parts)}",
            )
        )
        return None, errors

    # First 6 columns form the original entry
    scope = _parse_scope(parts[0], line_num, errors)
    mem_type = _parse_memory_type(parts[1], line_num, errors)
    priority = _parse_priority(parts[2], line_num, errors)
    stability = _parse_stability(parts[3], line_num, errors)

    if len(errors) > 0:
        return None, errors

    original_entry = MemoryEntry(
        scope=scope,  # type: ignore
        type=mem_type,  # type: ignore
        priority=priority,  # type: ignore
        stability=stability,  # type: ignore
        statement=parts[4],
        evidence=parts[5],
    )

    deprecated_entry = DeprecatedMemoryEntry(
        entry=original_entry,
        deprecation_reason=parts[6],
    )
    return deprecated_entry, errors


def _parse_open_question(
    line: str, line_num: int
) -> tuple[str | None, str | None, list[ParseError]]:
    """Parse an open question line (2 columns).

    Args:
        line: The line to parse.
        line_num: The line number for error reporting.

    Returns:
        Tuple of (question, why_it_matters, list of errors).
    """
    errors: list[ParseError] = []
    parts = [p.strip() for p in line.split("|")]

    if len(parts) != 2:
        errors.append(
            ParseError(
                line_num,
                line,
                f"Expected 2 columns for open question, got {len(parts)}",
            )
        )
        return None, None, errors

    return parts[0], parts[1], errors
