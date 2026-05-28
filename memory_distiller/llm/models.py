"""LLM usage, cost, and response models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LlmUsage:
    """Token usage from an LLM API call."""

    prompt_tokens: int | None = None
    prompt_cache_hit_tokens: int | None = None
    prompt_cache_miss_tokens: int | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class LlmCostEstimate:
    """Estimated cost for an LLM API call."""

    currency: str = "USD"
    input_cache_hit_cost: Decimal | None = None
    input_cache_miss_cost: Decimal | None = None
    output_cost: Decimal | None = None
    total_cost: Decimal | None = None
    pricing_source: str = "configured"
    note: str | None = None


@dataclass(frozen=True)
class LlmResponse:
    """Full LLM response including content and usage metadata."""

    content: str
    usage: LlmUsage | None = None
    cost_estimate: LlmCostEstimate | None = None
    model: str | None = None


@dataclass(frozen=True)
class DeepSeekBalanceInfo:
    """Balance info for a specific currency."""

    currency: str
    total_balance: Decimal
    granted_balance: Decimal
    topped_up_balance: Decimal


@dataclass(frozen=True)
class DeepSeekBalance:
    """DeepSeek account balance response."""

    is_available: bool
    balance_infos: tuple[DeepSeekBalanceInfo, ...]
