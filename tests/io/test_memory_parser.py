"""Tests for memory parser."""

import pytest

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import DeprecatedMemoryEntry
from memory_distiller.io.memory_parser import parse_memory_document


class TestParseValidMemoryEntry:
    """Tests for parsing valid memory entries."""

    def test_parse_valid_memory_entry_line(self):
        """Parse valid MemoryEntry line (6 columns)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|User prefers critical feedback.|2026-05-26 Chat
"""
        doc = parse_memory_document(text)
        assert len(doc.global_entries) == 1
        entry = doc.global_entries[0]
        assert entry.scope == "G"
        assert entry.type == MemoryType.RULE
        assert entry.priority == Priority.H
        assert entry.stability == Stability.D
        assert entry.statement == "User prefers critical feedback."
        assert entry.evidence == "2026-05-26 Chat"

    def test_parse_project_scope_entry(self):
        """Parse entry with project scope."""
        text = """# MEMORY_FULL
## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:myproject|PREF|M|M|Use tabs for indentation.|2026-05-20 Chat
"""
        doc = parse_memory_document(text)
        assert len(doc.project_entries) == 1
        entry = doc.project_entries[0]
        assert entry.scope == "P:myproject"
        assert entry.type == MemoryType.PREF

    def test_parse_repo_scope_entry(self):
        """Parse entry with repo scope."""
        text = """# MEMORY_FULL
## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
R:backend|FACT|L|T|API returns JSON.|2026-05-22 Review
"""
        doc = parse_memory_document(text)
        assert len(doc.repo_entries) == 1
        entry = doc.repo_entries[0]
        assert entry.scope == "R:backend"


class TestParseFullDocument:
    """Tests for parsing full documents."""

    def test_parse_full_document_with_all_sections(self):
        """Parse full document with all sections."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Global rule.|Evidence.

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:proj|PREF|M|M|Project pref.|Evidence.

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
R:repo|FACT|L|T|Repo fact.|Evidence.

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
T|TASK|H|D|Temp task.|Evidence.

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON
G|PREF|H|M|Old pref.|Evidence.|Replaced.

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS
Open question?|Why matters.
"""
        doc = parse_memory_document(text)
        assert len(doc.global_entries) == 1
        assert len(doc.project_entries) == 1
        assert len(doc.repo_entries) == 1
        assert len(doc.temporary_entries) == 1
        assert len(doc.deprecated_entries) == 1
        assert len(doc.open_questions) == 1


class TestParseErrors:
    """Tests for parsing error cases."""

    def test_reject_invalid_enum_value(self):
        """Reject invalid enum value (e.g., type=INVALID)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|INVALID|H|D|Some statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) == 1
        assert "Invalid" in str(errors[0]) or "Unknown" in str(errors[0])

    def test_reject_invalid_scope_empty(self):
        """Reject invalid scope (empty)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
|H|D|Some statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_reject_invalid_scope_unknown_prefix(self):
        """Reject invalid scope (unknown prefix)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
X:unknown|H|D|Some statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_reject_wrong_column_count_five(self):
        """Reject wrong column count (5 for normal entry)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
    G|RULE|H|D|Some statement.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_reject_wrong_column_count_seven(self):
        """Reject wrong column count (7 for normal entry)."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Some statement.|Evidence.|Extra col
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1

    def test_multiple_errors_collected(self):
        """Multiple errors collected across different entries."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|INVALID_TYPE1|H|D|Statement.|Evidence.
G|INVALID_TYPE2|H|D|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 2


class TestParseDeprecatedEntry:
    """Tests for parsing deprecated entries."""

    def test_parse_deprecated_entry(self):
        """Parse deprecated entry (7 columns)."""
        text = """# MEMORY_FULL
## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON
G|PREF|M|M|Old preference.|2026-05-01|Too specific, replaced.
"""
        doc = parse_memory_document(text)
        assert len(doc.deprecated_entries) == 1
        deprecated = doc.deprecated_entries[0]
        assert isinstance(deprecated, DeprecatedMemoryEntry)
        assert deprecated.entry.scope == "G"
        assert deprecated.entry.type == MemoryType.PREF
        assert deprecated.deprecation_reason == "Too specific, replaced."


class TestParseOpenQuestion:
    """Tests for parsing open questions."""

    def test_parse_open_question(self):
        """Parse open question (2 columns)."""
        text = """# MEMORY_FULL
## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS
Should we use tabs or spaces?|Affects consistency across team.
"""
        doc = parse_memory_document(text)
        assert len(doc.open_questions) == 1
        question, why = doc.open_questions[0]
        assert question == "Should we use tabs or spaces?"
        assert why == "Affects consistency across team."

    def test_parse_open_question_wrong_columns(self):
        """Reject open question with wrong column count."""
        text = """# MEMORY_FULL
## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS
Question only.
"""
        with pytest.raises(ParseErrorCollection):
            parse_memory_document(text)


