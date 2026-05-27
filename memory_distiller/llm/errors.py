"""Custom errors for LLM package."""

from __future__ import annotations


class LlmError(Exception):
    """Base error class for LLM-related errors."""

    pass


class MissingApiKeyError(LlmError):
    """Raised when API key environment variable is not set."""

    pass


class EmptyLlmResponseError(LlmError):
    """Raised when LLM returns an empty response."""

    pass


class LlmProviderError(LlmError):
    """Raised when LLM provider returns an error."""

    pass
