"""Streamlit session state management for Memory Distiller UI."""

from __future__ import annotations

import streamlit as st

# Session state key constants
CHAT_LOG: str = "chat_log"
EXISTING_MEMORY: str = "existing_memory"
NEXT_CONTEXT: str = "next_context"

MODE: str = "mode"
MODEL: str = "model"
TEMPERATURE: str = "temperature"
THINKING_ENABLED: str = "thinking_enabled"
REASONING_EFFORT: str = "reasoning_effort"

CANDIDATES_RAW: str = "candidates_raw"
VALIDATED_CANDIDATES_RAW: str = "validated_candidates_raw"
MEMORY_FULL_RAW: str = "memory_full_raw"
MEMORY_PROMPT_RAW: str = "memory_prompt_raw"

EXTRACTION_RESULT: str = "extraction_result"
LAST_CHAT_LOG_UPLOAD_NAME: str = "_last_chat_log_upload_name"
LAST_EXISTING_MEMORY_UPLOAD_NAME: str = "_last_existing_memory_upload_name"
VALIDATION_RESULT: str = "validation_result"
MERGE_RESULT: str = "merge_result"
MERGE_PLAN_RAW: str = "merge_plan_raw"
COMPRESSION_RESULT: str = "compression_result"

# Usage and cost per step
EXTRACT_USAGE: str = "extract_usage"
EXTRACT_MODEL: str = "extract_model"
VALIDATE_USAGE: str = "validate_usage"
VALIDATE_MODEL: str = "validate_model"
MERGE_USAGE: str = "merge_usage"
MERGE_MODEL: str = "merge_model"
COMPRESS_USAGE: str = "compress_usage"
COMPRESS_MODEL: str = "compress_model"

EXTRACT_COST: str = "extract_cost"
VALIDATE_COST: str = "validate_cost"
MERGE_COST: str = "merge_cost"
COMPRESS_COST: str = "compress_cost"

# Estimated request tokens per step
EXTRACT_ESTIMATED_REQUEST_TOKENS: str = "extract_estimated_request_tokens"
VALIDATE_ESTIMATED_REQUEST_TOKENS: str = "validate_estimated_request_tokens"
MERGE_ESTIMATED_REQUEST_TOKENS: str = "merge_estimated_request_tokens"
COMPRESS_ESTIMATED_REQUEST_TOKENS: str = "compress_estimated_request_tokens"

DEEPSEEK_BALANCE: str = "deepseek_balance"

# Pipeline run log
RUN_LOG_EVENTS: str = "run_log_events"

# Default values
DEFAULT_MODE: str = "Prompt-only"
DEFAULT_MODEL: str = "deepseek-v4-pro"
DEFAULT_TEMPERATURE: float = 0.2
DEFAULT_THINKING_ENABLED: bool = True
DEFAULT_REASONING_EFFORT: str = "high"


def initialize_session_state() -> None:
    """Initialize all session state keys with defaults if missing.

    Uses st.session_state.setdefault() to preserve existing values.
    """
    st.session_state.setdefault(CHAT_LOG, "")
    st.session_state.setdefault(EXISTING_MEMORY, "")
    st.session_state.setdefault(NEXT_CONTEXT, "")
    st.session_state.setdefault(MODE, DEFAULT_MODE)
    st.session_state.setdefault(MODEL, DEFAULT_MODEL)
    st.session_state.setdefault(TEMPERATURE, DEFAULT_TEMPERATURE)
    st.session_state.setdefault(THINKING_ENABLED, DEFAULT_THINKING_ENABLED)
    st.session_state.setdefault(REASONING_EFFORT, DEFAULT_REASONING_EFFORT)
    st.session_state.setdefault(CANDIDATES_RAW, "")
    st.session_state.setdefault(VALIDATED_CANDIDATES_RAW, "")
    st.session_state.setdefault(MEMORY_FULL_RAW, "")
    st.session_state.setdefault(MEMORY_PROMPT_RAW, "")
    st.session_state.setdefault(MERGE_PLAN_RAW, "")
    # Pipeline results initialized to None (set after pipeline runs)
    st.session_state.setdefault(LAST_CHAT_LOG_UPLOAD_NAME, "")
    st.session_state.setdefault(LAST_EXISTING_MEMORY_UPLOAD_NAME, "")
    st.session_state.setdefault(EXTRACTION_RESULT, None)
    st.session_state.setdefault(VALIDATION_RESULT, None)
    st.session_state.setdefault(MERGE_RESULT, None)
    st.session_state.setdefault(COMPRESSION_RESULT, None)
    # Usage and cost tracking
    st.session_state.setdefault(EXTRACT_USAGE, None)
    st.session_state.setdefault(EXTRACT_MODEL, None)
    st.session_state.setdefault(VALIDATE_USAGE, None)
    st.session_state.setdefault(VALIDATE_MODEL, None)
    st.session_state.setdefault(MERGE_USAGE, None)
    st.session_state.setdefault(MERGE_MODEL, None)
    st.session_state.setdefault(COMPRESS_USAGE, None)
    st.session_state.setdefault(COMPRESS_MODEL, None)
    st.session_state.setdefault(EXTRACT_COST, None)
    st.session_state.setdefault(VALIDATE_COST, None)
    st.session_state.setdefault(MERGE_COST, None)
    st.session_state.setdefault(COMPRESS_COST, None)
    # Estimated request tokens per step
    st.session_state.setdefault(EXTRACT_ESTIMATED_REQUEST_TOKENS, None)
    st.session_state.setdefault(VALIDATE_ESTIMATED_REQUEST_TOKENS, None)
    st.session_state.setdefault(MERGE_ESTIMATED_REQUEST_TOKENS, None)
    st.session_state.setdefault(COMPRESS_ESTIMATED_REQUEST_TOKENS, None)
    st.session_state.setdefault(DEEPSEEK_BALANCE, None)
    st.session_state.setdefault(RUN_LOG_EVENTS, [])


def get_state_value(key: str, default: str | None = None) -> str | None:
    """Get a session state value with optional default.

    Args:
        key: Session state key to retrieve.
        default: Default value if key not found (defaults to None).

    Returns:
        The value stored at key, or default if not found.
    """
    value: str | None = st.session_state.get(key, default)
    return value


def set_state_value(key: str, value: str | None) -> None:
    """Set a session state value.

    Args:
        key: Session state key to set.
        value: Value to store at key.
    """
    st.session_state[key] = value
