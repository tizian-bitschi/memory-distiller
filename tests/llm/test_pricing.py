"""Tests for pricing and cost estimation."""

from __future__ import annotations

from decimal import Decimal

from memory_distiller.llm.models import LlmUsage
from memory_distiller.llm.pricing import estimate_cost


class TestEstimateCost:
    def test_none_usage_returns_none(self) -> None:
        assert estimate_cost(None, "deepseek-v4-pro") is None

    def test_none_model_returns_none(self) -> None:
        usage = LlmUsage(prompt_tokens=100)
        assert estimate_cost(usage, None) is None

    def test_deepseek_v4_flash(self) -> None:
        usage = LlmUsage(
            prompt_cache_hit_tokens=1_000_000,
            prompt_cache_miss_tokens=1_000_000,
            completion_tokens=1_000_000,
        )
        cost = estimate_cost(usage, "deepseek-v4-flash")
        assert cost is not None
        assert cost.total_cost is not None
        assert cost.total_cost > Decimal("0")

    def test_deepseek_v4_pro(self) -> None:
        usage = LlmUsage(
            prompt_cache_hit_tokens=1_000_000,
            prompt_cache_miss_tokens=1_000_000,
            completion_tokens=1_000_000,
        )
        cost = estimate_cost(usage, "deepseek-v4-pro")
        assert cost is not None
        assert cost.total_cost is not None
        assert cost.total_cost > Decimal("0")

    def test_unsupported_model_returns_note(self) -> None:
        usage = LlmUsage(prompt_tokens=100)
        cost = estimate_cost(usage, "unknown-model")
        assert cost is not None
        assert "not configured" in (cost.note or "").lower()

    def test_fallback_cache_miss(self) -> None:
        usage = LlmUsage(prompt_tokens=1_000_000)
        cost = estimate_cost(usage, "deepseek-v4-flash")
        assert cost is not None
        assert cost.total_cost is not None
        assert "cache miss" in (cost.note or "").lower()

    def test_missing_tokens_treated_as_zero(self) -> None:
        usage = LlmUsage(
            prompt_cache_hit_tokens=100,
            prompt_cache_miss_tokens=None,
            completion_tokens=None,
        )
        cost = estimate_cost(usage, "deepseek-v4-flash")
        assert cost is not None
        assert cost.total_cost is not None
