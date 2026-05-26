"""Base protocol for LLM clients."""

from __future__ import annotations

from typing import Protocol


class LlmClient(Protocol):
    """Protocol defining the interface for LLM clients."""

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
