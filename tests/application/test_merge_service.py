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
        """Verify result has memory_document with parsed entries from merge plan."""
        # Valid merge plan text (not MEMORY_FULL format)
        valid_merge_plan = (
            "M1|APPLY_ADD|-|G|RULE|H|D|Prefer critical feedback."
            "|2026-05-27 Evidence.|New rule.\n"
            "M2|SKIP_DROP|-|T|FACT|L|T|Temp detail.|User said.|Temporary.\n"
        )
        service = MergeService()
        mock_client = MockClient(response=valid_merge_plan)
        result = service.run(
            existing_memory="",
            validated_candidates="some validated candidates",
            llm_client=mock_client,
        )
        assert result.prompt is not None
        assert result.raw_response == valid_merge_plan
        assert result.memory_document is not None
        # APPLY_ADD creates a global entry
        assert len(result.memory_document.global_entries) == 1
        assert result.memory_document.global_entries[0].statement == "Prefer critical feedback."
        # SKIP_DROP is ignored
        assert len(result.memory_document.temporary_entries) == 0

    def test_malformed_memory_document_raises_parser_error(self) -> None:
        """Verify ParseErrorCollection for bad output."""
        service = MergeService()
        # Invalid merge plan (wrong column count for merge plan = 10 columns required)
        invalid_text = """M1|APPLY_ADD|G|RULE|H|D|Invalid entry with wrong column count
"""
        mock_client = MockClient(response=invalid_text)
        with pytest.raises(ParseErrorCollection):
            service.run(
                existing_memory="",
                validated_candidates="some validated candidates",
                llm_client=mock_client,
            )

    def test_run_returns_memory_full_raw(self) -> None:
        """Verify result.memory_full_raw is populated and contains # MEMORY_FULL."""
        valid_merge_plan = "M1|APPLY_ADD|-|G|RULE|H|D|New global rule.|Evidence.|Reason.\n"
        service = MergeService()
        mock_client = MockClient(response=valid_merge_plan)
        result = service.run(
            existing_memory="",
            validated_candidates="some validated candidates",
            llm_client=mock_client,
        )
        assert result.memory_full_raw is not None
        assert "# MEMORY_FULL" in result.memory_full_raw


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
