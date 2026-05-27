"""Tests for UI LLM factory helpers."""

from __future__ import annotations

import pytest


class TestBuildLlmConfigFromValues:
    """Tests for build_llm_config_from_values function."""

    def test_builds_correct_llm_config_with_given_values(self):
        """Builds LlmConfig with given model, temperature, thinking_enabled, reasoning_effort."""
        from memory_distiller.ui.llm_factory import build_llm_config_from_values

        config = build_llm_config_from_values(
            model="deepseek-v4-pro",
            temperature=0.7,
            thinking_enabled=True,
            reasoning_effort="high",
        )
        assert config.model == "deepseek-v4-pro"
        assert config.temperature == 0.7
        assert config.thinking_enabled is True
        assert config.reasoning_effort == "high"

    def test_respects_all_parameters(self):
        """Respects model, temperature, thinking_enabled, and reasoning_effort parameters."""
        from memory_distiller.ui.llm_factory import build_llm_config_from_values

        config = build_llm_config_from_values(
            model="deepseek-v4-flash",
            temperature=1.0,
            thinking_enabled=False,
            reasoning_effort="low",
        )
        assert config.model == "deepseek-v4-flash"
        assert config.temperature == 1.0
        assert config.thinking_enabled is False
        assert config.reasoning_effort == "low"

    def test_function_is_pure_and_does_not_touch_session_state(self, patch_streamlit_session_state):
        """Does not read or modify session state - pure function."""
        from memory_distiller.ui.llm_factory import build_llm_config_from_values

        # Store original session state to verify it is not modified
        original_keys = set(patch_streamlit_session_state.keys())

        # Call the function
        build_llm_config_from_values(
            model="deepseek-v4-pro",
            temperature=0.2,
            thinking_enabled=True,
            reasoning_effort="high",
        )

        # Session state should be unchanged
        assert set(patch_streamlit_session_state.keys()) == original_keys


class TestCreateLlmConfigFromSessionState:
    """Tests for create_llm_config_from_session_state function."""

    def test_reads_defaults_when_session_state_empty(self, patch_streamlit_session_state):
        """Uses defaults from state.py when session state keys are missing."""
        from memory_distiller.ui.llm_factory import create_llm_config_from_session_state
        from memory_distiller.ui.state import (
            DEFAULT_MODEL,
            DEFAULT_REASONING_EFFORT,
            DEFAULT_TEMPERATURE,
            DEFAULT_THINKING_ENABLED,
        )

        config = create_llm_config_from_session_state()
        assert config.model == DEFAULT_MODEL
        assert config.temperature == DEFAULT_TEMPERATURE
        assert config.thinking_enabled == DEFAULT_THINKING_ENABLED
        assert config.reasoning_effort == DEFAULT_REASONING_EFFORT

    def test_respects_session_state_values(self, patch_streamlit_session_state):
        """Reads model, temperature, thinking_enabled, reasoning_effort from session state."""
        from memory_distiller.ui.llm_factory import create_llm_config_from_session_state
        from memory_distiller.ui.state import (
            MODEL,
            REASONING_EFFORT,
            TEMPERATURE,
            THINKING_ENABLED,
        )

        patch_streamlit_session_state[MODEL] = "deepseek-v4-flash"
        patch_streamlit_session_state[TEMPERATURE] = 0.9
        patch_streamlit_session_state[THINKING_ENABLED] = False
        patch_streamlit_session_state[REASONING_EFFORT] = "low"

        config = create_llm_config_from_session_state()
        assert config.model == "deepseek-v4-flash"
        assert config.temperature == 0.9
        assert config.thinking_enabled is False
        assert config.reasoning_effort == "low"


@pytest.fixture
def patch_streamlit_session_state(monkeypatch):
    """Patch st.session_state for testing without Streamlit."""
    from memory_distiller.ui import llm_factory as llm_factory_module
    from memory_distiller.ui import state as state_module

    session_state: dict[str, str | None] = {}
    mock_st = type("MockSt", (), {"session_state": session_state})
    monkeypatch.setattr(state_module, "st", mock_st)
    monkeypatch.setattr(llm_factory_module, "st", mock_st)
    yield session_state
