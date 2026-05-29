"""Tests for Validate tab prompt rendering and widgets."""

from __future__ import annotations

import inspect

from memory_distiller.application.validation_service import ValidationService
from memory_distiller.ui.tabs import validate_tab as validate_tab_module


class TestValidateTabPromptPreview:
    """Regression tests for Issue #39 - prompt preview uses st.code() not st.text_area()."""

    def test_prompt_preview_uses_st_code_not_text_area(self):
        """Prompt preview in Validate tab uses st.code(), not st.text_area(value=prompt)."""
        source = inspect.getsource(validate_tab_module)
        # Must NOT have st.text_area with value=prompt for the prompt preview
        assert 'st.text_area("Prompt"' not in source
        assert 'st.text_area("Validator Prompt"' not in source
        assert 'st.text_area("Rendered Prompt"' not in source
        # Must use st.code for the prompt display
        assert "st.code" in source

    def test_editablellm_response_uses_text_area(self):
        """Editable LLM response text_area uses st.text_area."""
        source = inspect.getsource(validate_tab_module)
        # The LLM response input should be st.text_area
        assert "st.text_area(" in source
        assert '"validate_llm_response"' in source or "key=" in source


class TestValidationServiceRenderPrompt:
    """Tests for ValidationService.render_prompt includes Existing Memory."""

    def test_render_prompt_includes_existing_memory_marker(self):
        """ValidationService.render_prompt includes existing_memory content in output."""
        service = ValidationService()
        marker = "P:LoopTest|FACT|M|D|Existing memory marker.|Test evidence."
        prompt = service.render_prompt(
            existing_memory=marker,
            chat_log="test chat log",
            candidates="test candidates",
        )
        assert marker in prompt
