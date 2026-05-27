"""Tests for UI components."""

from __future__ import annotations

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)
from memory_distiller.domain.errors import ParseError, ParseErrorCollection
from memory_distiller.domain.memory_entry import DeprecatedMemoryEntry, MemoryDocument, MemoryEntry
from memory_distiller.llm.errors import (
    EmptyLlmResponseError,
    LlmProviderError,
    MissingApiKeyError,
)
from memory_distiller.ui.components import (
    estimate_tokens,
    render_candidate_table,
    render_error,
    render_memory_summary,
    render_validated_candidate_table,
)


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    def test_empty_string(self) -> None:
        """Empty string returns 0."""
        assert estimate_tokens("") == 0

    def test_exact_division(self) -> None:
        """Text with length divisible by 4."""
        assert estimate_tokens("abcd") == 1

    def test_remainder_truncated(self) -> None:
        """Remainder is truncated, not rounded."""
        assert estimate_tokens("abc") == 0
        assert estimate_tokens("abcde") == 1

    def test_normal_text(self) -> None:
        """Normal text estimation."""
        text = "This is a sample text for testing token estimation."
        assert estimate_tokens(text) == len(text) // 4


class TestRenderCandidateTable:
    """Tests for render_candidate_table function."""

    def test_empty_list(self) -> None:
        """Empty candidate list returns empty list."""
        result = render_candidate_table([])
        assert result == []

    def test_single_candidate(self) -> None:
        """Single candidate renders correctly."""
        candidate = MemoryCandidate(
            id="test-001",
            action=CandidateAction.ADD,
            target="test-rule",
            scope="global",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test statement",
            evidence="Test evidence",
            reason="Test reason",
        )
        result = render_candidate_table([candidate])
        assert len(result) == 1
        assert result[0]["id"] == "test-001"
        assert result[0]["action"] == "ADD"
        assert result[0]["target"] == "test-rule"
        assert result[0]["scope"] == "global"
        assert result[0]["type"] == "RULE"
        assert result[0]["priority"] == "H"
        assert result[0]["stability"] == "D"
        assert result[0]["statement"] == "Test statement"
        assert result[0]["evidence"] == "Test evidence"
        assert result[0]["reason"] == "Test reason"

    def test_multiple_candidates(self) -> None:
        """Multiple candidates render correctly."""
        candidates = [
            MemoryCandidate(
                id="c1",
                action=CandidateAction.UPDATE,
                target="pref-1",
                scope="P:myproject",
                type=MemoryType.PREF,
                priority=Priority.M,
                stability=Stability.M,
                statement="Statement 1",
                evidence="Evidence 1",
                reason="Reason 1",
            ),
            MemoryCandidate(
                id="c2",
                action=CandidateAction.DEPRECATE,
                target="old-rule",
                scope="global",
                type=MemoryType.RULE,
                priority=Priority.L,
                stability=Stability.T,
                statement="Statement 2",
                evidence="Evidence 2",
                reason="Reason 2",
            ),
        ]
        result = render_candidate_table(candidates)
        assert len(result) == 2
        assert result[0]["id"] == "c1"
        assert result[1]["id"] == "c2"


class TestRenderValidatedCandidateTable:
    """Tests for render_validated_candidate_table function."""

    def test_empty_list(self) -> None:
        """Empty validated candidate list returns empty list."""
        result = render_validated_candidate_table([])
        assert result == []

    def test_single_validated_candidate(self) -> None:
        """Single validated candidate renders correctly with verdict."""
        candidate = ValidatedCandidate(
            id="val-001",
            verdict=ValidationVerdict.KEEP,
            action=CandidateAction.ADD,
            target="rule-1",
            scope="global",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Keep this",
            evidence="Evidence",
            reason="Reason",
        )
        result = render_validated_candidate_table([candidate])
        assert len(result) == 1
        assert result[0]["id"] == "val-001"
        assert result[0]["verdict"] == "KEEP"
        assert result[0]["action"] == "ADD"
        assert result[0]["target"] == "rule-1"

    def test_multiple_verdicts(self) -> None:
        """Multiple validated candidates with different verdicts."""
        candidates = [
            ValidatedCandidate(
                id="v1",
                verdict=ValidationVerdict.KEEP,
                action=CandidateAction.ADD,
                target="t1",
                scope="G",
                type=MemoryType.FACT,
                priority=Priority.H,
                stability=Stability.D,
                statement="S1",
                evidence="E1",
                reason="R1",
            ),
            ValidatedCandidate(
                id="v2",
                verdict=ValidationVerdict.DROP,
                action=CandidateAction.IGNORE,
                target="t2",
                scope="G",
                type=MemoryType.PREF,
                priority=Priority.L,
                stability=Stability.T,
                statement="S2",
                evidence="E2",
                reason="R2",
            ),
            ValidatedCandidate(
                id="v3",
                verdict=ValidationVerdict.EDIT,
                action=CandidateAction.UPDATE,
                target="t3",
                scope="P:test",
                type=MemoryType.DECISION,
                priority=Priority.M,
                stability=Stability.M,
                statement="S3",
                evidence="E3",
                reason="R3",
            ),
        ]
        result = render_validated_candidate_table(candidates)
        assert result[0]["verdict"] == "KEEP"
        assert result[1]["verdict"] == "DROP"
        assert result[2]["verdict"] == "EDIT"


