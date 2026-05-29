"""Base protocol for LLM clients."""

from __future__ import annotations

from typing import Protocol

from memory_distiller.llm.models import LlmResponse


class LlmClient(Protocol):
    """Protocol defining the minimal interface for LLM clients."""

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Generate completion from LLM.

        Args:
            system_prompt: System prompt for context.
            user_prompt: User prompt/query.

        Returns:
            LLM response text content.

        Raises:
            LlmError: On errors.
        """
        ...


class UsageAwareLlmClient(LlmClient, Protocol):
    """Protocol for LLM clients that support usage metadata."""

    def complete_with_usage(self, *, system_prompt: str, user_prompt: str) -> LlmResponse:
        """Generate completion from LLM with usage metadata.

        Args:
            system_prompt: System prompt for context.
            user_prompt: User prompt/query.

        Returns:
            LlmResponse with content, usage, cost estimate, and model.

        Raises:
            LlmError: On errors.
        """
        ...
