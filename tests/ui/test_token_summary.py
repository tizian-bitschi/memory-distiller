"""Tests for render_token_summary() and _compute_request_tokens() - Issue #38."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pytest

from memory_distiller.llm.models import LlmUsage
from memory_distiller.ui.components import (
    _compute_request_tokens,
    estimate_tokens,
    render_token_summary,
)


class TestComputeRequestTokens:
    """Tests for _compute_request_tokens function."""

    def test_both_none_returns_none(self) -> None:
        """Both None inputs returns None."""
        result = _compute_request_tokens(None, None)
        assert result is None

    def test_system_only_returns_estimate(self) -> None:
        """System prompt only returns estimate_tokens(system)."""
        system = "system prompt text"
        result = _compute_request_tokens(system, None)
        assert result == estimate_tokens(system)

    def test_rendered_only_returns_estimate(self) -> None:
        """Rendered prompt only returns estimate_tokens(rendered)."""
        rendered = "rendered prompt text"
        result = _compute_request_tokens(None, rendered)
        assert result == estimate_tokens(rendered)

    def test_both_returns_sum(self) -> None:
        """Both system and rendered returns sum of estimates."""
        system = "system"
        rendered = "rendered"
        expected = estimate_tokens(system) + estimate_tokens(rendered)
        result = _compute_request_tokens(system, rendered)
        assert result == expected


class TestRenderTokenSummarySourceInspection:
    """Source inspection tests for render_token_summary - verifies expected patterns exist."""

    def test_source_contains_system_prompt_tokens_label(self) -> None:
        """Source contains 'Estimated system prompt tokens'."""
        source = inspect.getsource(render_token_summary)
        assert "Estimated system prompt tokens" in source

    def test_source_contains_rendered_prompt_tokens_label(self) -> None:
        """Source contains 'Estimated rendered prompt tokens'."""
        source = inspect.getsource(render_token_summary)
        assert "Estimated rendered prompt tokens" in source

    def test_source_contains_request_tokens_label(self) -> None:
        """Source contains 'Estimated request tokens'."""
        source = inspect.getsource(render_token_summary)
        assert "Estimated request tokens" in source

    def test_source_contains_response_tokens_label(self) -> None:
        """Source contains 'Estimated response tokens'."""
        source = inspect.getsource(render_token_summary)
        assert "Estimated response tokens" in source

    def test_source_contains_provider_usage_label(self) -> None:
        """Source contains 'Provider-reported usage'."""
        source = inspect.getsource(render_token_summary)
        assert "Provider-reported usage" in source

    def test_source_contains_delta_label(self) -> None:
        """Source contains 'Delta' for provider comparison."""
        source = inspect.getsource(render_token_summary)
        assert "Delta" in source


class TestRenderTokenSummaryEmptyCall:
    """Tests for empty call behavior - returns early without expander."""

    def test_empty_call_returns_early(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Called with no args, function returns early without creating expander."""
        calls: list[str] = []

        def mock_expander(label: str):
            def inner():
                calls.append(label)

            return inner

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary("Test")

        assert "🔍 Test Token Summary" not in calls


class TestRenderTokenSummarySystemPromptOnly:
    """Tests for system_prompt only call."""

    def test_system_prompt_only_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Call with system_prompt only creates expander with correct label."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary("Test", system_prompt="test system prompt")

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]


class TestRenderTokenSummaryRenderedPromptOnly:
    """Tests for rendered_prompt only call."""

    def test_rendered_prompt_only_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Call with rendered_prompt only creates expander with correct label."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary("Test", rendered_prompt="test rendered prompt")

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]


class TestRenderTokenSummarySystemPlusRendered:
    """Tests for system + rendered prompt call."""

    def test_system_plus_rendered_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Call with both system and rendered creates expander."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary("Test", system_prompt="system", rendered_prompt="rendered")

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]


class TestRenderTokenSummaryRawResponse:
    """Tests for raw_response call."""

    def test_raw_response_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Call with raw_response creates expander."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary("Test", raw_response="test response content")

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]


class TestRenderTokenSummaryProviderUsage:
    """Tests for provider_usage call."""

    def test_provider_usage_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Call with provider_usage creates expander with metrics."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            context.metric = MagicMock()
            context.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        usage = LlmUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        render_token_summary("Test", provider_usage=usage)

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]


class TestRenderTokenSummaryDelta:
    """Tests for delta display when both request tokens and provider_usage available."""

    def test_delta_creates_expander(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Delta shown when both estimated request and provider prompt_tokens exist."""
        expander_calls = []

        def mock_expander(label):
            expander_calls.append(label)
            context = MagicMock()
            context.__enter__ = MagicMock(return_value=context)
            context.__exit__ = MagicMock()
            context.write = MagicMock()
            context.metric = MagicMock()
            context.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
            return context

        mock_st = MagicMock()
        mock_st.expander = mock_expander
        monkeypatch.setattr("memory_distiller.ui.components.st", mock_st)

        render_token_summary(
            "Test",
            system_prompt="system prompt for delta test",
            rendered_prompt="rendered prompt for delta test",
            provider_usage=LlmUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )

        assert len(expander_calls) == 1
        assert "🔍 Test Token Summary" in expander_calls[0]
