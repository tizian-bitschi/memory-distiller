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


class TestStrictParserRejectsAliases:
    """Tests that strict parsers reject enum aliases without repair."""

    def test_reject_type_alias_strict(self):
        """Type alias PREFERENCE is rejected with suggestion."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|PREFERENCE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'PREF'?" in str(e) for e in errors)

    def test_reject_scope_alias_strict(self):
        """Scope alias GLOBAL is rejected with suggestion."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|GLOBAL|RULE|H|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'G'?" in str(e) for e in errors)

    def test_reject_priority_alias_strict(self):
        """Priority alias HIGH is rejected with suggestion."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|RULE|HIGH|D|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'H'?" in str(e) for e in errors)

    def test_reject_stability_alias_strict(self):
        """Stability alias STABLE is rejected with suggestion."""
        text = """ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON
abc123|ADD|rule1|G|RULE|H|STABLE|Statement.|Evidence.|Reason.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'D'?" in str(e) for e in errors)

    def test_repair_then_parse_candidate_passes(self):
        """Repair with normalize_candidate_lines, then parse passes."""
        from memory_distiller.io.enum_aliases import normalize_candidate_lines

        raw = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY"
            "|STATEMENT|EVIDENCE|REASON\n"
            "abc123|ADD|rule1|PROJECT:Proj|PREFERENCE|HIGH|STABLE"
            "|Use units.|User said.|Project pref."
        )
        normalized, changes = normalize_candidate_lines(raw)
        assert len(changes) == 4
        candidates = parse_candidates(normalized)
        assert len(candidates) == 1
        assert candidates[0].scope == "P:Proj"
        assert candidates[0].type.value == "PREF"

    def test_repair_then_parse_validated_candidate_passes(self):
        """Repair validated candidate (11 columns), then parse passes."""
        from memory_distiller.io.enum_aliases import normalize_candidate_lines

        raw = (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY"
            "|STATEMENT|EVIDENCE|REASON\n"
            "M1|KEEP|ADD|-|PROJECT:RecipeBot|PREFERENCE|HIGH|STABLE"
            "|Use metric units.|User said so.|Project preference."
        )
        normalized, changes = normalize_candidate_lines(raw)
        assert len(changes) == 4
        validated = parse_validated_candidates(normalized)
        assert len(validated) == 1
        assert validated[0].scope == "P:RecipeBot"
        assert validated[0].type.value == "PREF"
        assert validated[0].priority.value == "H"
        assert validated[0].stability.value == "D"
        assert validated[0].verdict.value == "KEEP"

    def test_reject_validated_type_alias_strict(self):
        """Validated candidate type alias rejected with suggestion."""
        text = (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY"
            "|STATEMENT|EVIDENCE|REASON\n"
            "M1|KEEP|ADD|-|PROJECT:RecipeBot|PREFERENCE|HIGH|STABLE"
            "|Use metric units.|User said so.|Project preference.\n"
        )
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_validated_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'PREF'?" in str(e) for e in errors)


class TestParseValidatedCandidateFormatHint:
    """Tests for error hints when 10-column extractor format is used in validated parser."""

    def test_reject_10_column_extractor_format_with_helpful_hint(self):
        """Reject 10-column extractor format with helpful hint about expected 11 columns."""
        text = (
            "M1|ADD|-|P:RecipeBot|RULE|H|D|All recipes vegetarian."
            "|User asked.|Reusable project rule.\n"
        )
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_validated_candidates(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        error_text = str(errors[0])
        assert "Expected 11 columns" in error_text
        assert "got 10" in error_text
        assert "extractor candidate format" in error_text
        assert "VERDICT" in error_text
        assert "M1|KEEP|ADD" in error_text

    def test_parse_candidates_still_accepts_10_column_line(self):
        """parse_candidates still accepts 10-column extractor format (no VERDICT column)."""
        text = (
            "M1|ADD|-|P:RecipeBot|RULE|H|D|All recipes vegetarian."
            "|User asked.|Reusable project rule.\n"
        )
        candidates = parse_candidates(text)
        assert len(candidates) == 1
        assert candidates[0].id == "M1"
        assert candidates[0].action == CandidateAction.ADD

    def test_parse_validated_candidates_still_accepts_valid_11_column_line(self):
        """parse_validated_candidates accepts valid 11-column validated candidate line."""
        header = "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON"
        line = (
            "M1|KEEP|ADD|-|P:RecipeBot|RULE|H|D|All recipes vegetarian."
            "|User asked.|Reusable project rule."
        )
        text = f"{header}\n{line}\n"
        validated = parse_validated_candidates(text)
        assert len(validated) == 1
        assert validated[0].id == "M1"
        assert validated[0].verdict == ValidationVerdict.KEEP
