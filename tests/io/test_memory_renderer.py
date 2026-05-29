"""Tests for memory renderer."""

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.io.memory_renderer import render_memory_document


class TestRenderEmptyDocument:
    """Tests for rendering empty documents."""

    def test_empty_sections_no_placeholders(self) -> None:
        """Empty sections have only header + table header."""
        doc = MemoryDocument()
        output = render_memory_document(doc)

        lines = output.splitlines()

        # Should have header
        assert lines[0] == "# MEMORY_FULL"

        # GLOBAL section should end after table header (no entries)
        global_idx = lines.index("## GLOBAL")
        global_header_idx = global_idx + 1
        assert lines[global_header_idx] == "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE"
        # Next non-empty line should be the next section header
        next_section_idx = global_header_idx + 1
        # Skip empty lines
        while next_section_idx < len(lines) and lines[next_section_idx] == "":
            next_section_idx += 1
        assert lines[next_section_idx] == "## PROJECTS"

    def test_all_section_headers_present(self) -> None:
        """All 6 sections present."""
        doc = MemoryDocument()
        output = render_memory_document(doc)

        assert "## GLOBAL" in output
        assert "## PROJECTS" in output
        assert "## REPOS" in output
        assert "## TEMPORARY" in output
        assert "## DEPRECATED" in output
        assert "## OFFENE_KLÄRUNGEN" in output

    def test_all_table_headers_present(self) -> None:
        """Correct table headers per section."""
        doc = MemoryDocument()
        output = render_memory_document(doc)

        # Normal entry sections have 6-column header
        assert "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE" in output
        # Deprecated has 7-column header
        assert "SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON" in output
        # Open questions has 2-column header
        assert "QUESTION|WHY_IT_MATTERS" in output


class TestRenderWithEntries:
    """Tests for rendering documents with entries."""

    def test_global_entry_rendered(self) -> None:
        """Global entry rendered correctly."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Prefer critical feedback.",
            evidence="2026-05-27 Chat",
        )
        doc = MemoryDocument(global_entries=[entry])
        output = render_memory_document(doc)

        assert "G|RULE|H|D|Prefer critical feedback.|2026-05-27 Chat" in output

    def test_project_entry_rendered(self) -> None:
        """Project entry rendered correctly."""
        entry = MemoryEntry(
            scope="P:RecipeBot",
            type=MemoryType.PREF,
            priority=Priority.M,
            stability=Stability.M,
            statement="Use metric units.",
            evidence="User request",
        )
        doc = MemoryDocument(project_entries=[entry])
        output = render_memory_document(doc)

        assert "P:RecipeBot|PREF|M|M|Use metric units.|User request" in output

    def test_deprecated_entries_seven_columns(self) -> None:
        """Deprecated entries have 7 columns."""
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
        output = render_memory_document(doc)

        assert "G|PREF|H|D|Old preference.|Old evidence.|No longer relevant." in output

    def test_open_questions_two_columns(self) -> None:
        """Open questions have 2 columns."""
        doc = MemoryDocument(
            open_questions=[("Should we use tabs or spaces?", "Affects consistency.")]
        )
        output = render_memory_document(doc)

        assert "Should we use tabs or spaces?|Affects consistency." in output
        assert "QUESTION|WHY_IT_MATTERS" in output


class TestRoundtrip:
    """Tests for roundtrip parse -> render -> parse."""

    def test_roundtrip_parse_render_parse(self) -> None:
        """parse_memory_document(render_memory_document(doc)) succeeds."""
        original = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="User prefers critical feedback.",
            evidence="2026-05-26 Chat",
        )
        project_entry = MemoryEntry(
            scope="P:myproject",
            type=MemoryType.PREF,
            priority=Priority.M,
            stability=Stability.M,
            statement="Use tabs for indentation.",
            evidence="2026-05-20 Chat",
        )
        deprecated_original = MemoryEntry(
            scope="G",
            type=MemoryType.FACT,
            priority=Priority.L,
            stability=Stability.T,
            statement="Old fact.",
            evidence="Evidence.",
        )
        deprecated = DeprecatedMemoryEntry(
            entry=deprecated_original,
            deprecation_reason="Replaced.",
        )
        doc = MemoryDocument(
            global_entries=[original],
            project_entries=[project_entry],
            deprecated_entries=[deprecated],
            open_questions=[("Open question?", "Why matters.")],
        )

        rendered = render_memory_document(doc)
        reparsed = parse_memory_document(rendered)

        assert len(reparsed.global_entries) == 1
        assert reparsed.global_entries[0].scope == "G"
        assert reparsed.global_entries[0].type == MemoryType.RULE
        assert reparsed.global_entries[0].priority == Priority.H
        assert reparsed.global_entries[0].stability == Stability.D
        assert reparsed.global_entries[0].statement == "User prefers critical feedback."

        assert len(reparsed.project_entries) == 1
        assert reparsed.project_entries[0].scope == "P:myproject"

        assert len(reparsed.deprecated_entries) == 1
        assert reparsed.deprecated_entries[0].deprecation_reason == "Replaced."

        assert len(reparsed.open_questions) == 1
        assert reparsed.open_questions[0] == ("Open question?", "Why matters.")
