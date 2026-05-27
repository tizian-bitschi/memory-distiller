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


class TestPipelineServiceUsesInjectedServices:
    """Tests verifying PipelineService delegates to injected services."""

    def test_uses_injected_service_instances(self) -> None:
        """Verify render_all_prompts delegates to injected services."""

        # Create fake services that record their calls
        class FakeExtractionService:
            def __init__(self):
                self.called_with = None

            def render_prompt(self, *, existing_memory, chat_log):
                self.called_with = {"existing_memory": existing_memory, "chat_log": chat_log}
                return "fake-extractor-prompt"

        class FakeValidationService:
            def __init__(self):
                self.called_with = None

            def render_prompt(self, *, existing_memory, chat_log, candidates):
                self.called_with = {
                    "existing_memory": existing_memory,
                    "chat_log": chat_log,
                    "candidates": candidates,
                }
                return "fake-validator-prompt"

        class FakeMergeService:
            def __init__(self):
                self.called_with = None

            def render_prompt(self, *, existing_memory, validated_candidates):
                self.called_with = {
                    "existing_memory": existing_memory,
                    "validated_candidates": validated_candidates,
                }
                return "fake-merger-prompt"

        class FakeCompressionService:
            def __init__(self):
                self.called_with = None

            def render_prompt(self, *, memory_full, next_context=""):
                self.called_with = {"memory_full": memory_full, "next_context": next_context}
                return "fake-compressor-prompt"

        fake_extractor = FakeExtractionService()
        fake_validator = FakeValidationService()
        fake_merger = FakeMergeService()
        fake_compressor = FakeCompressionService()

        service = PipelineService(
            extraction_service=fake_extractor,
            validation_service=fake_validator,
            merge_service=fake_merger,
            compression_service=fake_compressor,
        )

        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
            candidates="candidates",
            validated_candidates="validated",
            memory_full="memory",
            next_context="next",
        )

        assert bundle.extractor_prompt == "fake-extractor-prompt"
        assert fake_extractor.called_with == {"existing_memory": "existing", "chat_log": "chat"}

        assert bundle.validator_prompt == "fake-validator-prompt"
        assert fake_validator.called_with == {
            "existing_memory": "existing",
            "chat_log": "chat",
            "candidates": "candidates",
        }

        assert bundle.merger_prompt == "fake-merger-prompt"
        assert fake_merger.called_with == {
            "existing_memory": "existing",
            "validated_candidates": "validated",
        }

        assert bundle.compressor_prompt == "fake-compressor-prompt"
        assert fake_compressor.called_with == {"memory_full": "memory", "next_context": "next"}

    def test_skips_injected_services_when_inputs_empty(self) -> None:
        """Verify services not called when inputs are empty."""

        class FakeExtractionService:
            def render_prompt(self, *, existing_memory, chat_log):
                return "fake-extractor"

        class FakeValidationService:
            def __init__(self):
                self.called = False

            def render_prompt(self, *, existing_memory, chat_log, candidates):
                self.called = True
                return "fake-validator"

        fake_extractor = FakeExtractionService()
        fake_validator = FakeValidationService()

        service = PipelineService(
            extraction_service=fake_extractor,
            validation_service=fake_validator,
        )

        bundle = service.render_all_prompts(
            existing_memory="existing",
            chat_log="chat",
        )

        assert bundle.extractor_prompt == "fake-extractor"
        assert bundle.validator_prompt is None
        assert not fake_validator.called
