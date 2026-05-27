"""UI-level helper for LLM config and client construction."""

from __future__ import annotations

import streamlit as st

from memory_distiller.llm.config import LlmConfig
from memory_distiller.llm.deepseek_client import DeepSeekClient
from memory_distiller.ui.state import (
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_TEMPERATURE,
    DEFAULT_THINKING_ENABLED,
    MODEL,
    REASONING_EFFORT,
    TEMPERATURE,
    THINKING_ENABLED,
)


def build_llm_config_from_values(
    *,
    model: str,
    temperature: float,
    thinking_enabled: bool,
    reasoning_effort: str,
) -> LlmConfig:
    """Build LlmConfig from explicit values.

    This is a pure function with no Streamlit dependencies.

    Args:
        model: LLM model name.
        temperature: Temperature setting.
        thinking_enabled: Whether to enable thinking mode.
        reasoning_effort: Reasoning effort level ("low", "medium", "high").

    Returns:
        LlmConfig configured with the given values.
    """
    return LlmConfig(
        model=model,
        temperature=temperature,
        thinking_enabled=thinking_enabled,
        reasoning_effort=reasoning_effort,
    )


def create_llm_config_from_session_state() -> LlmConfig:
    """Build LlmConfig from session state.

    Reads from st.session_state using keys: MODEL, TEMPERATURE,
    THINKING_ENABLED, REASONING_EFFORT with defaults from state.py.

    Returns:
        LlmConfig configured from session state values.

    Raises:
        ValueError: If model name is not supported.
        MissingApiKeyError: If API key is not set in environment.
    """
    config = LlmConfig(
        model=st.session_state.get(MODEL, DEFAULT_MODEL),
        temperature=st.session_state.get(TEMPERATURE, DEFAULT_TEMPERATURE),
        thinking_enabled=st.session_state.get(THINKING_ENABLED, DEFAULT_THINKING_ENABLED),
        reasoning_effort=st.session_state.get(REASONING_EFFORT, DEFAULT_REASONING_EFFORT),
    )
    return config


def create_deepseek_client_from_session_state() -> DeepSeekClient:
    """Create DeepSeekClient from session state.

    Build LlmConfig from session state and use it to create
    a DeepSeekClient.

    Returns:
        DeepSeekClient configured from session state.

    Raises:
        ValueError: If model name is not supported.
        MissingApiKeyError: If API key is not set in environment.
    """
    config = create_llm_config_from_session_state()
    client = DeepSeekClient(config)
    return client