class TestRenderMemorySummary:
    """Tests for render_memory_summary function."""

    def test_empty_document(self) -> None:
        """Empty memory document returns all zeros."""
        doc = MemoryDocument()
        result = render_memory_summary(doc)
        assert result["global_entries"] == 0
        assert result["project_entries"] == 0
        assert result["repo_entries"] == 0
        assert result["temporary_entries"] == 0
        assert result["deprecated_entries"] == 0
        assert result["open_questions"] == 0

    def test_populated_document(self) -> None:
        """Document with entries returns correct counts."""
        doc = MemoryDocument(
            global_entries=[
                MemoryEntry(
                    scope="G",
                    type=MemoryType.RULE,
                    priority=Priority.H,
                    stability=Stability.D,
                    statement="Global rule",
                    evidence="e1",
                ),
            ],
            project_entries=[
                MemoryEntry(
                    scope="P:test",
                    type=MemoryType.PREF,
                    priority=Priority.M,
                    stability=Stability.M,
                    statement="Pref1",
                    evidence="e2",
                ),
                MemoryEntry(
                    scope="P:test",
                    type=MemoryType.FACT,
                    priority=Priority.L,
                    stability=Stability.T,
                    statement="Fact1",
                    evidence="e3",
                ),
            ],
            repo_entries=[
                MemoryEntry(
                    scope="R:repo",
                    type=MemoryType.DECISION,
                    priority=Priority.H,
                    stability=Stability.D,
                    statement="Decision",
                    evidence="e4",
                ),
            ],
            temporary_entries=[
                MemoryEntry(
                    scope="T",
                    type=MemoryType.TASK,
                    priority=Priority.M,
                    stability=Stability.T,
                    statement="Task",
                    evidence="e5",
                ),
            ],
            deprecated_entries=[
                DeprecatedMemoryEntry(
                    entry=MemoryEntry(
                        scope="G",
                        type=MemoryType.RULE,
                        priority=Priority.L,
                        stability=Stability.D,
                        statement="Old rule",
                        evidence="e6",
                    ),
                    deprecation_reason="Superseded",
                ),
            ],
            open_questions=[("Question 1?", "Because it matters"), ("Question 2?", "For testing")],
        )
        result = render_memory_summary(doc)
        assert result["global_entries"] == 1
        assert result["project_entries"] == 2
        assert result["repo_entries"] == 1
        assert result["temporary_entries"] == 1
        assert result["deprecated_entries"] == 1
        assert result["open_questions"] == 2


class TestRenderError:
    """Tests for render_error function."""

    def test_parse_error_collection_single(self) -> None:
        """ParseErrorCollection with single error."""
        error = ParseErrorCollection(
            [ParseError(line_number=10, line="bad line", message="Invalid format")]
        )
        result = render_error(error)
        assert "Line 10" in result
        assert "Invalid format" in result

    def test_parse_error_collection_multiple(self) -> None:
        """ParseErrorCollection with multiple errors."""
        error = ParseErrorCollection(
            [
                ParseError(line_number=5, line="line1", message="Error 1"),
                ParseError(line_number=12, line="line2", message="Error 2"),
                ParseError(line_number=20, line="line3", message="Error 3"),
            ]
        )
        result = render_error(error)
        assert "Line 5" in result
        assert "Line 12" in result
        assert "Line 20" in result
        assert "Error 1" in result
        assert "Error 2" in result
        assert "Error 3" in result

    def test_parse_error_collection_empty(self) -> None:
        """ParseErrorCollection with no errors."""
        error = ParseErrorCollection([])
        result = render_error(error)
        assert "no errors" in result.lower()

    def test_value_error(self) -> None:
        """ValueError shows message."""
        error = ValueError("Invalid value provided")
        result = render_error(error)
        assert "Invalid value provided" in result

    def test_missing_api_key_error(self) -> None:
        """MissingApiKeyError (LlmError subclass) shows message."""
        error = MissingApiKeyError("DEEPSEEK_API_KEY not set")
        result = render_error(error)
        assert "DEEPSEEK_API_KEY not set" in result

    def test_empty_llm_response_error(self) -> None:
        """EmptyLlmResponseError shows message."""
        error = EmptyLlmResponseError("LLM returned empty response")
        result = render_error(error)
        assert "LLM returned empty response" in result

    def test_llm_provider_error(self) -> None:
        """LlmProviderError shows message."""
        error = LlmProviderError("Provider rate limit exceeded")
        result = render_error(error)
        assert "Provider rate limit exceeded" in result

    def test_generic_exception(self) -> None:
        """Generic Exception shows class name and message."""
        error = RuntimeError("Something went wrong")
        result = render_error(error)
        assert "RuntimeError" in result
        assert "Something went wrong" in result

    def test_custom_exception(self) -> None:
        """Custom exception shows class name and message."""

        class CustomError(Exception):
            pass

        error = CustomError("Custom error message")
        result = render_error(error)
        assert "CustomError" in result
        assert "Custom error message" in result
