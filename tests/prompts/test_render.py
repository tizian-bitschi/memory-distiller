"""Tests for prompt rendering functions."""

import re

import pytest

from memory_distiller.prompts import (
    render_compressor_prompt,
    render_extractor_prompt,
    render_merger_prompt,
    render_validator_prompt,
)


class TestRenderExtractorPrompt:
    """Tests for render_extractor_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_extractor_prompt("", "chat")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        chat = "chat content"
        result = render_extractor_prompt(existing, chat)
        assert existing in result

    def test_contains_chat_log(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory"
        chat = "chat content here"
        result = render_extractor_prompt(existing, chat)
        assert chat in result

    def test_contains_candidate_output_format(self) -> None:
        """Extractor prompt contains exact candidate output format."""
        result = render_extractor_prompt("", "chat")
        assert "ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_extractor_prompt("existing", "chat")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_extractor_prompt("", "chat")
        assert isinstance(result, str)
        assert "chat" in result

    def test_missing_chat_log_raises_value_error(self) -> None:
        """Missing chat_log raises ValueError."""
        with pytest.raises(ValueError, match="chat_log is required"):
            render_extractor_prompt("existing", None)  # type: ignore


class TestRenderValidatorPrompt:
    """Tests for render_validator_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_validator_prompt("", "chat", "candidates")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        result = render_validator_prompt(existing, "chat", "candidates")
        assert existing in result

    def test_contains_chat_log(self) -> None:
        """Each prompt contains its inserted input."""
        chat = "chat content here"
        result = render_validator_prompt("", chat, "candidates")
        assert chat in result

    def test_contains_candidates(self) -> None:
        """Each prompt contains its inserted input."""
        candidates = "candidate content here"
        result = render_validator_prompt("", "chat", candidates)
        assert candidates in result

    def test_contains_validated_candidate_output_format(self) -> None:
        """Validator prompt contains exact validated candidate output format."""
        result = render_validator_prompt("", "chat", "candidates")
        assert (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON" in result
        )

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_validator_prompt("existing", "chat", "candidates")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_validator_prompt("", "chat", "candidates")
        assert isinstance(result, str)

    def test_missing_chat_log_raises_value_error(self) -> None:
        """Missing chat_log raises ValueError."""
        with pytest.raises(ValueError, match="chat_log is required"):
            render_validator_prompt("existing", None, "candidates")  # type: ignore

    def test_missing_candidates_raises_value_error(self) -> None:
        """Missing candidates for validator raises ValueError."""
        with pytest.raises(ValueError, match="candidates is required"):
            render_validator_prompt("existing", "chat", None)  # type: ignore


class TestRenderMergerPrompt:
    """Tests for render_merger_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_merger_prompt("", "validated")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        result = render_merger_prompt(existing, "validated candidates")
        assert existing in result

    def test_contains_validated_candidates(self) -> None:
        """Each prompt contains its inserted input."""
        validated = "validated candidates content"
        result = render_merger_prompt("", validated)
        assert validated in result

    def test_contains_memory_full(self) -> None:
        """Merger prompt contains # MEMORY_FULL."""
        result = render_merger_prompt("", "validated")
        assert "# MEMORY_FULL" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_merger_prompt("existing", "validated")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_merger_prompt("", "validated")
        assert isinstance(result, str)
        assert "validated" in result

    def test_missing_validated_candidates_raises_value_error(self) -> None:
        """Missing validated_candidates raises ValueError."""
        with pytest.raises(ValueError, match="validated_candidates is required"):
            render_merger_prompt("existing", None)  # type: ignore


class TestRenderCompressorPrompt:
    """Tests for render_compressor_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_compressor_prompt("memory_full")
        assert isinstance(result, str)

    def test_contains_memory_full(self) -> None:
        """Each prompt contains its inserted input."""
        memory_full = "full memory content"
        result = render_compressor_prompt(memory_full)
        assert memory_full in result

    def test_contains_memory_prompt(self) -> None:
        """Compressor prompt contains # MEMORY_PROMPT."""
        result = render_compressor_prompt("memory_full")
        assert "# MEMORY_PROMPT" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_compressor_prompt("memory_full", "next context")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_next_context_allowed(self) -> None:
        """Test empty next_context is allowed."""
        result = render_compressor_prompt("memory_full", "")
        assert isinstance(result, str)
        assert "memory_full" in result

    def test_next_context_inserted(self) -> None:
        """Next context is inserted when provided."""
        next_ctx = "next context here"
        result = render_compressor_prompt("memory_full", next_ctx)
        assert next_ctx in result

    def test_missing_memory_full_raises_value_error(self) -> None:
        """Missing memory_full raises ValueError."""
        with pytest.raises(ValueError, match="memory_full is required"):
            render_compressor_prompt(None, "next")  # type: ignore
