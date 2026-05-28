"""Tests for compress_tab module."""

from __future__ import annotations

from memory_distiller.ui.state import COMPRESSION_RESULT, MEMORY_PROMPT_RAW


class TestSaveMemoryPromptToState:
    """Tests for save_memory_prompt_to_state helper."""

    def test_rejects_empty_string(self):
        """Empty string is rejected and returns False."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        result = save_memory_prompt_to_state(state, "")
        assert result is False
        assert MEMORY_PROMPT_RAW not in state
        assert COMPRESSION_RESULT not in state

    def test_rejects_whitespace_only(self):
        """Whitespace-only string is rejected and returns False."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        result = save_memory_prompt_to_state(state, "   \n\t  ")
        assert result is False
        assert MEMORY_PROMPT_RAW not in state
        assert COMPRESSION_RESULT not in state

    def test_accepts_non_empty_content(self):
        """Non-empty content is stored in both state keys."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        content = "# MEMORY_PROMPT\nSome memory content"
        result = save_memory_prompt_to_state(state, content)
        assert result is True
        assert state[MEMORY_PROMPT_RAW] == content
        assert state[COMPRESSION_RESULT] == content

    def test_strips_whitespace(self):
        """Content is stripped of leading/trailing whitespace."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        content = "  # MEMORY_PROMPT\nSome content  "
        result = save_memory_prompt_to_state(state, content)
        assert result is True
        assert state[MEMORY_PROMPT_RAW] == "# MEMORY_PROMPT\nSome content"
        assert state[COMPRESSION_RESULT] == "# MEMORY_PROMPT\nSome content"

    def test_accepts_content_without_header(self):
        """Content without # MEMORY_PROMPT header is still accepted."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        content = "Just some memory text without header"
        result = save_memory_prompt_to_state(state, content)
        assert result is True
        assert state[MEMORY_PROMPT_RAW] == content
        assert state[COMPRESSION_RESULT] == content

    def test_preserves_multiline_content(self):
        """Multiline content is preserved correctly."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {}
        content = "# MEMORY_PROMPT\n- Rule 1\n- Rule 2\n- Rule 3"
        result = save_memory_prompt_to_state(state, content)
        assert result is True
        assert state[MEMORY_PROMPT_RAW] == content
        assert state[COMPRESSION_RESULT] == content

    def test_overwrites_existing_values(self):
        """New content overwrites existing state values."""
        from memory_distiller.ui.tabs.compress_tab import save_memory_prompt_to_state

        state = {MEMORY_PROMPT_RAW: "old content", COMPRESSION_RESULT: "old content"}
        content = "# MEMORY_PROMPT\nNew content"
        result = save_memory_prompt_to_state(state, content)
        assert result is True
        assert state[MEMORY_PROMPT_RAW] == content
        assert state[COMPRESSION_RESULT] == content
