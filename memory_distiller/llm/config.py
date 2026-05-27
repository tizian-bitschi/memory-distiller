"""Configuration dataclass for LLM clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmConfig:
    """Frozen configuration for LLM client."""

    provider: str = "deepseek"
    model: str = "deepseek-v4-pro"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    temperature: float = 0.2
    max_tokens: int | None = None
    thinking_enabled: bool = True
    reasoning_effort: str = "high"
    timeout_seconds: int = 120
