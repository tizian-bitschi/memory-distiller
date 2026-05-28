"""Tests for usage extraction from LLM responses."""

from __future__ import annotations

from types import SimpleNamespace

from memory_distiller.llm.deepseek_client import DeepSeekClient


class TestExtractUsage:
    def test_none_usage(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        response = SimpleNamespace()
        result = client._extract_usage(response)
        assert result is None

    def test_full_usage(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        usage = SimpleNamespace(
            prompt_tokens=100,
            prompt_cache_hit_tokens=50,
            prompt_cache_miss_tokens=50,
            completion_tokens=200,
            total_tokens=300,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=150),
        )
        response = SimpleNamespace(usage=usage)
        result = client._extract_usage(response)
        assert result is not None
        assert result.prompt_tokens == 100
        assert result.prompt_cache_hit_tokens == 50
        assert result.prompt_cache_miss_tokens == 50
        assert result.completion_tokens == 200
        assert result.reasoning_tokens == 150
        assert result.total_tokens == 300

    def test_partial_usage(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        usage = SimpleNamespace(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )
        response = SimpleNamespace(usage=usage)
        result = client._extract_usage(response)
        assert result is not None
        assert result.prompt_tokens == 100
        assert result.prompt_cache_hit_tokens is None
        assert result.reasoning_tokens is None

    def test_no_token_data(self) -> None:
        client = DeepSeekClient.__new__(DeepSeekClient)
        usage = SimpleNamespace()
        response = SimpleNamespace(usage=usage)
        result = client._extract_usage(response)
        assert result is None
