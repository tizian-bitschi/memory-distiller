"""Tests for usage display helpers."""

from __future__ import annotations

from decimal import Decimal

from memory_distiller.llm.models import LlmCostEstimate, LlmUsage
from memory_distiller.ui.components import (
    aggregate_cost,
    aggregate_usage,
    format_cost,
    format_token_count,
)


class TestFormatTokenCount:
    def test_none_returns_dash(self) -> None:
        assert format_token_count(None) == "—"

    def test_zero(self) -> None:
        assert format_token_count(0) == "0"

    def test_with_commas(self) -> None:
        assert format_token_count(1000) == "1,000"

    def test_large_number(self) -> None:
        assert format_token_count(1234567) == "1,234,567"


class TestFormatCost:
    def test_none_returns_dash(self) -> None:
        assert format_cost(None) == "—"

    def test_zero(self) -> None:
        assert format_cost(Decimal("0")) == "$0.00000000"

    def test_small_cost(self) -> None:
        assert "$" in format_cost(Decimal("0.0001"))


class TestAggregateUsage:
    def test_empty_list(self) -> None:
        result = aggregate_usage([])
        assert result.prompt_tokens is None
        assert result.total_tokens is None

    def test_single_usage(self) -> None:
        usage = LlmUsage(prompt_tokens=100, completion_tokens=200)
        result = aggregate_usage([usage])
        assert result.prompt_tokens == 100
        assert result.completion_tokens == 200

    def test_multiple_usages(self) -> None:
        usages = [
            LlmUsage(prompt_tokens=100, completion_tokens=200),
            LlmUsage(prompt_tokens=50, completion_tokens=100),
        ]
        result = aggregate_usage(usages)
        assert result.prompt_tokens == 150
        assert result.completion_tokens == 300

    def test_partial_usages(self) -> None:
        usages = [
            LlmUsage(prompt_tokens=100),
            LlmUsage(completion_tokens=200),
        ]
        result = aggregate_usage(usages)
        assert result.prompt_tokens == 100
        assert result.completion_tokens == 200
        assert result.total_tokens is None

    def test_with_cache_and_reasoning(self) -> None:
        usages = [
            LlmUsage(
                prompt_cache_hit_tokens=50,
                prompt_cache_miss_tokens=50,
                reasoning_tokens=100,
            ),
            LlmUsage(
                prompt_cache_hit_tokens=25,
                prompt_cache_miss_tokens=25,
                reasoning_tokens=50,
            ),
        ]
        result = aggregate_usage(usages)
        assert result.prompt_cache_hit_tokens == 75
        assert result.prompt_cache_miss_tokens == 75
        assert result.reasoning_tokens == 150


class TestAggregateCost:
    def test_empty_list(self) -> None:
        assert aggregate_cost([]) is None

    def test_all_none(self) -> None:
        assert aggregate_cost([None, None]) is None

    def test_single_cost(self) -> None:
        cost = LlmCostEstimate(total_cost=Decimal("0.001"))
        assert aggregate_cost([cost]) == Decimal("0.001")

    def test_multiple_costs(self) -> None:
        costs = [
            LlmCostEstimate(total_cost=Decimal("0.001")),
            LlmCostEstimate(total_cost=Decimal("0.002")),
        ]
        result = aggregate_cost(costs)
        assert result == Decimal("0.003")

    def test_skips_none(self) -> None:
        costs = [
            None,
            LlmCostEstimate(total_cost=Decimal("0.001")),
            None,
        ]
        assert aggregate_cost(costs) == Decimal("0.001")

    def test_skips_missing_total_cost(self) -> None:
        costs = [
            LlmCostEstimate(),
            LlmCostEstimate(total_cost=Decimal("0.001")),
        ]
        assert aggregate_cost(costs) == Decimal("0.001")
