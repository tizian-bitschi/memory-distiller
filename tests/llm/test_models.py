"""Tests for LLM usage, cost, and response models."""

from __future__ import annotations

from decimal import Decimal

import pytest

from memory_distiller.llm.models import (
    DeepSeekBalance,
    DeepSeekBalanceInfo,
    LlmCostEstimate,
    LlmResponse,
    LlmUsage,
)


class TestLlmUsage:
    def test_default_values(self) -> None:
        usage = LlmUsage()
        assert usage.prompt_tokens is None
        assert usage.prompt_cache_hit_tokens is None
        assert usage.prompt_cache_miss_tokens is None
        assert usage.completion_tokens is None
        assert usage.reasoning_tokens is None
        assert usage.total_tokens is None

    def test_with_values(self) -> None:
        usage = LlmUsage(
            prompt_tokens=100,
            prompt_cache_hit_tokens=50,
            prompt_cache_miss_tokens=50,
            completion_tokens=200,
            reasoning_tokens=150,
            total_tokens=300,
        )
        assert usage.prompt_tokens == 100
        assert usage.prompt_cache_hit_tokens == 50
        assert usage.prompt_cache_miss_tokens == 50
        assert usage.completion_tokens == 200
        assert usage.reasoning_tokens == 150
        assert usage.total_tokens == 300

    def test_frozen(self) -> None:
        usage = LlmUsage(prompt_tokens=100)
        with pytest.raises(AttributeError):
            usage.prompt_tokens = 200  # type: ignore[misc]


class TestLlmCostEstimate:
    def test_default_values(self) -> None:
        cost = LlmCostEstimate()
        assert cost.currency == "USD"
        assert cost.input_cache_hit_cost is None
        assert cost.input_cache_miss_cost is None
        assert cost.output_cost is None
        assert cost.total_cost is None
        assert cost.pricing_source == "configured"
        assert cost.note is None

    def test_with_decimal_values(self) -> None:
        cost = LlmCostEstimate(
            input_cache_hit_cost=Decimal("0.0001"),
            input_cache_miss_cost=Decimal("0.001"),
            output_cost=Decimal("0.002"),
            total_cost=Decimal("0.0031"),
        )
        assert cost.input_cache_hit_cost == Decimal("0.0001")
        assert cost.total_cost == Decimal("0.0031")


class TestLlmResponse:
    def test_minimal(self) -> None:
        response = LlmResponse(content="hello")
        assert response.content == "hello"
        assert response.usage is None
        assert response.cost_estimate is None
        assert response.model is None

    def test_full(self) -> None:
        usage = LlmUsage(prompt_tokens=100, completion_tokens=200)
        cost = LlmCostEstimate(total_cost=Decimal("0.001"))
        response = LlmResponse(
            content="hello",
            usage=usage,
            cost_estimate=cost,
            model="deepseek-v4-pro",
        )
        assert response.usage == usage
        assert response.cost_estimate == cost
        assert response.model == "deepseek-v4-pro"


class TestDeepSeekBalanceInfo:
    def test_creation(self) -> None:
        info = DeepSeekBalanceInfo(
            currency="USD",
            total_balance=Decimal("10.50"),
            granted_balance=Decimal("5.00"),
            topped_up_balance=Decimal("5.50"),
        )
        assert info.currency == "USD"
        assert info.total_balance == Decimal("10.50")


class TestDeepSeekBalance:
    def test_creation(self) -> None:
        info = DeepSeekBalanceInfo(
            currency="USD",
            total_balance=Decimal("10.50"),
            granted_balance=Decimal("5.00"),
            topped_up_balance=Decimal("5.50"),
        )
        balance = DeepSeekBalance(
            is_available=True,
            balance_infos=(info,),
        )
        assert balance.is_available is True
        assert len(balance.balance_infos) == 1
