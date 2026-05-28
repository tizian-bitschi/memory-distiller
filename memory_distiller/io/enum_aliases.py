"""Alias maps and suggestion helpers for enum values."""

from __future__ import annotations

# Type aliases (case-insensitive)
TYPE_ALIASES: dict[str, str] = {
    "PREFERENCE": "PREF",
    "PREFERENCES": "PREF",
    "PREFS": "PREF",
}

# Priority aliases (case-insensitive)
PRIORITY_ALIASES: dict[str, str] = {
    "HIGH": "H",
    "MEDIUM": "M",
    "LOW": "L",
}

# Stability aliases (case-insensitive)
STABILITY_ALIASES: dict[str, str] = {
    "STABLE": "D",
    "DURABLE": "D",
    "LONG_TERM": "D",
    "PERMANENT": "D",
    "MEDIUM_TERM": "M",
    "TEMPORARY": "T",
    "TEMP": "T",
}


def suggest_type_alias(type_str: str) -> str | None:
    """Suggest canonical type for an alias.

    Args:
        type_str: The type string to look up.

    Returns:
        The canonical type if found, None otherwise.
    """
    return TYPE_ALIASES.get(type_str.upper())


def suggest_priority_alias(prio_str: str) -> str | None:
    """Suggest canonical priority for an alias.

    Args:
        prio_str: The priority string to look up.

    Returns:
        The canonical priority if found, None otherwise.
    """
    return PRIORITY_ALIASES.get(prio_str.upper())


def suggest_stability_alias(stability_str: str) -> str | None:
    """Suggest canonical stability for an alias.

    Args:
        stability_str: The stability string to look up.

    Returns:
        The canonical stability if found, None otherwise.
    """
    return STABILITY_ALIASES.get(stability_str.upper())


def suggest_scope_alias(scope: str) -> str | None:
    """Suggest canonical scope for an alias.

    Handles GLOBAL->G, TEMPORARY->T, TEMP->T and dynamic PROJECT/REPO/REPOSITORY.

    Args:
        scope: The scope string to look up.

    Returns:
        The canonical scope if found, None otherwise.
    """
    upper = scope.upper()
    if upper == "GLOBAL":
        return "G"
    if upper in ("TEMPORARY", "TEMP"):
        return "T"
    if upper.startswith("PROJECT:"):
        return "P:" + scope[8:]
    if upper.startswith("REPO:"):
        return "R:" + scope[5:]
    if upper.startswith("REPOSITORY:"):
        return "R:" + scope[11:]
    return None


def normalize_candidate_lines(raw: str) -> tuple[str, list[str]]:
    """Normalize candidate/validated candidate lines by replacing aliases.

    Free-text fields (statement, evidence, reason) are not modified.

    Args:
        raw: The raw candidate text.

    Returns:
        Tuple of (normalized_text, changes_list).
    """
    lines = raw.splitlines()
    changes: list[str] = []
    result_lines: list[str] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            result_lines.append(line)
            continue
        if stripped.startswith("ID|ACTION|TARGET") or stripped.startswith("ID|VERDICT|ACTION"):
            result_lines.append(line)
            continue

        parts = stripped.split("|")
        is_validated = len(parts) == 11
        is_candidate = len(parts) == 10

        if is_validated:
            # col 0=id, 1=verdict, 2=action, 3=target, 4=scope, 5=type, 6=priority, 7=stability
            id_val, verdict, action, target, scope, type_str, prio, stability = (
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
                parts[5],
                parts[6],
                parts[7],
            )
            other_parts = parts[8:]
        elif is_candidate:
            # col 0=id, 1=action, 2=target, 3=scope, 4=type, 5=priority, 6=stability
            id_val, action, target, scope, type_str, prio, stability = (
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
                parts[5],
                parts[6],
            )
            other_parts = parts[7:]
            verdict = ""
        else:
            result_lines.append(line)
            continue

        original_scope = scope
        original_type = type_str
        original_prio = prio
        original_stability = stability

        # Normalize scope
        suggested_scope = suggest_scope_alias(scope)
        if suggested_scope and suggested_scope != scope:
            scope = suggested_scope
            changes.append(f"Line {line_num}: SCOPE {original_scope} -> {scope}")

        # Normalize type
        suggested_type = suggest_type_alias(type_str)
        if suggested_type and suggested_type != type_str:
            type_str = suggested_type
            changes.append(f"Line {line_num}: TYPE {original_type} -> {type_str}")

        # Normalize priority
        suggested_prio = suggest_priority_alias(prio)
        if suggested_prio and suggested_prio != prio:
            prio = suggested_prio
            changes.append(f"Line {line_num}: PRIORITY {original_prio} -> {prio}")

        # Normalize stability
        suggested_stability = suggest_stability_alias(stability)
        if suggested_stability and suggested_stability != stability:
            stability = suggested_stability
            changes.append(f"Line {line_num}: STABILITY {original_stability} -> {stability}")

        # Rebuild line
        if is_validated:
            new_line = "|".join(
                [id_val, verdict, action, target, scope, type_str, prio, stability] + other_parts
            )
        else:
            new_line = "|".join(
                [id_val, action, target, scope, type_str, prio, stability] + other_parts
            )

        result_lines.append(new_line)

    return "\n".join(result_lines), changes


