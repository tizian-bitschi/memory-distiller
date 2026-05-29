"""Tests for merge plan parser."""

import pytest

from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.merge_plan import MergeDecision, MergePlan
from memory_distiller.io.merge_plan_parser import parse_merge_plan


class TestParseValidMergePlan:
    """Tests for parsing valid merge plan entries."""

    def test_valid_apply_add(self) -> None:
        """Valid APPLY_ADD entry parses correctly."""
        text = (
            "M1|APPLY_ADD|-|G|RULE|H|D|Prefer critical feedback.|2026-05-27 Evidence.|New rule.\n"
        )
        plan = parse_merge_plan(text)

        assert len(plan.entries) == 1
        entry = plan.entries[0]
        assert entry.candidate_id == "M1"
        assert entry.decision == MergeDecision.APPLY_ADD
        assert entry.target == "-"
        assert entry.scope == "G"
        assert entry.type == "RULE"
        assert entry.priority == "H"
        assert entry.stability == "D"
        assert entry.statement == "Prefer critical feedback."
        assert entry.evidence == "2026-05-27 Evidence."
        assert entry.reason == "New rule."

    def test_valid_apply_update(self) -> None:
        """Valid APPLY_UPDATE entry parses correctly."""
        text = (
            "M2|APPLY_UPDATE|Old statement.|P:RecipeBot|PREF|M|M|"
            "New statement.|Evidence.|Refines.\n"
        )
        plan = parse_merge_plan(text)

        assert len(plan.entries) == 1
        entry = plan.entries[0]
        assert entry.candidate_id == "M2"
        assert entry.decision == MergeDecision.APPLY_UPDATE
        assert entry.target == "Old statement."
        assert entry.scope == "P:RecipeBot"
        assert entry.type == "PREF"
        assert entry.priority == "M"
        assert entry.stability == "M"
        assert entry.statement == "New statement."
        assert entry.evidence == "Evidence."
        assert entry.reason == "Refines."

    def test_valid_skip_drop(self) -> None:
        """Valid SKIP_DROP entry parses correctly."""
        text = "M3|SKIP_DROP|-|T|FACT|L|T|Temp detail.|User said.|Temporary.\n"
        plan = parse_merge_plan(text)

        assert len(plan.entries) == 1
        entry = plan.entries[0]
        assert entry.candidate_id == "M3"
        assert entry.decision == MergeDecision.SKIP_DROP
        assert entry.target == "-"
        assert entry.scope == "T"
        assert entry.type == "FACT"
        assert entry.priority == "L"
        assert entry.stability == "T"

    def test_valid_add_open_question(self) -> None:
        """Valid ADD_OPEN_QUESTION entry parses correctly."""
        text = (
            "M4|ADD_OPEN_QUESTION|-|P:RecipeBot|RULE|H|M|"
            "Should we support JSON?|Not decided.|Needs decision.\n"
        )
        plan = parse_merge_plan(text)

        assert len(plan.entries) == 1
        entry = plan.entries[0]
        assert entry.candidate_id == "M4"
        assert entry.decision == MergeDecision.ADD_OPEN_QUESTION
        assert entry.statement == "Should we support JSON?"
        assert entry.reason == "Needs decision."

    def test_valid_apply_deprecate(self) -> None:
        """Valid APPLY_DEPRECATE entry parses correctly."""
        text = (
            "M5|APPLY_DEPRECATE|Old rule.|G|RULE|H|D|Replaced rule.|Evidence.|No longer relevant.\n"
        )
        plan = parse_merge_plan(text)

        assert len(plan.entries) == 1
        entry = plan.entries[0]
        assert entry.candidate_id == "M5"
        assert entry.decision == MergeDecision.APPLY_DEPRECATE
        assert entry.target == "Old rule."
        assert entry.reason == "No longer relevant."


