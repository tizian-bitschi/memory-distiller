"""DeepSeek pricing configuration and cost estimation."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from memory_distiller.llm.models import LlmCostEstimate, LlmUsage


# Pricing per 1 million tokens in USD
_PRICING: dict[str, dict[str, Decimal]] = {
    "deepseek-v4-flash": {
        "input_cache_hit_usd_per_1m": Decimal("0.0028"),
        "input_cache_miss_usd_per_1m": Decimal("0.14"),
        "output_usd_per_1m": Decimal("0.28"),
    },
    "deepseek-v4-pro": {
        "input_cache_hit_usd_per_1m": Decimal("0.003625"),
        "input_cache_miss_usd_per_1m": Decimal("0.435"),
        "output_usd_per_1m": Decimal("0.87"),
    },
}


_DEFAULT_NOTE = "Estimated from manually configured DeepSeek pricing; verify pricing regularly."


def estimate_cost(usage: LlmUsage | None, model: str | None) -> LlmCostEstimate | None:
    """Estimate cost from usage and model.

    Args:
        usage: Token usage metadata.
        model: Model name used for the call.

    Returns:
        LlmCostEstimate or None if model unsupported or usage missing.
    """
    from memory_distiller.llm.models import LlmCostEstimate

    if usage is None or model is None:
        return None

    pricing = _PRICING.get(model)
    if pricing is None:
        return LlmCostEstimate(
            note=f"Pricing not configured for model '{model}'.",
        )

    hit_tokens = usage.prompt_cache_hit_tokens or 0
    miss_tokens = usage.prompt_cache_miss_tokens or 0
    completion = usage.completion_tokens or 0

    # Fallback: if cache hit/miss both missing but prompt_tokens exists
    note: str | None = _DEFAULT_NOTE
    if usage.prompt_cache_hit_tokens is None and usage.prompt_cache_miss_tokens is None:
        if usage.prompt_tokens is not None:
            miss_tokens = usage.prompt_tokens
            note = (
                "Input cache split unavailable; prompt tokens treated as cache miss. "
                + _DEFAULT_NOTE
            )
        else:
            # No prompt token info at all
            return LlmCostEstimate(note=note)

    hit_price = pricing["input_cache_hit_usd_per_1m"]
    miss_price = pricing["input_cache_miss_usd_per_1m"]
    output_price = pricing["output_usd_per_1m"]

    hit_cost = Decimal(hit_tokens) * hit_price / Decimal(1_000_000)
    miss_cost = Decimal(miss_tokens) * miss_price / Decimal(1_000_000)
    output_cost = Decimal(completion) * output_price / Decimal(1_000_000)
    total = hit_cost + miss_cost + output_cost

    return LlmCostEstimate(
        input_cache_hit_cost=hit_cost.quantize(Decimal("0.00000001")),
        input_cache_miss_cost=miss_cost.quantize(Decimal("0.00000001")),
        output_cost=output_cost.quantize(Decimal("0.00000001")),
        total_cost=total.quantize(Decimal("0.00000001")),
        note=note,
    )