def normalize_memory_document(raw: str) -> tuple[str, list[str]]:
    """Normalize memory_full document by replacing aliases.

    Free-text fields (statement, evidence, deprecation_reason) are not modified.

    Args:
        raw: The raw memory document text.

    Returns:
        Tuple of (normalized_text, changes_list).
    """
    lines = raw.splitlines()
    changes: list[str] = []
    result_lines: list[str] = []
    current_section: str | None = None
    section_mapping = {
        "## GLOBAL": "global",
        "## PROJECTS": "projects",
        "## REPOS": "repos",
        "## TEMPORARY": "temporary",
        "## DEPRECATED": "deprecated",
        "## OFFENE_KLÄRUNGEN": "open_questions",
    }
    data_sections = {"global", "projects", "repos", "temporary", "deprecated"}

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            result_lines.append(line)
            continue
        if stripped == "# MEMORY_FULL":
            result_lines.append(line)
            continue
        if stripped in (
            "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE",
            "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON",
            "QUESTION|WHY_IT_MATTERS",
        ):
            result_lines.append(line)
            continue
        if stripped in section_mapping:
            current_section = section_mapping[stripped]
            result_lines.append(line)
            continue

        if current_section is None or current_section not in data_sections:
            result_lines.append(line)
            continue

        parts = stripped.split("|")
        is_deprecated = len(parts) == 7
        is_normal = len(parts) == 6

        if not is_normal and not is_deprecated:
            result_lines.append(line)
            continue

        # col 0=scope, 1=type, 2=priority, 3=stability, 4=statement, 5=evidence
        scope, type_str, prio, stability = parts[0], parts[1], parts[2], parts[3]
        original_scope = scope
        original_type = type_str
        original_prio = prio
        original_stability = stability

        # Normalize scope
        suggested_scope = suggest_scope_alias(scope)
        if suggested_scope and suggested_scope != scope:
            scope = suggested_scope
            changes.append(f"Line {line_num}: SCOPE {original_scope} -> {scope}")

        # Normalize type
        suggested_type = suggest_type_alias(type_str)
        if suggested_type and suggested_type != type_str:
            type_str = suggested_type
            changes.append(f"Line {line_num}: TYPE {original_type} -> {type_str}")

        # Normalize priority
        suggested_prio = suggest_priority_alias(prio)
        if suggested_prio and suggested_prio != prio:
            prio = suggested_prio
            changes.append(f"Line {line_num}: PRIORITY {original_prio} -> {prio}")

        # Normalize stability
        suggested_stability = suggest_stability_alias(stability)
        if suggested_stability and suggested_stability != stability:
            stability = suggested_stability
            changes.append(f"Line {line_num}: STABILITY {original_stability} -> {stability}")

        # Rebuild line
        if is_deprecated:
            new_line = "|".join([scope, type_str, prio, stability, parts[4], parts[5], parts[6]])
        else:
            new_line = "|".join([scope, type_str, prio, stability, parts[4], parts[5]])

        result_lines.append(new_line)

    return "\n".join(result_lines), changes
