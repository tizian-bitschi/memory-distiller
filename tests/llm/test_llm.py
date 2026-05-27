"""Tests for LLM package."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from memory_distiller.llm import (
    DeepSeekClient,
    EmptyLlmResponseError,
    LlmConfig,
    LlmError,
    LlmProviderError,
    MissingApiKeyError,
    MockClient,
)


class TestLlmConfig:
    """Tests for LlmConfig dataclass."""

    def test_default_config_uses_deepseek_v4_pro(self) -> None:
        """Default config should use deepseek-v4-pro model."""
        config = LlmConfig()
        assert config.model == "deepseek-v4-pro"
        assert config.provider == "deepseek"
        assert config.base_url == "https://api.deepseek.com"
        assert config.temperature == 0.2

    def test_config_allows_deepseek_v4_flash(self) -> None:
        """Config should allow deepseek-v4-flash model."""
        config = LlmConfig(model="deepseek-v4-flash")
        assert config.model == "deepseek-v4-flash"

    def test_config_allows_custom_values(self) -> None:
        """Config should allow custom values for all fields."""
        config = LlmConfig(
            provider="custom",
            model="custom-model",
            base_url="https://custom.api.com",
            api_key_env="CUSTOM_API_KEY",
            temperature=0.5,
            max_tokens=1000,
            thinking_enabled=True,
            reasoning_effort="medium",
            timeout_seconds=30,
        )
        assert config.provider == "custom"
        assert config.model == "custom-model"
        assert config.temperature == 0.5
        assert config.thinking_enabled is True
        assert config.reasoning_effort == "medium"

    def test_default_thinking_enabled_is_true(self) -> None:
        """Default thinking_enabled should be True."""
        config = LlmConfig()
        assert config.thinking_enabled is True

    def test_default_reasoning_effort_is_high(self) -> None:
        """Default reasoning_effort should be 'high'."""
        config = LlmConfig()
        assert config.reasoning_effort == "high"

    def test_default_timeout_is_120(self) -> None:
        """Default timeout_seconds should be 120."""
        config = LlmConfig()
        assert config.timeout_seconds == 120


class TestDeprecatedModelRejection:
    """Tests for deprecated model name rejection."""

    def test_rejects_deepseek_chat(self) -> None:
        """Should reject deepseek-chat as deprecated."""
        config = LlmConfig(model="deepseek-chat")
        with pytest.raises(ValueError, match="deprecated"):
            DeepSeekClient(config)

    def test_rejects_deepseek_reasoner(self) -> None:
        """Should reject deepseek-reasoner as deprecated."""
        config = LlmConfig(model="deepseek-reasoner")
        with pytest.raises(ValueError, match="deprecated"):
            DeepSeekClient(config)

    def test_rejects_invalid_model(self) -> None:
        """Should reject invalid model names."""
        config = LlmConfig(model="invalid-model")
        with pytest.raises(ValueError, match="not supported"):
            DeepSeekClient(config)


class TestMissingApiKey:
    """Tests for missing API key handling."""

    def test_raises_missing_api_key_error(self) -> None:
        """Should raise MissingApiKeyError when API key not set."""
        env_vars_to_remove = ["DEEPSEEK_API_KEY"]
        original_values = {var: os.environ.get(var) for var in env_vars_to_remove}
        try:
            for var in env_vars_to_remove:
                os.environ.pop(var, None)
            config = LlmConfig()
            with pytest.raises(MissingApiKeyError):
                DeepSeekClient(config)
        finally:
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value


class TestMockClient:
    """Tests for MockClient."""

    def test_returns_fixed_response(self) -> None:
        """Should return the fixed response string."""
        client = MockClient(response="Hello, world!")
        result = client.complete(system_prompt="System", user_prompt="User")
        assert result == "Hello, world!"

    def test_records_prompts(self) -> None:
        """Should record the last prompts."""
        client = MockClient(response="Response")
        client.complete(system_prompt="System prompt", user_prompt="User prompt")
        assert client.last_system_prompt == "System prompt"
        assert client.last_user_prompt == "User prompt"

    def test_empty_response_raises_error(self) -> None:
        """Should raise EmptyLlmResponseError for empty response."""
        client = MockClient(response="")
        with pytest.raises(EmptyLlmResponseError):
            client.complete(system_prompt="System", user_prompt="User")


class TestDeepSeekClientInit:
    """Tests for DeepSeekClient initialization."""

    def test_client_does_not_call_api_on_init(self) -> None:
        """Client should be initializable without making API call."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            config = LlmConfig()
            client = DeepSeekClient(config)
            assert client is not None


