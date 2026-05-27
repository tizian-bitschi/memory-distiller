"""End-to-end tests for the full pipeline with MockClient."""

# ruff: noqa: E501

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.application.merge_service import MergeService
from memory_distiller.application.validation_service import ValidationService
from memory_distiller.llm.mock_client import MockClient

# Exact fixture content from examples/
EXTRACTOR_RESPONSE = """ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
1|ADD|-|G|PREF|H|D|Answer in German.|User explicitly stated preference|Direct user instruction
2|ADD|-|P:RecipeBot|RULE|H|D|Keep all recipes vegetarian.|User explicitly requested vegetarian recipes|Direct user instruction
3|ADD|-|P:RecipeBot|PREF|H|D|Use metric units for measurements.|User rejected imperial units|Direct user instruction
4|ADD|-|P:RecipeBot|DECISION|H|D|Use Streamlit for the UI.|User agreed to assistant suggestion|Explicit user confirmation
5|ADD|-|P:RecipeBot|AVOID|H|D|Flag recipes containing peanuts clearly.|User mentioned peanut allergy|Safety-critical user need
6|ADD|-|P:RecipeBot|DECISION|H|D|Store recipes as Markdown files.|User explicitly chose Markdown over database|Direct user choice
7|IGNORE|-|P:RecipeBot|PREF|L|T|Prefer dark mode UI.|Assistant suggested, user deferred|Not explicitly accepted yet
8|IGNORE|-|T|TASK|H|T|Complete basic features by next Friday.|Temporary deadline|Time-bound, not persistent memory"""

VALIDATOR_RESPONSE = """ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
1|KEEP|ADD|-|G|PREF|H|D|Answer in German.|User explicitly stated preference|Valid global preference
2|KEEP|ADD|-|P:RecipeBot|RULE|H|D|Keep all recipes vegetarian.|User explicitly requested vegetarian recipes|Valid project rule
3|KEEP|ADD|-|P:RecipeBot|PREF|H|D|Use metric units for measurements.|User rejected imperial units|Valid project preference
4|KEEP|ADD|-|P:RecipeBot|DECISION|H|D|Use Streamlit for the UI.|User agreed to assistant suggestion|Valid confirmed decision
5|KEEP|ADD|-|P:RecipeBot|AVOID|H|D|Flag recipes containing peanuts clearly.|User mentioned peanut allergy|Valid safety rule
6|EDIT|ADD|-|P:RecipeBot|DECISION|H|D|Store recipes as Markdown files in the project repository.|User explicitly chose Markdown over database|Clarified storage location
7|DROP|IGNORE|-|P:RecipeBot|PREF|L|T|Prefer dark mode UI.|Assistant suggested, user deferred|Not explicitly accepted, too tentative
8|DROP|IGNORE|-|T|TASK|H|T|Complete basic features by next Friday.|Temporary deadline|Temporary constraint, not permanent memory"""

MERGE_RESPONSE = """# MEMORY_FULL

## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Always provide concise answers.|Previous chat
G|PREF|H|D|Answer in German.|RecipeBot chat 2026-05-27

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:RecipeBot|RULE|H|D|Keep all recipes vegetarian.|RecipeBot chat 2026-05-27
P:RecipeBot|PREF|H|D|Use metric units for measurements.|RecipeBot chat 2026-05-27
P:RecipeBot|DECISION|H|D|Use Streamlit for the UI.|RecipeBot chat 2026-05-27
P:RecipeBot|AVOID|H|D|Flag recipes containing peanuts clearly.|RecipeBot chat 2026-05-27
P:RecipeBot|DECISION|H|D|Store recipes as Markdown files in the project repository.|RecipeBot chat 2026-05-27

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS"""

COMPRESSION_RESPONSE = """# MEMORY_PROMPT

Beachte dauerhaft:
- Antworte auf Deutsch.
- Halte Antworten prägnant.

Projektkontext RecipeBot:
- Alle Rezepte müssen vegetarisch sein.
- Nutze metrische Einheiten.
- Verwende Streamlit für das UI.
- Speichere Rezepte als Markdown-Dateien im Repository.
- Kennzeichne Rezepte mit Erdnüssen deutlich."""


