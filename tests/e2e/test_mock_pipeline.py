"""End-to-end tests for the full pipeline with MockClient."""

from pathlib import Path

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.application.merge_service import MergeService
from memory_distiller.application.validation_service import ValidationService
from memory_distiller.io.candidate_parser import parse_candidates, parse_validated_candidates
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.llm.mock_client import MockClient

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def _load_example(filename: str) -> str:
    """Load an example file from the examples directory."""
    return (EXAMPLES_DIR / filename).read_text(encoding="utf-8")


class TestMockPipeline:
    """End-to-end tests using MockClient to simulate LLM responses."""

    def test_full_pipeline_with_mock_client(self) -> None:
        """Test complete pipeline: Extract -> Validate -> Merge -> Compress."""
        # Arrange - load all fixtures from examples/
        existing_memory = _load_example("memory_full_before.md")
        chat_log = _load_example("synthetic_chat_log.md")
        extractor_response = _load_example("extractor_candidates.txt")
        validator_response = _load_example("validated_candidates.txt")
        merger_response = _load_example("memory_full_after.md")
        compressor_response = _load_example("memory_prompt.md")

        # Act - Extract
        extractor = MockClient(response=extractor_response)
        extraction_result = ExtractionService().run(
            existing_memory=existing_memory,
            chat_log=chat_log,
            llm_client=extractor,
        )

        # Assert extraction
        assert len(extraction_result.candidates) == 8
        assert extraction_result.raw_response == extractor_response

        # Act - Validate
        validator = MockClient(response=validator_response)
        validation_result = ValidationService().run(
            existing_memory=existing_memory,
            chat_log=chat_log,
            candidates=extraction_result.raw_response,
            llm_client=validator,
        )

        # Assert validation
        assert len(validation_result.validated_candidates) == 8
        keep_count = sum(
            1 for c in validation_result.validated_candidates if c.verdict.value == "KEEP"
        )
        drop_count = sum(
            1 for c in validation_result.validated_candidates if c.verdict.value == "DROP"
        )
        assert keep_count == 5
        assert drop_count == 2
        edit_count = sum(
            1 for c in validation_result.validated_candidates if c.verdict.value == "EDIT"
        )
        assert edit_count == 1

        # Act - Merge
        merger = MockClient(response=merger_response)
        merge_result = MergeService().run(
            existing_memory=existing_memory,
            validated_candidates=validation_result.raw_response,
            llm_client=merger,
        )

        # Assert merge
        assert merge_result.memory_document is not None
        assert len(merge_result.memory_document.global_entries) == 2
        assert len(merge_result.memory_document.project_entries) == 5

        # Act - Compress
        compressor = MockClient(response=compressor_response)
        compression_result = CompressionService().run(
            memory_full=merge_result.raw_response,
            llm_client=compressor,
        )

        # Assert compression
        assert "# MEMORY_PROMPT" in compression_result.memory_prompt
        assert "Deutsch" in compression_result.memory_prompt
        assert "vegetarisch" in compression_result.memory_prompt

    def test_no_real_api_call_made(self) -> None:
        """Verify MockClient does not make real API calls."""
        existing_memory = _load_example("memory_full_before.md")
        chat_log = _load_example("synthetic_chat_log.md")
        extractor_response = _load_example("extractor_candidates.txt")

        extractor = MockClient(response=extractor_response)
        ExtractionService().run(
            existing_memory=existing_memory,
            chat_log=chat_log,
            llm_client=extractor,
        )

        assert extractor.last_system_prompt is not None
        assert extractor.last_user_prompt is not None


class TestExampleFilesParse:
    """Tests that verify example files parse correctly."""

    def test_example_memory_full_before_parses(self) -> None:
        """Load and parse examples/memory_full_before.md."""
        content = _load_example("memory_full_before.md")
        document = parse_memory_document(content)

        assert document is not None
        assert len(document.global_entries) == 1
        assert document.global_entries[0].statement == "Always provide concise answers."

    def test_example_memory_full_after_parses(self) -> None:
        """Load and parse examples/memory_full_after.md."""
        content = _load_example("memory_full_after.md")
        document = parse_memory_document(content)

        assert document is not None
        assert len(document.global_entries) == 2
        assert len(document.project_entries) == 5
        assert len(document.repo_entries) == 0
        assert len(document.temporary_entries) == 0
        assert len(document.deprecated_entries) == 0
        assert len(document.open_questions) == 0

    def test_example_extractor_candidates_parses(self) -> None:
        """Load and parse examples/extractor_candidates.txt."""
        content = _load_example("extractor_candidates.txt")
        candidates = parse_candidates(content)

        assert candidates is not None
        assert len(candidates) == 8
        assert candidates[0].id == "1"
        assert candidates[0].action.value == "ADD"

    def test_example_validated_candidates_parses(self) -> None:
        """Load and parse examples/validated_candidates.txt."""
        content = _load_example("validated_candidates.txt")
        validated = parse_validated_candidates(content)

        assert validated is not None
        assert len(validated) == 8
        assert validated[0].id == "1"
        assert validated[0].verdict.value == "KEEP"
