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


class TestCompressTabTokenSummary:
    """Tests for Issue #38 - token transparency in compress_tab."""

    def test_source_imports_render_token_summary(self):
        """Compress tab imports render_token_summary from components."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        assert "render_token_summary" in source
        assert "from memory_distiller.ui.components import" in source

    def test_source_imports_estimate_tokens(self):
        """Compress tab imports estimate_tokens from components."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        assert "estimate_tokens" in source

    def test_source_has_estimated_request_tokens_state_key(self):
        """Compress tab references COMPRESS_ESTIMATED_REQUEST_TOKENS state key."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        assert "COMPRESS_ESTIMATED_REQUEST_TOKENS" in source

    def test_prompt_only_mode_calls_render_token_summary(self):
        """Prompt-only mode calls render_token_summary before st.code(prompt)."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        prompt_only_idx = source.find("def _render_compress_prompt_only")
        code_idx = source.find("st.code(prompt", prompt_only_idx)
        render_idx = source.find("render_token_summary", prompt_only_idx)
        assert render_idx != -1, "render_token_summary not found in prompt-only mode"
        assert code_idx != -1, "st.code(prompt) not found in prompt-only mode"
        assert render_idx < code_idx, "render_token_summary should be called before st.code(prompt)"

    def test_prompt_only_mode_stores_estimated_request_tokens(self):
        """Prompt-only mode stores estimated request tokens in session state."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        prompt_only_idx = source.find("def _render_compress_prompt_only")
        state_set_idx = source.find(
            "st.session_state[COMPRESS_ESTIMATED_REQUEST_TOKENS]", prompt_only_idx
        )
        assert state_set_idx != -1, "Session state for estimated request tokens not set"

    def test_api_mode_calls_render_token_summary_before_run_button(self):
        """API mode calls render_token_summary before run button."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        api_idx = source.find("def _render_compress_api")
        run_btn_idx = source.find('st.button("Run compression"', api_idx)
        render_idx = source.find("render_token_summary", api_idx)
        assert render_idx != -1, "render_token_summary not found in API mode"
        assert run_btn_idx != -1, "Run compression button not found"
        assert render_idx < run_btn_idx, "render_token_summary should be called before run button"

    def test_api_mode_passes_provider_usage_in_display_section(self):
        """API mode passes provider_usage to render_token_summary in display section."""
        import inspect

        from memory_distiller.ui.tabs import compress_tab as compress_tab_module

        source = inspect.getsource(compress_tab_module)
        api_idx = source.find("def _render_compress_api")
        next_func_idx = source.find("def ", api_idx + 1)
        if next_func_idx == -1:
            module_end = len(source)
        else:
            module_end = next_func_idx
        render_calls = []
        pos = api_idx
        while True:
            pos = source.find("render_token_summary", pos)
            if pos == -1 or pos > module_end:
                break
            render_calls.append(pos)
            pos += 1
        assert len(render_calls) >= 2, "Expected at least 2 render_token_summary calls in API mode"
        display_section = source[render_calls[1] :]
        assert "provider_usage=" in display_section, "provider_usage not passed in display section"
