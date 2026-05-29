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


class TestChatLogHtmlSupport:
    """Tests for Issue #29 - ChatGPT HTML chat export support."""

    def test_chat_log_file_uploader_accepts_html(self):
        """Chat log file_uploader type includes 'html'."""
        source = inspect.getsource(render_input_tab)
        # Find the chat_log_file uploader block
        assert 'type=["txt", "md", "markdown", "html", "htm"]' in source

    def test_chat_log_uses_validate_chat_log_extension(self):
        """Chat log uses validate_chat_log_extension, not validate_text_file_extension."""
        source = inspect.getsource(render_input_tab)
        # Should use validate_chat_log_extension
        assert "validate_chat_log_extension" in source
        # The chat log block should NOT use validate_text_file_extension
        lines = source.splitlines()
        chat_log_block_idx = None
        for i, line in enumerate(lines):
            if 'key="chat_log_upload"' in line:
                chat_log_block_idx = i
                break
        assert chat_log_block_idx is not None
        # Check within the chat log block (next ~20 lines after file_uploader)
        chat_log_block = lines[chat_log_block_idx : chat_log_block_idx + 20]
        block_source = "\n".join(chat_log_block)
        assert "validate_text_file_extension" not in block_source

    def test_chat_log_error_message_mentions_html_htm(self):
        """Error message for invalid chat log extension mentions html and htm."""
        source = inspect.getsource(render_input_tab)
        # Should mention html and htm in the allowed extensions error
        assert ".html, .htm" in source


class TestExistingMemoryUploadReliability:
    """Regression tests for Issue #39 - Existing Memory upload reliability."""

    def test_existing_memory_upload_uses_hashlib_sha256(self):
        """Existing Memory upload computes SHA256 hash, not filename-only comparison."""
        source = inspect.getsource(render_input_tab)
        # Must use hashlib.sha256 for content-based change detection
        assert "hashlib.sha256" in source
        assert "file_hash" in source

    def test_existing_memory_text_area_uses_existing_memory_key(self):
        """Existing Memory text_area uses canonical EXISTING_MEMORY key."""
        source = inspect.getsource(render_input_tab)
        assert "key=EXISTING_MEMORY" in source

    def test_same_filename_different_content_updates(self):
        """Same filename with different content triggers update via hash detection."""
        source = inspect.getsource(render_input_tab)
        # The implementation constructs current_identity with f"{filename}|{file_hash}"
        assert "current_identity" in source

    def test_invalid_extension_shows_error(self):
        """Invalid file extension for existing memory shows error."""
        source = inspect.getsource(render_input_tab)
        # Should have error message for invalid extension
        assert "Invalid file extension" in source
        assert ".txt" in source and ".md" in source and ".markdown" in source
