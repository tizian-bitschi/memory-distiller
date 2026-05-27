"""Mock LLM client for testing."""

from __future__ import annotations

from typing import Any

from memory_distiller.llm.config import LlmConfig
from memory_distiller.llm.errors import EmptyLlmResponseError


class MockClient:
    """Mock LLM client that returns a fixed response string."""

    def __init__(self, response: str = "", config: LlmConfig | None = None) -> None:
        """Initialize mock client.

        Args:
            response: Fixed response string to return.
            config: Optional configuration (not used but kept for interface).
        """
        self._response = response
        self._config = config if config is not None else LlmConfig()
        self._last_system_prompt: str | None = None
        self._last_user_prompt: str | None = None

    @property
    def last_system_prompt(self) -> str | None:
        """Get last system prompt passed to complete."""
        return self._last_system_prompt

    @property
    def last_user_prompt(self) -> str | None:
        """Get last user prompt passed to complete."""
        return self._last_user_prompt

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return fixed response.

        Args:
            system_prompt: System prompt (recorded but not used).
            user_prompt: User prompt (recorded but not used).

        Returns:
            Fixed response string.

        Raises:
            EmptyLlmResponseError: If response is empty string.
        """
        self._last_system_prompt = system_prompt
        self._last_user_prompt = user_prompt

        if self._response == "":
            msg = "Mock client returned empty response"
            raise EmptyLlmResponseError(msg)

        return self._response


class MockDeepSeekClient:
    """Mock DeepSeek client for testing without real API calls."""

    def __init__(self, config: LlmConfig | None = None) -> None:
        """Initialize mock client.

        Args:
            config: Optional configuration.
        """
        self._config = config if config is not None else LlmConfig()
        self._last_messages: list[dict[str, str]] | None = None
        self._last_kwargs: dict[str, Any] | None = None

    @property
    def last_messages(self) -> list[dict[str, str]] | None:
        """Get last messages passed to complete."""
        return self._last_messages

    @property
    def last_kwargs(self) -> dict[str, Any] | None:
        """Get last request kwargs."""
        return self._last_kwargs

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Record prompts and return empty string.

        Args:
            system_prompt: System prompt.
            user_prompt: User prompt.
        """
        self._last_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return ""