class TestParseErrorLineNumbers:
    """Tests for error line numbers."""

    def test_errors_include_line_number(self):
        """Errors include line number."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|INVALID_TYPE|H|D|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        # The error should reference line 4 (where the invalid entry is)
        assert any(e.line_number == 4 for e in errors)


class TestParseSkippedLines:
    """Tests for lines that should be ignored."""

    def test_header_lines_ignored(self):
        """Header lines are ignored."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Valid entry.|Evidence.
"""
        doc = parse_memory_document(text)
        assert len(doc.global_entries) == 1

    def test_empty_lines_ignored(self):
        """Empty lines are ignored."""
        text = """
# MEMORY_FULL

## GLOBAL

SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

G|RULE|H|D|Valid entry.|Evidence.

"""
        doc = parse_memory_document(text)
        assert len(doc.global_entries) == 1

    def test_lines_before_first_section_ignored(self):
        """Lines before first section are ignored."""
        text = """Some random text before sections.
# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Valid entry.|Evidence.
"""
        doc = parse_memory_document(text)
        assert len(doc.global_entries) == 1


class TestRoundtrip:
    """Tests for roundtrip parsing."""

    def test_roundtrip(self):
        """Parse, write, parse again produces equivalent document."""
        original_text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|User prefers critical feedback.|2026-05-26 Chat

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:myproject|PREF|M|M|Use tabs for indentation.|2026-05-20 Chat

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
R:backend|FACT|L|T|API returns JSON.|2026-05-22 Review

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
T|TASK|H|D|Temp task.|Evidence.

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON
G|PREF|H|M|Old pref.|Evidence.|Replaced.

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS
Open question?|Why matters.
"""
        from memory_distiller.io.memory_writer import write_memory_document

        doc1 = parse_memory_document(original_text)
        written = write_memory_document(doc1)
        doc2 = parse_memory_document(written)

        assert len(doc1.global_entries) == len(doc2.global_entries)
        assert len(doc1.project_entries) == len(doc2.project_entries)
        assert len(doc1.repo_entries) == len(doc2.repo_entries)
        assert len(doc1.temporary_entries) == len(doc2.temporary_entries)
        assert len(doc1.deprecated_entries) == len(doc2.deprecated_entries)
        assert len(doc1.open_questions) == len(doc2.open_questions)

        # Compare entries field by field
        for e1, e2 in zip(doc1.global_entries, doc2.global_entries):
            assert e1.scope == e2.scope
            assert e1.type == e2.type
            assert e1.priority == e2.priority
            assert e1.stability == e2.stability
            assert e1.statement == e2.statement
            assert e1.evidence == e2.evidence

        for d1, d2 in zip(doc1.deprecated_entries, doc2.deprecated_entries):
            assert d1.deprecation_reason == d2.deprecation_reason
            assert d1.entry.scope == d2.entry.scope
            assert d1.entry.type == d2.entry.type
            assert d1.entry.statement == d2.entry.statement


class TestStrictParserRejectsAliases:
    """Tests that strict parser rejects enum aliases without repair."""

    def test_reject_memory_type_alias_strict(self):
        """Type alias PREFERENCE is rejected with suggestion."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|PREFERENCE|H|D|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'PREF'?" in str(e) for e in errors)

    def test_reject_memory_scope_alias_strict(self):
        """Scope alias GLOBAL is rejected with suggestion."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
GLOBAL|RULE|H|D|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'G'?" in str(e) for e in errors)

    def test_reject_memory_priority_alias_strict(self):
        """Priority alias HIGH is rejected with suggestion."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|HIGH|D|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'H'?" in str(e) for e in errors)

    def test_reject_memory_stability_alias_strict(self):
        """Stability alias STABLE is rejected with suggestion."""
        text = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|STABLE|Statement.|Evidence.
"""
        with pytest.raises(ParseErrorCollection) as exc_info:
            parse_memory_document(text)
        errors = exc_info.value.errors
        assert len(errors) >= 1
        assert any("Did you mean 'D'?" in str(e) for e in errors)

    def test_repair_then_parse_memory_passes(self):
        """Repair with normalize_memory_document, then parse passes."""
        from memory_distiller.io.enum_aliases import normalize_memory_document

        raw = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
GLOBAL|RULE|HIGH|STABLE|Use metric units.|User said so.

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
PROJECT:RecipeBot|PREFERENCE|MEDIUM|DURABLE|Project preference.|Evidence.
"""
        normalized, changes = normalize_memory_document(raw)
        assert len(changes) >= 4
        doc = parse_memory_document(normalized)
        assert len(doc.global_entries) == 1
        assert doc.global_entries[0].scope == "G"
        assert doc.global_entries[0].type.value == "RULE"
        assert doc.project_entries[0].scope == "P:RecipeBot"
        assert doc.project_entries[0].type.value == "PREF"
