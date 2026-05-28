"""DeepSeek LLM client implementation."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any

from openai import OpenAI

from memory_distiller.llm.config import LlmConfig
from memory_distiller.llm.errors import (
    EmptyLlmResponseError,
    LlmProviderError,
    MissingApiKeyError,
)
from memory_distiller.llm.models import (
    DeepSeekBalance,
    DeepSeekBalanceInfo,
    LlmResponse,
    LlmUsage,
)
from memory_distiller.llm.pricing import estimate_cost

# Models that are no longer supported
_DEPRECATED_MODELS = {"deepseek-chat", "deepseek-reasoner"}

# Valid models for this adapter
_VALID_MODELS = {"deepseek-v4-pro", "deepseek-v4-flash"}


class DeepSeekClient:
    """DeepSeek LLM client using OpenAI-compatible API."""

    def __init__(self, config: LlmConfig | None = None) -> None:
        """Initialize DeepSeek client.

        Args:
            config: LLM configuration. Uses defaults if not provided.

        Raises:
            MissingApiKeyError: If API key is not set in environment.
            ValueError: If model name is deprecated or invalid.
        """
        self._config = config if config is not None else LlmConfig()
        self._validate_model()
        self._api_key = self._get_api_key()
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=self._config.base_url,
            timeout=self._config.timeout_seconds,
        )

    def _validate_model(self) -> None:
        """Validate model name."""
        if self._config.model in _DEPRECATED_MODELS:
            msg = (
                f"Model '{self._config.model}' is deprecated. "
                f"Use 'deepseek-v4-pro' or 'deepseek-v4-flash' instead."
            )
            raise ValueError(msg)
        if self._config.model not in _VALID_MODELS:
            msg = (
                f"Model '{self._config.model}' is not supported. "
                f"Use 'deepseek-v4-pro' or 'deepseek-v4-flash'."
            )
            raise ValueError(msg)

    def _get_api_key(self) -> str:
        """Get API key from environment variable."""
        api_key = os.environ.get(self._config.api_key_env)
        if not api_key:
            msg = f"API key not found in environment variable '{self._config.api_key_env}'"
            raise MissingApiKeyError(msg)
        return api_key

    def _build_request_kwargs(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Build request kwargs for API call.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            Dictionary of kwargs for chat.completions.create.
        """
        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": self._config.temperature,
        }
        if self._config.max_tokens is not None:
            kwargs["max_tokens"] = self._config.max_tokens

        if self._config.thinking_enabled:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        if self._config.reasoning_effort is not None:
            kwargs["reasoning_effort"] = self._config.reasoning_effort

        return kwargs

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Generate completion from DeepSeek.

        Args:
            system_prompt: System prompt for context.
            user_prompt: User prompt/query.

        Returns:
            LLM response text content.

        Raises:
            MissingApiKeyError: If API key is not set.
            EmptyLlmResponseError: If response is empty.
            LlmProviderError: On provider errors.
        """
        return self.complete_with_usage(
            system_prompt=system_prompt, user_prompt=user_prompt
        ).content

    def complete_with_usage(self, *, system_prompt: str, user_prompt: str) -> LlmResponse:
        """Generate completion from DeepSeek with usage metadata.

        Args:
            system_prompt: System prompt for context.
            user_prompt: User prompt/query.

        Returns:
            LlmResponse with content, usage, cost estimate, and model.

        Raises:
            MissingApiKeyError: If API key is not set.
            EmptyLlmResponseError: If response is empty.
            LlmProviderError: On provider errors.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        kwargs = self._build_request_kwargs(messages)

        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            msg = f"DeepSeek API error: {exc}"
            raise LlmProviderError(msg) from exc

        content = response.choices[0].message.content
        if content is None or content == "":
            msg = "LLM returned empty response"
            raise EmptyLlmResponseError(msg)

        assert isinstance(content, str)

        usage = self._extract_usage(response)
        model = getattr(response, "model", None) or self._config.model
        cost = estimate_cost(usage, model)

        return LlmResponse(
            content=content,
            usage=usage,
            cost_estimate=cost,
            model=model,
        )

    def _extract_usage(self, response: Any) -> LlmUsage | None:
        """Safely extract usage from OpenAI response object."""
        usage_obj = getattr(response, "usage", None)
        if usage_obj is None:
            return None

        prompt_tokens = getattr(usage_obj, "prompt_tokens", None)
        completion_tokens = getattr(usage_obj, "completion_tokens", None)
        total_tokens = getattr(usage_obj, "total_tokens", None)

        prompt_cache_hit_tokens = getattr(usage_obj, "prompt_cache_hit_tokens", None)
        prompt_cache_miss_tokens = getattr(usage_obj, "prompt_cache_miss_tokens", None)

        reasoning_tokens = None
        completion_details = getattr(usage_obj, "completion_tokens_details", None)
        if completion_details is not None:
            reasoning_tokens = getattr(completion_details, "reasoning_tokens", None)

        # Only return LlmUsage if we have at least some token data
        if prompt_tokens is None and completion_tokens is None and total_tokens is None:
            return None

        return LlmUsage(
            prompt_tokens=prompt_tokens,
            prompt_cache_hit_tokens=prompt_cache_hit_tokens,
            prompt_cache_miss_tokens=prompt_cache_miss_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            total_tokens=total_tokens,
        )

    def get_balance(self) -> DeepSeekBalance:
        """Fetch DeepSeek account balance.

        Returns:
            DeepSeekBalance with account balance info.

        Raises:
            LlmProviderError: On HTTP/API/parsing errors.
        """
        url = f"{self._config.base_url}/user/balance"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self._api_key}"},
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            msg = f"DeepSeek balance HTTP error: {exc.code}"
            raise LlmProviderError(msg) from exc
        except urllib.error.URLError as exc:
            msg = f"DeepSeek balance connection error: {exc.reason}"
            raise LlmProviderError(msg) from exc
        except json.JSONDecodeError as exc:
            msg = f"DeepSeek balance invalid JSON: {exc}"
            raise LlmProviderError(msg) from exc
        except Exception as exc:
            msg = f"DeepSeek balance error: {exc}"
            raise LlmProviderError(msg) from exc

        return self._parse_balance(data)

    def _parse_balance(self, data: dict[str, Any]) -> DeepSeekBalance:
        """Parse balance JSON response."""
        try:
            is_available = data.get("is_available", False)
            raw_infos = data.get("balance_infos", [])
            infos = []
            for info in raw_infos:
                currency = info["currency"]
                total_balance = Decimal(str(info["total_balance"]))
                granted_balance = Decimal(str(info["granted_balance"]))
                topped_up_balance = Decimal(str(info["topped_up_balance"]))
                infos.append(
                    DeepSeekBalanceInfo(
                        currency=currency,
                        total_balance=total_balance,
                        granted_balance=granted_balance,
                        topped_up_balance=topped_up_balance,
                    )
                )
            return DeepSeekBalance(
                is_available=is_available,
                balance_infos=tuple(infos),
            )
        except (KeyError, TypeError, ValueError) as exc:
            msg = f"DeepSeek balance parse error: {exc}"
            raise LlmProviderError(msg) from exc
