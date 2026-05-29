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
