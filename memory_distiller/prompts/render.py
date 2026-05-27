"""Render functions for prompt templates."""

from memory_distiller.prompts.templates import (
    COMPRESSOR_V1,
    EXTRACTOR_V1,
    MERGER_V1,
    VALIDATOR_V1,
)


def render_extractor_prompt(existing_memory: str, chat_log: str) -> str:
    """Render extractor prompt."""
    if chat_log is None:
        raise ValueError("chat_log is required")
    return EXTRACTOR_V1.format(
        existing_memory=existing_memory,
        chat_log=chat_log,
    )


def render_validator_prompt(existing_memory: str, chat_log: str, candidates: str) -> str:
    """Render validator prompt."""
    if chat_log is None:
        raise ValueError("chat_log is required")
    if candidates is None:
        raise ValueError("candidates is required")
    return VALIDATOR_V1.format(
        existing_memory=existing_memory,
        chat_log=chat_log,
        candidates=candidates,
    )


def render_merger_prompt(existing_memory: str, validated_candidates: str) -> str:
    """Render merger prompt."""
    if validated_candidates is None:
        raise ValueError("validated_candidates is required")
    return MERGER_V1.format(
        existing_memory=existing_memory,
        validated_candidates=validated_candidates,
    )


def render_compressor_prompt(memory_full: str, next_context: str = "") -> str:
    """Render compressor prompt."""
    if memory_full is None:
        raise ValueError("memory_full is required")
    return COMPRESSOR_V1.format(
        memory_full=memory_full,
        next_context=next_context,
    )
