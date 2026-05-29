"""Tests that application services preserve usage/cost metadata."""

from __future__ import annotations

from decimal import Decimal

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.application.merge_service import MergeService
from memory_distiller.application.validation_service import ValidationService
from memory_distiller.llm.mock_client import MockClient
from memory_distiller.llm.models import LlmCostEstimate, LlmUsage


class TestExtractionServiceUsage:
    def test_run_preserves_usage_from_mock_client(self) -> None:
        usage = LlmUsage(prompt_tokens=100, completion_tokens=200)
        cost = LlmCostEstimate(total_cost=Decimal("0.001"))
        response_text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
c1|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence|Reason 1."""
        client = MockClient(
            response=response_text,
            usage=usage,
            cost_estimate=cost,
            model="deepseek-v4-pro",
        )
        service = ExtractionService()
        result = service.run(
            existing_memory="",
            chat_log="test chat",
            llm_client=client,
        )
        assert result.usage == usage
        assert result.cost_estimate == cost
        assert result.model == "deepseek-v4-pro"

    def test_run_fallback_without_complete_with_usage(self) -> None:
        """Test that services work with clients that only have complete()."""
        response_text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
c1|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence|Reason 1."""

        class MinimalClient:
            def complete(self, *, system_prompt: str, user_prompt: str) -> str:
                return response_text

        client = MinimalClient()
        service = ExtractionService()
        result = service.run(
            existing_memory="",
            chat_log="test chat",
            llm_client=client,
        )
        assert result.raw_response is not None
        assert result.usage is None
        assert result.cost_estimate is None
        assert result.model is None


class TestValidationServiceUsage:
    def test_run_preserves_usage(self) -> None:
        usage = LlmUsage(prompt_tokens=50, completion_tokens=100)
        response_text = (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "v1|KEEP|ADD|prefer-critical|G|RULE|H|D|Prefer critical feedback."
            "|2026-05-27 Evidence|Reason 1."
        )
        client = MockClient(
            response=response_text,
            usage=usage,
            model="deepseek-v4-flash",
        )
        service = ValidationService()
        result = service.run(
            existing_memory="",
            chat_log="test",
            candidates="test",
            llm_client=client,
        )
        assert result.usage == usage
        assert result.model == "deepseek-v4-flash"


class TestMergeServiceUsage:
    def test_run_preserves_usage(self) -> None:
        usage = LlmUsage(prompt_tokens=200, completion_tokens=300)
        client = MockClient(
            response=(
                "# GLOBAL\n- test\n# PROJECT\n\n# REPO\n\n# TEMPORARY\n\n"
                "# DEPRECATED\n\n# OPEN_QUESTIONS\n"
            ),
            usage=usage,
        )
        service = MergeService()
        result = service.run(
            existing_memory="",
            validated_candidates="test",
            llm_client=client,
        )
        assert result.usage == usage


class TestCompressionServiceUsage:
    def test_run_preserves_usage(self) -> None:
        usage = LlmUsage(prompt_tokens=150, completion_tokens=250)
        client = MockClient(
            response="# MEMORY_PROMPT\ntest memory",
            usage=usage,
        )
        service = CompressionService()
        result = service.run(
            memory_full="test",
            llm_client=client,
        )
        assert result.usage == usage
