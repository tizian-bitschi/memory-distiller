"""Tests for Extract tab prompt rendering and widgets."""

from __future__ import annotations

import inspect

from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.ui.tabs import extract_tab as extract_tab_module


class TestExtractTabPromptPreview:
    """Regression tests for Issue #39 - prompt preview uses st.code() not st.text_area()."""

    def test_prompt_preview_uses_st_code_not_text_area(self):
        """Prompt preview in Extract tab uses st.code(), not st.text_area(value=prompt)."""
        source = inspect.getsource(extract_tab_module)
        # Must NOT have st.text_area with value=prompt for the prompt preview
        assert 'st.text_area("Prompt"' not in source
        assert 'st.text_area("Extractor Prompt"' not in source
        assert 'st.text_area("Rendered Prompt"' not in source
        # Must use st.code for the prompt display
        assert "st.code" in source

    def test_editablellm_response_uses_text_area(self):
        """Editable LLM response text_area uses st.text_area."""
        source = inspect.getsource(extract_tab_module)
        # The LLM response input should be st.text_area
        assert "st.text_area(" in source
        assert '"extract_llm_response"' in source or "key=" in source


class TestExtractionServiceRenderPrompt:
    """Tests for ExtractionService.render_prompt includes Existing Memory."""

    def test_render_prompt_includes_existing_memory_marker(self):
        """ExtractionService.render_prompt includes existing_memory content in output."""
        service = ExtractionService()
        marker = "P:LoopTest|FACT|M|D|Existing memory marker.|Test evidence."
        prompt = service.render_prompt(existing_memory=marker, chat_log="test chat log")
        assert marker in prompt


class TestExtractTabTokenSummary:
    """Tests for Issue #38 - token transparency in extract_tab."""

    def test_source_imports_render_token_summary(self):
        """Extract tab imports render_token_summary from components."""
        source = inspect.getsource(extract_tab_module)
        assert "render_token_summary" in source
        assert "from memory_distiller.ui.components import" in source

    def test_source_imports_estimate_tokens(self):
        """Extract tab imports estimate_tokens from components."""
        source = inspect.getsource(extract_tab_module)
        assert "estimate_tokens" in source

    def test_source_has_estimated_request_tokens_state_key(self):
        """Extract tab references EXTRACT_ESTIMATED_REQUEST_TOKENS state key."""
        source = inspect.getsource(extract_tab_module)
        assert "EXTRACT_ESTIMATED_REQUEST_TOKENS" in source

    def test_prompt_only_mode_calls_render_token_summary(self):
        """Prompt-only mode calls render_token_summary before st.code(prompt)."""
        source = inspect.getsource(extract_tab_module)
        prompt_only_idx = source.find("def _render_extract_prompt_only")
        code_idx = source.find("st.code(prompt", prompt_only_idx)
        render_idx = source.find("render_token_summary", prompt_only_idx)
        assert render_idx != -1, "render_token_summary not found in prompt-only mode"
        assert code_idx != -1, "st.code(prompt) not found in prompt-only mode"
        assert render_idx < code_idx, "render_token_summary should be called before st.code(prompt)"

    def test_prompt_only_mode_stores_estimated_request_tokens(self):
        """Prompt-only mode stores estimated request tokens in session state."""
        source = inspect.getsource(extract_tab_module)
        prompt_only_idx = source.find("def _render_extract_prompt_only")
        state_set_idx = source.find(
            "st.session_state[EXTRACT_ESTIMATED_REQUEST_TOKENS]", prompt_only_idx
        )
        assert state_set_idx != -1, "Session state for estimated request tokens not set"

    def test_api_mode_calls_render_token_summary_before_run_button(self):
        """API mode calls render_token_summary before run button."""
        source = inspect.getsource(extract_tab_module)
        api_idx = source.find("def _render_extract_api")
        run_btn_idx = source.find('st.button("Run extraction"', api_idx)
        render_idx = source.find("render_token_summary", api_idx)
        assert render_idx != -1, "render_token_summary not found in API mode"
        assert run_btn_idx != -1, "Run extraction button not found"
        assert render_idx < run_btn_idx, "render_token_summary should be called before run button"

    def test_api_mode_passes_provider_usage_in_display_section(self):
        """API mode passes provider_usage to render_token_summary in display section."""
        source = inspect.getsource(extract_tab_module)
        api_idx = source.find("def _render_extract_api")
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
