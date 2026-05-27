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
COMPRESSION_RESULT: str = "compression_result"

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
    # Pipeline results initialized to None (set after pipeline runs)
    st.session_state.setdefault(LAST_CHAT_LOG_UPLOAD_NAME, "")
    st.session_state.setdefault(LAST_EXISTING_MEMORY_UPLOAD_NAME, "")
    st.session_state.setdefault(EXTRACTION_RESULT, None)
    st.session_state.setdefault(VALIDATION_RESULT, None)
    st.session_state.setdefault(MERGE_RESULT, None)
    st.session_state.setdefault(COMPRESSION_RESULT, None)


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
