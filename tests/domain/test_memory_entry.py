"""Tests for memory entry domain models."""

import pytest

from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.memory_entry import (
    DeprecatedMemoryEntry,
    MemoryDocument,
    MemoryEntry,
)


class TestMemoryEntryCreation:
    """Tests for MemoryEntry creation with valid data."""

    def test_create_memory_entry(self):
        """MemoryEntry creation with valid data."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="User prefers critical feedback.",
            evidence="2026-05-26 Chat",
        )
        assert entry.scope == "G"
        assert entry.type == MemoryType.RULE
        assert entry.priority == Priority.H
        assert entry.stability == Stability.D
        assert entry.statement == "User prefers critical feedback."
        assert entry.evidence == "2026-05-26 Chat"

    def test_create_memory_entry_project_scope(self):
        """MemoryEntry with project scope."""
        entry = MemoryEntry(
            scope="P:myproject",
            type=MemoryType.PREF,
            priority=Priority.M,
            stability=Stability.M,
            statement="Use tabs for indentation.",
            evidence="2026-05-20 Chat",
        )
        assert entry.scope == "P:myproject"
        assert entry.type == MemoryType.PREF

    def test_create_memory_entry_repo_scope(self):
        """MemoryEntry with repo scope."""
        entry = MemoryEntry(
            scope="R:backend-api",
            type=MemoryType.FACT,
            priority=Priority.L,
            stability=Stability.T,
            statement="Endpoint returns JSON.",
            evidence="2026-05-22 Code review",
        )
        assert entry.scope == "R:backend-api"
        assert entry.type == MemoryType.FACT


class TestMemoryEntryFrozen:
    """Tests for MemoryEntry immutability."""

    def test_memory_entry_is_frozen(self):
        """MemoryEntry is frozen (immutable)."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test statement.",
            evidence="Test evidence.",
        )
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            entry.statement = "Modified"  # type: ignore

    def test_memory_entry_hashable(self):
        """Frozen entries are hashable."""
        entry1 = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test statement.",
            evidence="Test evidence.",
        )
        entry2 = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test statement.",
            evidence="Test evidence.",
        )
        assert hash(entry1) == hash(entry2)


class TestDeprecatedMemoryEntry:
    """Tests for DeprecatedMemoryEntry."""

    def test_create_deprecated_memory_entry(self):
        """DeprecatedMemoryEntry creation."""
        original = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Old rule.",
            evidence="Old evidence.",
        )
        deprecated = DeprecatedMemoryEntry(
            entry=original,
            deprecation_reason="Replaced by new rule.",
        )
        assert deprecated.entry == original
        assert deprecated.deprecation_reason == "Replaced by new rule."

    def test_deprecated_memory_entry_is_frozen(self):
        """DeprecatedMemoryEntry is frozen."""
        original = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Old rule.",
            evidence="Old evidence.",
        )
        deprecated = DeprecatedMemoryEntry(
            entry=original,
            deprecation_reason="Replaced by new rule.",
        )
        with pytest.raises(Exception):
            deprecated.deprecation_reason = "Modified"  # type: ignore


class TestMemoryDocument:
    """Tests for MemoryDocument."""

    def test_create_memory_document_with_defaults(self):
        """MemoryDocument creation with defaults."""
        doc = MemoryDocument()
        assert doc.global_entries == []
        assert doc.project_entries == []
        assert doc.repo_entries == []
        assert doc.temporary_entries == []
        assert doc.deprecated_entries == []
        assert doc.open_questions == []

    def test_create_memory_document_with_entries(self):
        """MemoryDocument creation with entries."""
        entry = MemoryEntry(
            scope="G",
            type=MemoryType.RULE,
            priority=Priority.H,
            stability=Stability.D,
            statement="Test rule.",
            evidence="Test evidence.",
        )
        deprecated_entry = DeprecatedMemoryEntry(
            entry=MemoryEntry(
                scope="G",
                type=MemoryType.PREF,
                priority=Priority.M,
                stability=Stability.M,
                statement="Old pref.",
                evidence="Old evidence.",
            ),
            deprecation_reason="No longer needed.",
        )
        doc = MemoryDocument(
            global_entries=[entry],
            project_entries=[],
            repo_entries=[],
            temporary_entries=[],
            deprecated_entries=[deprecated_entry],
            open_questions=[("Question 1?", "Why it matters 1.")],
        )
        assert len(doc.global_entries) == 1
        assert doc.global_entries[0] == entry
        assert len(doc.deprecated_entries) == 1
        assert len(doc.open_questions) == 1
        assert doc.open_questions[0] == ("Question 1?", "Why it matters 1.")