class TestMockPipeline:
    """End-to-end tests using MockClient to simulate LLM responses."""

    def test_full_pipeline_with_mock_client(self) -> None:
        """Test complete pipeline: Extract -> Validate -> Merge -> Compress."""
        # Arrange
        existing_memory = """# MEMORY_FULL

## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Always provide concise answers.|Previous chat"""
        chat_log = "User wants RecipeBot..."

        # Act - Extract
        extractor = MockClient(response=EXTRACTOR_RESPONSE)
        extraction_result = ExtractionService().run(
            existing_memory=existing_memory,
            chat_log=chat_log,
            llm_client=extractor,
        )

        # Assert extraction
        assert len(extraction_result.candidates) == 8
        assert extraction_result.raw_response == EXTRACTOR_RESPONSE

        # Act - Validate
        validator = MockClient(response=VALIDATOR_RESPONSE)
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
        # EDIT verdict counts as KEEP (but modifies the entry)
        edit_count = sum(
            1 for c in validation_result.validated_candidates if c.verdict.value == "EDIT"
        )
        assert edit_count == 1

        # Act - Merge
        merger = MockClient(response=MERGE_RESPONSE)
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
        compressor = MockClient(response=COMPRESSION_RESPONSE)
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
        existing_memory = "# MEMORY_FULL\n\n## GLOBAL\nSCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE\nG|RULE|H|D|Always provide concise answers.|Previous chat"
        chat_log = "User wants RecipeBot..."

        # All services use MockClient - no real API calls
        extractor = MockClient(response=EXTRACTOR_RESPONSE)
        ExtractionService().run(
            existing_memory=existing_memory,
            chat_log=chat_log,
            llm_client=extractor,
        )

        # Verify MockClient recorded the prompts but didn't make HTTP calls
        assert extractor.last_system_prompt is not None
        assert extractor.last_user_prompt is not None
        # MockClient just records; real clients would make network calls


class TestExampleFilesParse:
    """Tests that verify example files parse correctly."""

    def test_example_memory_full_before_parses(self) -> None:
        """Load and parse examples/memory_full_before.md."""
        from pathlib import Path

        from memory_distiller.io.memory_parser import parse_memory_document

        example_path = Path(__file__).parent.parent.parent / "examples" / "memory_full_before.md"
        content = example_path.read_text(encoding="utf-8")
        document = parse_memory_document(content)

        assert document is not None
        assert len(document.global_entries) == 1
        assert document.global_entries[0].statement == "Always provide concise answers."

    def test_example_memory_full_after_parses(self) -> None:
        """Load and parse examples/memory_full_after.md."""
        from pathlib import Path

        from memory_distiller.io.memory_parser import parse_memory_document

        example_path = Path(__file__).parent.parent.parent / "examples" / "memory_full_after.md"
        content = example_path.read_text(encoding="utf-8")
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
        from pathlib import Path

        from memory_distiller.io.candidate_parser import parse_candidates

        example_path = Path(__file__).parent.parent.parent / "examples" / "extractor_candidates.txt"
        content = example_path.read_text(encoding="utf-8")
        candidates = parse_candidates(content)

        assert candidates is not None
        assert len(candidates) == 8
        assert candidates[0].id == "1"
        assert candidates[0].action.value == "ADD"

    def test_example_validated_candidates_parses(self) -> None:
        """Load and parse examples/validated_candidates.txt."""
        from pathlib import Path

        from memory_distiller.io.candidate_parser import parse_validated_candidates

        example_path = Path(__file__).parent.parent.parent / "examples" / "validated_candidates.txt"
        content = example_path.read_text(encoding="utf-8")
        validated = parse_validated_candidates(content)

        assert validated is not None
        assert len(validated) == 8
        assert validated[0].id == "1"
        assert validated[0].verdict.value == "KEEP"
