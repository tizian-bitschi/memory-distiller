"""Tests for validation service."""

import pytest

from memory_distiller.application.validation_service import ValidationService
from memory_distiller.llm.mock_client import MockClient


class TestValidationService:
    """Tests for ValidationService."""

    def test_render_prompt_includes_candidates(self) -> None:
        """Verify prompt contains candidates."""
        service = ValidationService()
        candidates = "candidate content here"
        prompt = service.render_prompt(
            existing_memory="existing",
            chat_log="chat",
            candidates=candidates,
        )
        assert candidates in prompt

    def test_run_returns_parsed_validated_candidates(self) -> None:
        """Verify result has validated_candidates."""
        valid_text = """ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
v1|KEEP|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence|Reason 1."""
        service = ValidationService()
        mock_client = MockClient(response=valid_text)
        result = service.run(
            existing_memory="",
            chat_log="chat",
            candidates="some candidates",
            llm_client=mock_client,
        )
        assert result.prompt is not None
        assert result.raw_response == valid_text
        assert len(result.validated_candidates) == 1
        assert result.validated_candidates[0].id == "v1"

    def test_missing_candidates_raises_value_error(self) -> None:
        """Verify ValueError when candidates missing."""
        service = ValidationService()
        with pytest.raises(ValueError, match="candidates is required"):
            service.render_prompt(
                existing_memory="existing",
                chat_log="chat",
                candidates=None,  # type: ignore
            )


class TestValidationServiceRunValidation:
    """Tests for run method validation in ValidationService."""

    def test_missing_candidates_in_run_raises_value_error(self) -> None:
        """Missing candidates in run raises ValueError."""
        service = ValidationService()
        mock_client = MockClient(response="some response")
        with pytest.raises(ValueError, match="candidates is required"):
            service.run(
                existing_memory="",
                chat_log="chat",
                candidates=None,  # type: ignore
                llm_client=mock_client,
            )
