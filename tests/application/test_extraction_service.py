"""Tests for extraction service."""

import pytest

from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.llm.mock_client import MockClient


class TestExtractionService:
    """Tests for ExtractionService."""

    def test_render_prompt_includes_inputs(self) -> None:
        """Verify prompt contains existing_memory and chat_log."""
        service = ExtractionService()
        existing = "existing memory content"
        chat = "chat content here"
        prompt = service.render_prompt(existing_memory=existing, chat_log=chat)
        assert existing in prompt
        assert chat in prompt

    def test_run_calls_mock_client(self) -> None:
        """Verify MockClient.complete is called, verify last_system_prompt and last_user_prompt."""
        service = ExtractionService()
        valid_text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
c1|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence|Reason 1."""
        mock_client = MockClient(response=valid_text)
        existing = "existing memory"
        chat = "chat log"
        service.run(
            existing_memory=existing,
            chat_log=chat,
            llm_client=mock_client,
        )
        assert mock_client.last_system_prompt is not None
        assert mock_client.last_user_prompt is not None
        assert existing in mock_client.last_user_prompt
        assert chat in mock_client.last_user_prompt

    def test_run_returns_parsed_candidates(self) -> None:
        """Verify result has prompt, raw_response, candidates list."""
        valid_text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
c1|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence|Reason 1."""
        service = ExtractionService()
        mock_client = MockClient(response=valid_text)
        result = service.run(
            existing_memory="",
            chat_log="some chat",
            llm_client=mock_client,
        )
        assert result.prompt is not None
        assert result.raw_response == valid_text
        assert len(result.candidates) == 1
        assert result.candidates[0].id == "c1"

    def test_run_invalid_response_raises_parser_error(self) -> None:
        """Verify ParseErrorCollection is raised for bad LLM output."""
        service = ExtractionService()
        invalid_text = "this is not valid candidate format"
        mock_client = MockClient(response=invalid_text)
        with pytest.raises(ParseErrorCollection):
            service.run(
                existing_memory="",
                chat_log="some chat",
                llm_client=mock_client,
            )


class TestExtractionServiceRenderPromptValidation:
    """Tests for render_prompt validation in ExtractionService."""

    def test_missing_chat_log_raises_value_error(self) -> None:
        """Missing chat_log raises ValueError."""
        service = ExtractionService()
        with pytest.raises(ValueError, match="chat_log is required"):
            service.render_prompt(existing_memory="existing", chat_log=None)  # type: ignore