class TestParseInvalidMergePlan:
    """Tests for parsing invalid merge plan entries."""

    def test_invalid_decision(self) -> None:
        """Unknown decision raises ParseErrorCollection."""
        text = "M1|INVALID_DECISION|-|G|RULE|H|D|Statement.|Evidence.|Reason.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        assert len(exc_info.value.errors) >= 1
        assert any("Unknown merge decision" in str(e) for e in exc_info.value.errors)

    def test_invalid_enum_type(self) -> None:
        """Unknown type raises ParseErrorCollection."""
        text = "M1|APPLY_ADD|-|G|INVALID_TYPE|H|D|Statement.|Evidence.|Reason.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Unknown memory type" in str(e) for e in errors)

    def test_invalid_enum_priority(self) -> None:
        """Unknown priority raises ParseErrorCollection."""
        text = "M1|APPLY_ADD|-|G|RULE|INVALID_PRIO|D|Statement.|Evidence.|Reason.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Unknown priority" in str(e) for e in errors)

    def test_invalid_enum_stability(self) -> None:
        """Unknown stability raises ParseErrorCollection."""
        text = "M1|APPLY_ADD|-|G|RULE|H|INVALID_STAB|Statement.|Evidence.|Reason.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Unknown stability" in str(e) for e in errors)

    def test_wrong_column_count(self) -> None:
        """Wrong number of columns raises ParseErrorCollection."""
        text = "M1|APPLY_ADD|-|G|RULE|H|D|Statement.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Expected exactly 10 columns" in str(e) for e in errors)

    def test_apply_update_missing_target(self) -> None:
        """APPLY_UPDATE with placeholder target raises error."""
        text = "M1|APPLY_UPDATE|-|G|RULE|H|D|New statement.|Evidence.|Reason.\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("APPLY_UPDATE requires non-empty" in str(e) for e in errors)

    def test_apply_add_missing_statement(self) -> None:
        """APPLY_ADD with placeholder statement raises error."""
        # 10 columns: ID|DECISION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
        # TARGET is "-" (column 3), using placeholder "n/a" as statement (column 8)
        text = "M1|APPLY_ADD|-|G|RULE|H|D|n/a|Evidence|Reason\n"
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        # The error message says "APPLY_ADD requires non-empty statement"
        assert any("APPLY_ADD requires non-empty" in str(e) for e in errors)

    def test_multiple_errors_collected(self) -> None:
        """Multiple errors in one call collected."""
        text = """M1|INVALID_DECISION|-|G|RULE|H|D|Statement.|Evidence.|Reason.
M2|APPLY_ADD|-|G|INVALID_TYPE|H|D|Statement.|Evidence.|Reason.
M3|SKIP_DROP|-|T|FACT|L|T|Temp.|User.|Note.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_merge_plan(text)
        errors = exc_info.value.errors
        # At least 2 errors should be collected
        assert len(errors) >= 2

    def test_rejects_placeholder_text(self) -> None:
        """Placeholder texts like 'No entries', 'None', 'Keine Einträge' rejected."""
        for placeholder in ["No entries", "None", "Keine Einträge"]:
            text = f"M1|APPLY_ADD|-|-|G|RULE|H|D|{placeholder}|Evidence.|Reason.\n"
            with pytest.raises(ParseErrorCollection) as exc_info:
                parse_merge_plan(text)
            errors = exc_info.value.errors
            assert len(errors) >= 1


class TestParseEmptyOrWhitespace:
    """Tests for empty or whitespace-only input."""

    def test_empty_string_returns_empty_plan(self) -> None:
        """Empty string returns empty MergePlan."""
        plan = parse_merge_plan("")
        assert plan.entries == ()

    def test_whitespace_only_returns_empty_plan(self) -> None:
        """Whitespace-only returns empty MergePlan."""
        plan = parse_merge_plan("   \n\n  \n")
        assert plan.entries == ()

    def test_empty_lines_ignored(self) -> None:
        """Empty lines in input are ignored."""
        text = """M1|APPLY_ADD|-|G|RULE|H|D|Rule.|Evidence.|Reason.

M2|SKIP_DROP|-|T|FACT|L|T|Temp.|User.|Note.
"""
        plan = parse_merge_plan(text)
        assert len(plan.entries) == 2


class TestParseMergePlanReturnsMergePlan:
    """Tests that parse_merge_plan returns correct type."""

    def test_returns_merge_plan_instance(self) -> None:
        """parse_merge_plan returns MergePlan instance."""
        text = "M1|APPLY_ADD|-|G|RULE|H|D|Statement.|Evidence.|Reason.\n"
        result = parse_merge_plan(text)
        assert isinstance(result, MergePlan)

    def test_entries_is_tuple(self) -> None:
        """entries attribute is a tuple (immutable)."""
        text = "M1|APPLY_ADD|-|G|RULE|H|D|Statement.|Evidence.|Reason.\n"
        plan = parse_merge_plan(text)
        assert isinstance(plan.entries, tuple)
