"""Tests for pipeline service."""

from memory_distiller.application.pipeline_service import PipelineService


class TestPipelineService:
    """Tests for PipelineService."""

    def test_render_all_prompts_returns_extractor_prompt(self) -> None:
        """Verify bundle has extractor_prompt."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
        )
        assert bundle.extractor_prompt is not None
        assert "existing" in bundle.extractor_prompt
        assert "chat" in bundle.extractor_prompt

    def test_validator_prompt_none_when_candidates_missing(self) -> None:
        """Verify None when candidates is empty."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            candidates="",
        )
        assert bundle.validator_prompt is None

    def test_validator_prompt_present_when_candidates_provided(self) -> None:
        """Verify rendered when candidates given."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            candidates="some candidates",
        )
        assert bundle.validator_prompt is not None
        assert "some candidates" in bundle.validator_prompt

    def test_merger_prompt_none_when_validated_candidates_missing(self) -> None:
        """Verify None when validated_candidates is empty."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            validated_candidates="",
        )
        assert bundle.merger_prompt is None

    def test_merger_prompt_present_when_validated_candidates_provided(self) -> None:
        """Verify rendered when validated_candidates given."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            validated_candidates="some validated candidates",
        )
        assert bundle.merger_prompt is not None
        assert "some validated candidates" in bundle.merger_prompt

    def test_compressor_prompt_present_when_memory_full_provided(self) -> None:
        """Verify rendered when memory_full given."""
        service = PipelineService()
        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            memory_full="full memory content",
            next_context="next context",
        )
        assert bundle.compressor_prompt is not None
        assert "full memory content" in bundle.compressor_prompt
        assert "next context" in bundle.compressor_prompt
