"""Tests for UI session state management."""

from __future__ import annotations

import pytest


class TestSessionStateKeys:
    """Tests for session state key constants."""

    def test_chat_log_key(self):
        """Chat log key is defined."""
        from memory_distiller.ui.state import CHAT_LOG

        assert CHAT_LOG == "chat_log"

    def test_existing_memory_key(self):
        """Existing memory key is defined."""
        from memory_distiller.ui.state import EXISTING_MEMORY

        assert EXISTING_MEMORY == "existing_memory"

    def test_next_context_key(self):
        """Next context key is defined."""
        from memory_distiller.ui.state import NEXT_CONTEXT

        assert NEXT_CONTEXT == "next_context"

    def test_mode_key(self):
        """Mode key is defined."""
        from memory_distiller.ui.state import MODE

        assert MODE == "mode"

    def test_model_key(self):
        """Model key is defined."""
        from memory_distiller.ui.state import MODEL

        assert MODEL == "model"

    def test_temperature_key(self):
        """Temperature key is defined."""
        from memory_distiller.ui.state import TEMPERATURE

        assert TEMPERATURE == "temperature"

    def test_thinking_enabled_key(self):
        """Thinking enabled key is defined."""
        from memory_distiller.ui.state import THINKING_ENABLED

        assert THINKING_ENABLED == "thinking_enabled"

    def test_reasoning_effort_key(self):
        """Reasoning effort key is defined."""
        from memory_distiller.ui.state import REASONING_EFFORT

        assert REASONING_EFFORT == "reasoning_effort"

    def test_candidates_raw_key(self):
        """Candidates raw key is defined."""
        from memory_distiller.ui.state import CANDIDATES_RAW

        assert CANDIDATES_RAW == "candidates_raw"

    def test_validated_candidates_raw_key(self):
        """Validated candidates raw key is defined."""
        from memory_distiller.ui.state import VALIDATED_CANDIDATES_RAW

        assert VALIDATED_CANDIDATES_RAW == "validated_candidates_raw"

    def test_memory_full_raw_key(self):
        """Memory full raw key is defined."""
        from memory_distiller.ui.state import MEMORY_FULL_RAW

        assert MEMORY_FULL_RAW == "memory_full_raw"

    def test_memory_prompt_raw_key(self):
        """Memory prompt raw key is defined."""
        from memory_distiller.ui.state import MEMORY_PROMPT_RAW

        assert MEMORY_PROMPT_RAW == "memory_prompt_raw"

    def test_extraction_result_key(self):
        """Extraction result key is defined."""
        from memory_distiller.ui.state import EXTRACTION_RESULT

        assert EXTRACTION_RESULT == "extraction_result"

    def test_validation_result_key(self):
        """Validation result key is defined."""
        from memory_distiller.ui.state import VALIDATION_RESULT

        assert VALIDATION_RESULT == "validation_result"

    def test_merge_result_key(self):
        """Merge result key is defined."""
        from memory_distiller.ui.state import MERGE_RESULT

        assert MERGE_RESULT == "merge_result"

    def test_compression_result_key(self):
        """Compression result key is defined."""
        from memory_distiller.ui.state import COMPRESSION_RESULT

        assert COMPRESSION_RESULT == "compression_result"

    def test_extract_usage_key(self):
        """Extract usage key is defined."""
        from memory_distiller.ui.state import EXTRACT_USAGE

        assert EXTRACT_USAGE == "extract_usage"

    def test_validate_usage_key(self):
        """Validate usage key is defined."""
        from memory_distiller.ui.state import VALIDATE_USAGE

        assert VALIDATE_USAGE == "validate_usage"

    def test_merge_usage_key(self):
        """Merge usage key is defined."""
        from memory_distiller.ui.state import MERGE_USAGE

        assert MERGE_USAGE == "merge_usage"

    def test_compress_usage_key(self):
        """Compress usage key is defined."""
        from memory_distiller.ui.state import COMPRESS_USAGE

        assert COMPRESS_USAGE == "compress_usage"

    def test_extract_cost_key(self):
        """Extract cost key is defined."""
        from memory_distiller.ui.state import EXTRACT_COST

        assert EXTRACT_COST == "extract_cost"

    def test_validate_cost_key(self):
        """Validate cost key is defined."""
        from memory_distiller.ui.state import VALIDATE_COST

        assert VALIDATE_COST == "validate_cost"

    def test_merge_cost_key(self):
        """Merge cost key is defined."""
        from memory_distiller.ui.state import MERGE_COST

        assert MERGE_COST == "merge_cost"

    def test_compress_cost_key(self):
        """Compress cost key is defined."""
        from memory_distiller.ui.state import COMPRESS_COST

        assert COMPRESS_COST == "compress_cost"

    def test_deepseek_balance_key(self):
        """DeepSeek balance key is defined."""
        from memory_distiller.ui.state import DEEPSEEK_BALANCE

        assert DEEPSEEK_BALANCE == "deepseek_balance"


