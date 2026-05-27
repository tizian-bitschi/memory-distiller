"""DeepSeek LLM client implementation."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from memory_distiller.llm.config import LlmConfig
from memory_distiller.llm.errors import (
    EmptyLlmResponseError,
    LlmProviderError,
    MissingApiKeyError,
)

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
        return content