class TestRequestKwargs:
    """Tests for request kwargs building."""

    def test_request_kwargs_contains_model(self) -> None:
        """Request kwargs should contain correct model."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(model="deepseek-v4-pro")
                client = DeepSeekClient(config)
                # Replace the client's chat.completions.create with mock
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert call_kwargs["model"] == "deepseek-v4-pro"

    def test_request_kwargs_contains_temperature(self) -> None:
        """Request kwargs should contain temperature."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(temperature=0.5)
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert call_kwargs["temperature"] == 0.5

    def test_request_kwargs_contains_messages(self) -> None:
        """Request kwargs should contain messages."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig()
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System prompt", user_prompt="User prompt")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                messages = call_kwargs["messages"]
                assert len(messages) == 2
                assert messages[0]["role"] == "system"
                assert messages[0]["content"] == "System prompt"
                assert messages[1]["role"] == "user"
                assert messages[1]["content"] == "User prompt"

    def test_thinking_enabled_adds_extra_body(self) -> None:
        """When thinking_enabled is True, extra_body should be added."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(thinking_enabled=True)
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert "extra_body" in call_kwargs
                assert call_kwargs["extra_body"] == {"thinking": {"type": "enabled"}}

    def test_reasoning_effort_adds_to_kwargs(self) -> None:
        """When reasoning_effort is set, it should be added to kwargs."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(reasoning_effort="high")
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert "reasoning_effort" in call_kwargs
                assert call_kwargs["reasoning_effort"] == "high"

    def test_base_url_used_from_config(self) -> None:
        """Client should use base_url from config."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(base_url="https://custom.api.com")
                client = DeepSeekClient(config)
                # The client stores the OpenAI instance internally
                assert client._client.base_url == "https://custom.api.com"

    def test_default_config_includes_reasoning_effort_high(self) -> None:
        """Default config should include reasoning_effort='high' in kwargs."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig()
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert call_kwargs["reasoning_effort"] == "high"

    def test_thinking_disabled_does_not_add_extra_body(self) -> None:
        """When thinking_enabled is False, extra_body should NOT be added."""
        mock_response = _create_mock_response("test")

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                config = LlmConfig(thinking_enabled=False)
                client = DeepSeekClient(config)
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                client.complete(system_prompt="System", user_prompt="User")

                call_kwargs = client._client.chat.completions.create.call_args[1]
                assert "extra_body" not in call_kwargs


class TestEmptyResponse:
    """Tests for empty response handling."""

    def test_empty_mocked_response_raises_error(self) -> None:
        """Empty mocked response should raise EmptyLlmResponseError."""
        mock_response = _create_mock_response(None)

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            with patch("openai.OpenAI"):
                client = DeepSeekClient(LlmConfig())
                client._client.chat.completions.create = MagicMock(return_value=mock_response)

                with pytest.raises(EmptyLlmResponseError):
                    client.complete(system_prompt="System", user_prompt="User")


class TestLlmErrorHierarchy:
    """Tests for error class hierarchy."""

    def test_llm_error_is_base_class(self) -> None:
        """LlmError should be base class for all custom errors."""
        assert issubclass(MissingApiKeyError, LlmError)
        assert issubclass(EmptyLlmResponseError, LlmError)
        assert issubclass(LlmProviderError, LlmError)


def _create_mock_response(content: str | None) -> Any:
    """Helper to create a mock response object."""
    mock_message = _create_mock_message(content)
    mock_choice = _create_mock_choice(mock_message)
    mock_response = _create_mock_completion_response([mock_choice])
    return mock_response


def _create_mock_message(content: str | None) -> Any:
    """Helper to create a mock message object."""
    mock_message = type("MockMessage", (), {})()
    mock_message.content = content
    return mock_message


def _create_mock_choice(message: Any) -> Any:
    """Helper to create a mock choice object."""
    mock_choice = type("MockChoice", (), {})()
    mock_choice.message = message
    return mock_choice


def _create_mock_completion_response(choices: list[Any]) -> Any:
    """Helper to create a mock completion response."""
    mock_response = type("MockResponse", (), {})()
    mock_response.choices = choices
    return mock_response


@pytest.mark.integration_llm
class TestIntegrationDeepSeek:
    """Integration tests for real DeepSeek API - skipped by default."""

    def test_real_api_call(self) -> None:
        """Test against real DeepSeek API - only runs with DEEPSEEK_API_KEY set."""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set")

        config = LlmConfig(model="deepseek-v4-flash")
        client = DeepSeekClient(config)
        result = client.complete(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'hello' in one word.",
        )
        assert isinstance(result, str)
        assert len(result) > 0