class TestDefaultValues:
    """Tests for default value constants."""

    def test_default_mode(self):
        """Default mode is 'Prompt-only'."""
        from memory_distiller.ui.state import DEFAULT_MODE

        assert DEFAULT_MODE == "Prompt-only"

    def test_default_model(self):
        """Default model is 'deepseek-v4-pro'."""
        from memory_distiller.ui.state import DEFAULT_MODEL

        assert DEFAULT_MODEL == "deepseek-v4-pro"

    def test_default_temperature(self):
        """Default temperature is 0.2."""
        from memory_distiller.ui.state import DEFAULT_TEMPERATURE

        assert DEFAULT_TEMPERATURE == 0.2

    def test_default_thinking_enabled(self):
        """Default thinking enabled is True."""
        from memory_distiller.ui.state import DEFAULT_THINKING_ENABLED

        assert DEFAULT_THINKING_ENABLED is True

    def test_default_reasoning_effort(self):
        """Default reasoning effort is 'high'."""
        from memory_distiller.ui.state import DEFAULT_REASONING_EFFORT

        assert DEFAULT_REASONING_EFFORT == "high"


class TestInitializeSessionState:
    """Tests for initialize_session_state function."""

    def test_sets_default_chat_log(self, patch_streamlit_session_state):
        """Sets default chat_log when missing."""
        from memory_distiller.ui.state import (
            CHAT_LOG,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(CHAT_LOG) == ""

    def test_sets_default_existing_memory(self, patch_streamlit_session_state):
        """Sets default existing_memory when missing."""
        from memory_distiller.ui.state import (
            EXISTING_MEMORY,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(EXISTING_MEMORY) == ""

    def test_sets_default_next_context(self, patch_streamlit_session_state):
        """Sets default next_context when missing."""
        from memory_distiller.ui.state import (
            NEXT_CONTEXT,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(NEXT_CONTEXT) == ""

    def test_sets_default_mode(self, patch_streamlit_session_state):
        """Sets default mode when missing."""
        from memory_distiller.ui.state import (
            DEFAULT_MODE,
            MODE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(MODE) == DEFAULT_MODE

    def test_sets_default_temperature(self, patch_streamlit_session_state):
        """Sets default temperature when missing."""
        from memory_distiller.ui.state import (
            DEFAULT_TEMPERATURE,
            TEMPERATURE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(TEMPERATURE) == DEFAULT_TEMPERATURE

    def test_sets_default_extract_usage(self, patch_streamlit_session_state):
        """Sets default extract_usage to None."""
        from memory_distiller.ui.state import (
            EXTRACT_USAGE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(EXTRACT_USAGE) is None

    def test_sets_default_validate_usage(self, patch_streamlit_session_state):
        """Sets default validate_usage to None."""
        from memory_distiller.ui.state import (
            VALIDATE_USAGE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(VALIDATE_USAGE) is None

    def test_sets_default_merge_usage(self, patch_streamlit_session_state):
        """Sets default merge_usage to None."""
        from memory_distiller.ui.state import (
            MERGE_USAGE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(MERGE_USAGE) is None

    def test_sets_default_compress_usage(self, patch_streamlit_session_state):
        """Sets default compress_usage to None."""
        from memory_distiller.ui.state import (
            COMPRESS_USAGE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(COMPRESS_USAGE) is None

    def test_sets_default_extract_cost(self, patch_streamlit_session_state):
        """Sets default extract_cost to None."""
        from memory_distiller.ui.state import (
            EXTRACT_COST,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(EXTRACT_COST) is None

    def test_sets_default_validate_cost(self, patch_streamlit_session_state):
        """Sets default validate_cost to None."""
        from memory_distiller.ui.state import (
            VALIDATE_COST,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(VALIDATE_COST) is None

    def test_sets_default_merge_cost(self, patch_streamlit_session_state):
        """Sets default merge_cost to None."""
        from memory_distiller.ui.state import (
            MERGE_COST,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(MERGE_COST) is None

    def test_sets_default_compress_cost(self, patch_streamlit_session_state):
        """Sets default compress_cost to None."""
        from memory_distiller.ui.state import (
            COMPRESS_COST,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(COMPRESS_COST) is None

    def test_sets_default_deepseek_balance(self, patch_streamlit_session_state):
        """Sets default deepseek_balance to None."""
        from memory_distiller.ui.state import (
            DEEPSEEK_BALANCE,
            initialize_session_state,
        )

        initialize_session_state()
        assert patch_streamlit_session_state.get(DEEPSEEK_BALANCE) is None

    def test_does_not_overwrite_existing_values(self, patch_streamlit_session_state):
        """Does not overwrite existing session state values."""
        from memory_distiller.ui.state import (
            CHAT_LOG,
            initialize_session_state,
        )

        patch_streamlit_session_state[CHAT_LOG] = "existing chat log content"
        initialize_session_state()
        assert patch_streamlit_session_state.get(CHAT_LOG) == "existing chat log content"


class TestGetStateValue:
    """Tests for get_state_value helper function."""

    def test_returns_value_when_key_exists(self, patch_streamlit_session_state):
        """Returns value when key exists in session state."""
        from memory_distiller.ui.state import CHAT_LOG, get_state_value

        patch_streamlit_session_state[CHAT_LOG] = "test value"
        result = get_state_value(CHAT_LOG)
        assert result == "test value"

    def test_returns_default_when_key_missing(self, patch_streamlit_session_state):
        """Returns default when key not found."""
        from memory_distiller.ui.state import get_state_value

        result = get_state_value("nonexistent_key", default="fallback")
        assert result == "fallback"

    def test_returns_none_default_when_key_missing(self, patch_streamlit_session_state):
        """Returns None when key missing and no default provided."""
        from memory_distiller.ui.state import get_state_value

        result = get_state_value("nonexistent_key")
        assert result is None


class TestSetStateValue:
    """Tests for set_state_value helper function."""

    def test_sets_value_in_session_state(self, patch_streamlit_session_state):
        """Sets value in session state."""
        from memory_distiller.ui.state import CHAT_LOG, set_state_value

        set_state_value(CHAT_LOG, "new value")
        assert patch_streamlit_session_state.get(CHAT_LOG) == "new value"

    def test_can_set_none_value(self, patch_streamlit_session_state):
        """Can set None as a value."""
        from memory_distiller.ui.state import CHAT_LOG, set_state_value

        set_state_value(CHAT_LOG, None)
        assert patch_streamlit_session_state.get(CHAT_LOG) is None


@pytest.fixture
def patch_streamlit_session_state(monkeypatch):
    """Patch st.session_state for testing without Streamlit."""
    from memory_distiller.ui import state as state_module

    session_state: dict[str, str | None] = {}
    monkeypatch.setattr(state_module, "st", type("MockSt", (), {"session_state": session_state}))
    yield session_state
