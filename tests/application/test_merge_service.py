"""Tests for merge service."""

import pytest

from memory_distiller.application.merge_service import MergeService
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.llm.mock_client import MockClient


class TestMergeService:
    """Tests for MergeService."""

    def test_render_prompt_includes_validated_candidates(self) -> None:
        """Verify prompt contains validated_candidates."""
        service = MergeService()
        validated = "validated candidates content"
        prompt = service.render_prompt(
            existing_memory="existing",
            validated_candidates=validated,
        )
        assert validated in prompt

    def test_run_parses_memory_document(self) -> None:
        """Verify result has memory_document."""
        valid_text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence
"""
        service = MergeService()
        mock_client = MockClient(response=valid_text)
        result = service.run(
            existing_memory="",
            validated_candidates="some validated candidates",
            llm_client=mock_client,
        )
        assert result.prompt is not None
        assert result.raw_response == valid_text
        assert result.memory_document is not None
        assert len(result.memory_document.global_entries) == 1

    def test_malformed_memory_document_raises_parser_error(self) -> None:
        """Verify ParseErrorCollection for bad output."""
        service = MergeService()
        # Valid section header but wrong column count for entry
        invalid_text = """# MEMORY_FULL
## GLOBAL
G|RULE|H|D|Invalid entry with wrong column count
"""
        mock_client = MockClient(response=invalid_text)
        with pytest.raises(ParseErrorCollection):
            service.run(
                existing_memory="",
                validated_candidates="some validated candidates",
                llm_client=mock_client,
            )


class TestMergeServiceRenderPromptValidation:
    """Tests for render_prompt validation in MergeService."""

    def test_missing_validated_candidates_raises_value_error(self) -> None:
        """Missing validated_candidates raises ValueError."""
        service = MergeService()
        with pytest.raises(ValueError, match="validated_candidates is required"):
            service.render_prompt(
                existing_memory="existing",
                validated_candidates=None,  # type: ignore
            )
