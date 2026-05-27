"""Tests for compression service."""

import pytest

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.llm.mock_client import MockClient


class TestCompressionService:
    """Tests for CompressionService."""

    def test_render_prompt_includes_memory_full_and_next_context(self) -> None:
        """Verify prompt contains inputs."""
        service = CompressionService()
        memory_full = "full memory content"
        next_context = "next context here"
        prompt = service.render_prompt(memory_full=memory_full, next_context=next_context)
        assert memory_full in prompt
        assert next_context in prompt

    def test_run_returns_raw_response_as_memory_prompt(self) -> None:
        """Verify memory_prompt == raw_response."""
        expected_response = "compressed memory prompt content"
        service = CompressionService()
        mock_client = MockClient(response=expected_response)
        result = service.run(
            memory_full="full memory",
            next_context="next context",
            llm_client=mock_client,
        )
        assert result.prompt is not None
        assert result.raw_response == expected_response
        assert result.memory_prompt == expected_response
        assert result.memory_prompt == result.raw_response


class TestCompressionServiceRenderPromptValidation:
    """Tests for render_prompt validation in CompressionService."""

    def test_missing_memory_full_raises_value_error(self) -> None:
        """Missing memory_full raises ValueError."""
        service = CompressionService()
        with pytest.raises(ValueError, match="memory_full is required"):
            service.render_prompt(memory_full=None, next_context="next")  # type: ignore
