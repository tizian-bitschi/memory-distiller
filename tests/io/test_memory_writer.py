"""Tests for memory writer."""

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)
from memory_distiller.io.memory_writer import write_memory_document


class TestWriteEmptyDocument:
    """Tests for writing empty documents."""

    def test_write_empty_document_produces_correct_structure(self):
        """Write empty document produces correct structure."""
        doc = MemoryDocument()
        output = write_memory_document(doc)

        assert "# MEMORY_FULL" in output
        assert "## GLOBAL" in output
        assert "## PROJECTS" in output
        assert "## REPOS" in output
        assert "## TEMPORARY" in output
        assert "## DEPRECATED" in output
        assert "## OFFENE_KLÄRUNGEN" in output

        # Should have header lines
        lines = output.splitlines()
        assert any("SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE" in line for line in lines)
        assert any(
            "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON" in line
            for line in lines
        )
        assert any("QUESTION|WHY_IT_MATTERS" in line for line in lines)


class TestWriteDocumentWithEntries:
    """Tests for writing documents with entries."""

    def test_write_document_with_entries_produces_correct_output(self):
        """Write document with entries produces correct output."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="User prefers critical feedback.",
            evidence="2026-05-26 Chat",
        )
        doc = MemoryDocument(global_entries=[entry])
        output = write_memory_document(doc)

        assert "G|RULE|H|D|User prefers critical feedback.|2026-05-26 Chat" in output

    def test_write_project_entry(self):
        """Write project entry."""
        entry = MemoryEntry(
            scope="P:myproject",
            type=MemoryType.PREF,
            priority=Priority.M,
            stability=Stability.M,
            statement="Use tabs for indentation.",
            evidence="2026-05-20 Chat",
        )
        doc = MemoryDocument(project_entries=[entry])
        output = write_memory_document(doc)

        assert "P:myproject|PREF|M|M|Use tabs for indentation.|2026-05-20 Chat" in output


class TestWriteDeprecatedEntries:
    """Tests for writing deprecated entries."""

    def test_deprecated_entries_include_deprecation_reason(self):
        """Deprecated entries include deprecation_reason."""
        original = MemoryEntry(
            scope="G",
            type=MemoryType.PREF,
            priority=Priority.H,
            stability=Stability.D,
            statement="Old preference.",
            evidence="Old evidence.",
        )
        deprecated = DeprecatedMemoryEntry(
            entry=original,
            deprecation_reason="No longer relevant.",
        )
        doc = MemoryDocument(deprecated_entries=[deprecated])
        output = write_memory_document(doc)

        assert "G|PREF|H|D|Old preference.|Old evidence.|No longer relevant." in output


class TestWriteOpenQuestions:
    """Tests for writing open questions."""

    def test_open_questions_formatted_correctly(self):
        """Open questions formatted correctly."""
        doc = MemoryDocument(
            open_questions=[("Should we use tabs or spaces?", "Affects consistency.")]
        )
        output = write_memory_document(doc)

        assert "Should we use tabs or spaces?|Affects consistency." in output
        assert "QUESTION|WHY_IT_MATTERS" in output


class TestWriteRoundtrip:
    """Tests for writing and re-parsing."""

    def test_write_and_reparse(self):
        """Written document can be reparsed."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test rule.",
            evidence="Test evidence.",
        )
        doc = MemoryDocument(global_entries=[entry])
        output = write_memory_document(doc)

        from memory_distiller.io.memory_parser import parse_memory_document

        reparsed = parse_memory_document(output)
        assert len(reparsed.global_entries) == 1
        assert reparsed.global_entries[0].scope == "G"
        assert reparsed.global_entries[0].type == MemoryType.RULE
        assert reparsed.global_entries[0].priority == Priority.H
        assert reparsed.global_entries[0].stability == Stability.D
        assert reparsed.global_entries[0].statement == "Test rule."
        assert reparsed.global_entries[0].evidence == "Test evidence."

    def test_write_multiple_sections(self):
        """Write document with multiple sections."""
        global_entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Global rule.",
            evidence="Evidence.",
        )
        project_entry = MemoryEntry(
            scope="P:proj",
            type=MemoryType.PREF,
            priority=Priority.M,
            stability=Stability.M,
            statement="Project pref.",
            evidence="Evidence.",
        )
        deprecated = DeprecatedMemoryEntry(
            entry=MemoryEntry(
                scope="G",
                type=MemoryType.FACT,
                priority=Priority.L,
                stability=Stability.T,
                statement="Old fact.",
                evidence="Evidence.",
            ),
            deprecation_reason="Replaced.",
        )
        doc = MemoryDocument(
            global_entries=[global_entry],
            project_entries=[project_entry],
            deprecated_entries=[deprecated],
            open_questions=[("Question?", "Why matters.")],
        )
        output = write_memory_document(doc)

        from memory_distiller.io.memory_parser import parse_memory_document

        reparsed = parse_memory_document(output)
        assert len(reparsed.global_entries) == 1
        assert len(reparsed.project_entries) == 1
        assert len(reparsed.deprecated_entries) == 1
        assert len(reparsed.open_questions) == 1
