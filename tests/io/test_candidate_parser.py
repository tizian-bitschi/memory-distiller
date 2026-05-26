"""Tests for candidate parser."""

import pytest

from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.io.candidate_parser import (
    parse_candidates,
    parse_validated_candidates,
)


class TestParseValidCandidateLine:
    """Tests for parsing valid candidate lines."""

    def test_parse_valid_candidate_line(self):
        """Parse valid candidate line (10 columns)."""
        header = "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON"
        line = "abc123|ADD|prefer-critical-feedback|G|RULE|H|D|User prefers critical feedback."
        line += "|2026-05-26 Chat|Extracted from discussion."
        text = f"{header}\n{line}\n"
        candidates = parse_candidates(text)
        assert len(candidates) == 1
        candidate = candidates[0]
        assert candidate.id == "abc123"
        assert candidate.action == CandidateAction.ADD
        assert candidate.target == "prefer-critical-feedback"
        assert candidate.scope == "G"
        assert candidate.type == MemoryType.RULE
        assert candidate.priority == Priority.H
        assert candidate.stability == Stability.D
        assert candidate.statement == "User prefers critical feedback."
        assert candidate.evidence == "2026-05-26 Chat"
        assert candidate.reason == "Extracted from discussion."

    def test_parse_multiple_candidates(self):
        """Parse multiple candidate lines."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|RULE|H|D|Rule 1.|Evidence.|Reason 1.
def456|ADD|rule2|P:proj|PREF|M|M|Rule 2.|Evidence.|Reason 2.
"""
        candidates = parse_candidates(text)
        assert len(candidates) == 2
        assert candidates[0].id == "abc123"
        assert candidates[1].id == "def456"


class TestParseValidatedCandidateLine:
    """Tests for parsing validated candidate lines."""

    def test_parse_valid_validated_candidate_line(self):
        """Parse valid validated candidate line (11 columns)."""
        header = "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON"
        line = "abc123|KEEP|ADD|prefer-critical-feedback|G|RULE|H|D|User prefers critical feedback."
        line += "|2026-05-26 Chat|Extracted from discussion."
        text = f"{header}\n{line}\n"
        validated = parse_validated_candidates(text)
        assert len(validated) == 1
        candidate = validated[0]
        assert candidate.id == "abc123"
        assert candidate.verdict == ValidationVerdict.KEEP
        assert candidate.action == CandidateAction.ADD
        assert candidate.target == "prefer-critical-feedback"
        assert candidate.scope == "G"
        assert candidate.type == MemoryType.RULE
        assert candidate.priority == Priority.H
        assert candidate.stability == Stability.D
        assert candidate.statement == "User prefers critical feedback."
        assert candidate.evidence == "2026-05-26 Chat"
        assert candidate.reason == "Extracted from discussion."


class TestParseCandidateErrors:
    """Tests for candidate parsing errors."""

    def test_reject_wrong_column_count(self):
        """Reject wrong column count."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|RULE|H|D|Statement.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_reject_invalid_action_enum(self):
        """Reject invalid enum value for action."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|INVALID|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("action" in str(e).lower() or "invalid" in str(e).lower() for e in errors)

    def test_reject_invalid_type_enum(self):
        """Reject invalid enum value for type."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|INVALID_TYPE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("type" in str(e).lower() or "invalid" in str(e).lower() for e in errors)

    def test_reject_invalid_scope_empty(self):
        """Reject invalid scope (empty)."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1||RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_reject_invalid_scope_unknown_prefix(self):
        """Reject invalid scope (unknown prefix)."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|X:unknown|RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_multiple_errors_collected(self):
        """Multiple errors collected in ParseErrorCollection."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|INVALID|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.
def456|INVALID2|rule2|P:proj|PREF|M|M|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 2


class TestParseSkippedLines:
    """Tests for lines that should be ignored."""

    def test_ignore_empty_lines(self):
        """Ignore empty lines."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON

abc123|ADD|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.

"""
        candidates = parse_candidates(text)
        assert len(candidates) == 1
        assert candidates[0].id == "abc123"

    def test_ignore_header_line(self):
        """Ignore header line."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.
"""
        candidates = parse_candidates(text)
        assert len(candidates) == 1
        assert candidates[0].id == "abc123"


class TestParseErrorLineNumbers:
    """Tests for error line numbers."""

    def test_errors_include_line_number(self):
        """Errors include line number for candidates."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|INVALID|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any(e.line_number == 2 for e in errors)

    def test_errors_include_line_number_validated(self):
        """Errors include line number for validated candidates."""
        text = """ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|INVALID_VERDICT|ADD|rule1|G|RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_validated_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any(e.line_number == 2 for e in errors)
