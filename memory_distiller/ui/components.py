"""UI components for Streamlit MVP - pure helper functions."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import TYPE_CHECKING

import streamlit as st

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.llm.errors import LlmError
from memory_distiller.llm.models import LlmCostEstimate, LlmUsage

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


def format_token_count(value: int | None) -> str:
    """Format token count for display.

    Args:
        value: Token count or None.

    Returns:
        Formatted string.
    """
    if value is None:
        return "—"
    return f"{value:,}"


def format_cost(value: Decimal | None) -> str:
    """Format cost for display.

    Args:
        value: Cost in USD or None.

    Returns:
        Formatted string with $.
    """
    if value is None:
        return "—"
    return f"${value:.8f}"


def render_usage_summary(
    label: str,
    usage: LlmUsage | None,
    cost: LlmCostEstimate | None,
    model: str | None,
) -> None:
    """Render usage summary in a Streamlit expander.

    Args:
        label: Label for the expander.
        usage: Token usage metadata.
        cost: Cost estimate.
        model: Model name.
    """
    if usage is None and cost is None and model is None:
        return

    with st.expander(f"📊 {label} Usage & Cost"):
        if model:
            st.write(f"**Model:** {model}")

        cols = st.columns(3)
        with cols[0]:
            st.metric("Prompt tokens", format_token_count(usage.prompt_tokens if usage else None))
        with cols[1]:
            st.metric(
                "Cache hit",
                format_token_count(usage.prompt_cache_hit_tokens if usage else None),
            )
        with cols[2]:
            st.metric(
                "Cache miss",
                format_token_count(usage.prompt_cache_miss_tokens if usage else None),
            )

        cols2 = st.columns(3)
        with cols2[0]:
            st.metric(
                "Completion",
                format_token_count(usage.completion_tokens if usage else None),
            )
        with cols2[1]:
            reasoning = None
            if usage and usage.reasoning_tokens is not None:
                reasoning = usage.reasoning_tokens
            st.metric("Reasoning", format_token_count(reasoning))
        with cols2[2]:
            st.metric("Total", format_token_count(usage.total_tokens if usage else None))

        if cost and cost.total_cost is not None:
            st.write(f"**Estimated cost:** {format_cost(cost.total_cost)}")
        if cost and cost.note:
            st.caption(cost.note)


def aggregate_usage(usages: Sequence[LlmUsage]) -> LlmUsage:
    """Aggregate multiple LlmUsage objects.

    Args:
        usages: List of usage objects.

    Returns:
        Aggregated LlmUsage.
    """
    total_prompt = 0
    total_hit = 0
    total_miss = 0
    total_completion = 0
    total_reasoning = 0
    total_tokens = 0

    for u in usages:
        if u.prompt_tokens is not None:
            total_prompt += u.prompt_tokens
        if u.prompt_cache_hit_tokens is not None:
            total_hit += u.prompt_cache_hit_tokens
        if u.prompt_cache_miss_tokens is not None:
            total_miss += u.prompt_cache_miss_tokens
        if u.completion_tokens is not None:
            total_completion += u.completion_tokens
        if u.reasoning_tokens is not None:
            total_reasoning += u.reasoning_tokens
        if u.total_tokens is not None:
            total_tokens += u.total_tokens

    return LlmUsage(
        prompt_tokens=total_prompt if total_prompt > 0 else None,
        prompt_cache_hit_tokens=total_hit if total_hit > 0 else None,
        prompt_cache_miss_tokens=total_miss if total_miss > 0 else None,
        completion_tokens=total_completion if total_completion > 0 else None,
        reasoning_tokens=total_reasoning if total_reasoning > 0 else None,
        total_tokens=total_tokens if total_tokens > 0 else None,
    )


def aggregate_cost(costs: Sequence[LlmCostEstimate | None]) -> Decimal | None:
    """Aggregate total cost from multiple estimates.

    Args:
        costs: List of cost estimates (may contain None).

    Returns:
        Total cost Decimal or None.
    """
    total: Decimal | None = None
    for cost in costs:
        if cost is not None and cost.total_cost is not None:
            if total is None:
                total = cost.total_cost
            else:
                total = total + cost.total_cost
    return total
