"""Tests for Input tab state handling."""

from __future__ import annotations

import inspect

from memory_distiller.ui.tabs.input_tab import render_input_tab


class TestInputTabUsesExplicitWidgetKeys:
    """Regression tests for Issue #22 - explicit widget keys prevent state loss."""

    def test_chat_log_text_area_uses_key_constant(self):
        """CHAT_LOG text_area uses key=CHAT_LOG."""
        source = inspect.getsource(render_input_tab)
        assert "key=CHAT_LOG" in source
        # Must NOT have manual assignment after widget
        lines = source.splitlines()
        chat_log_widget_idx = None
        for i, line in enumerate(lines):
            if "key=CHAT_LOG" in line:
                chat_log_widget_idx = i
                break
        assert chat_log_widget_idx is not None
        # Check no st.session_state[CHAT_LOG] = ... in the next 5 lines
        for line in lines[chat_log_widget_idx : chat_log_widget_idx + 5]:
            assert "st.session_state[CHAT_LOG] =" not in line

    def test_existing_memory_text_area_uses_key_constant(self):
        """EXISTING_MEMORY text_area uses key=EXISTING_MEMORY."""
        source = inspect.getsource(render_input_tab)
        assert "key=EXISTING_MEMORY" in source
        lines = source.splitlines()
        widget_idx = None
        for i, line in enumerate(lines):
            if "key=EXISTING_MEMORY" in line:
                widget_idx = i
                break
        assert widget_idx is not None
        for line in lines[widget_idx : widget_idx + 5]:
            assert "st.session_state[EXISTING_MEMORY] =" not in line

    def test_next_context_text_area_uses_key_constant(self):
        """NEXT_CONTEXT text_area uses key=NEXT_CONTEXT."""
        source = inspect.getsource(render_input_tab)
        assert "key=NEXT_CONTEXT" in source
        lines = source.splitlines()
        widget_idx = None
        for i, line in enumerate(lines):
            if "key=NEXT_CONTEXT" in line:
                widget_idx = i
                break
        assert widget_idx is not None
        for line in lines[widget_idx : widget_idx + 5]:
            assert "st.session_state[NEXT_CONTEXT] =" not in line
