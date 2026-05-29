"""Tests for merge applier."""

import pytest

from memory_distiller.application.merge_applier import apply_merge_plan
from memory_distiller.domain.enums import MemoryType, Priority, Stability
from memory_distiller.domain.memory_entry import (
    MemoryEntry,
)
from memory_distiller.domain.merge_plan import MergeDecision, MergePlan, MergePlanEntry


def make_entry(
    scope: str = "G",
    mem_type: str = "RULE",
    priority: str = "H",
    stability: str = "D",
    statement: str = "Test statement.",
    evidence: str = "Test evidence.",
) -> MemoryEntry:
    """Helper to create a MemoryEntry."""
    return MemoryEntry(
        scope=scope,
        type=MemoryType(mem_type),
        priority=Priority(priority),
        stability=Stability(stability),
        statement=statement,
        evidence=evidence,
    )


def make_plan_entry(
    decision: MergeDecision,
    statement: str,
    target: str = "-",
    scope: str = "G",
    mem_type: str = "RULE",
    priority: str = "H",
    stability: str = "D",
    evidence: str = "Test evidence.",
    reason: str = "Test reason.",
    candidate_id: str = "M1",
) -> MergePlanEntry:
    """Helper to create a MergePlanEntry."""
    return MergePlanEntry(
        candidate_id=candidate_id,
        decision=decision,
        target=target,
        scope=scope,
        type=mem_type,
        priority=priority,
        stability=stability,
        statement=statement,
        evidence=evidence,
        reason=reason,
    )


class TestApplyMergePlan:
    """Tests for apply_merge_plan function."""

    def test_apply_add_becomes_memory_entry(self) -> None:
        """APPLY_ADD adds to correct section."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="New global rule.",
                    scope="G",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        result = apply_merge_plan(existing, plan)

        assert len(result.global_entries) == 2
        assert any(e.statement == "New global rule." for e in result.global_entries)

    def test_apply_add_to_project_section(self) -> None:
        """APPLY_ADD adds to project section when scope is P:."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="Project rule.",
                    scope="P:RecipeBot",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Global rule.|Evidence.
"""
        result = apply_merge_plan(existing, plan)

        assert len(result.project_entries) == 1
        assert result.project_entries[0].statement == "Project rule."
        assert result.project_entries[0].scope == "P:RecipeBot"

    def test_apply_update_changes_existing(self) -> None:
        """APPLY_UPDATE replaces matching entry."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_UPDATE,
                    statement="Updated statement.",
                    target="Old statement.",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Old statement.|Old evidence.
"""
        result = apply_merge_plan(existing, plan)

        assert len(result.global_entries) == 1
        assert result.global_entries[0].statement == "Updated statement."

    def test_skip_drop_does_not_appear(self) -> None:
        """SKIP_DROP ignored."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.SKIP_DROP,
                    statement="This should not be added.",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        result = apply_merge_plan(existing, plan)

        assert len(result.global_entries) == 1
        assert not any(e.statement == "This should not be added." for e in result.global_entries)

    def test_add_open_question(self) -> None:
        """ADD_OPEN_QUESTION adds to open_questions."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.ADD_OPEN_QUESTION,
                    statement="Should we use tabs or spaces?",
                    reason="Affects consistency.",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        result = apply_merge_plan(existing, plan)

        assert len(result.open_questions) == 1
        assert result.open_questions[0] == ("Should we use tabs or spaces?", "Affects consistency.")

    def test_existing_global_entry_preserved(self) -> None:
        """Existing entries stay unless updated."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="New rule.",
                    scope="G",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        result = apply_merge_plan(existing, plan)

        # Original entry preserved
        assert len(result.global_entries) == 2
        assert any(e.statement == "Existing rule." for e in result.global_entries)
        assert any(e.statement == "New rule." for e in result.global_entries)

    def test_existing_project_entry_updated_not_duplicated(self) -> None:
        """Update replaces, doesn't duplicate."""
        existing = """# MEMORY_FULL
## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:RecipeBot|PREF|M|M|Old preference.|Old evidence.
"""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_UPDATE,
                    statement="New preference.",
                    target="Old preference.",
                    scope="P:RecipeBot",
                ),
            )
        )
        result = apply_merge_plan(existing, plan)

        # Only one entry, updated
        assert len(result.project_entries) == 1
        assert result.project_entries[0].statement == "New preference."

    def test_ambiguous_missing_update_target_raises(self) -> None:
        """Missing target raises ValueError."""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_UPDATE,
                    statement="Updated statement.",
                    target="Nonexistent statement.",
                ),
            )
        )
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        with pytest.raises(ValueError, match="No entry found with statement"):
            apply_merge_plan(existing, plan)

    def test_apply_deprecate_moves_entry(self) -> None:
        """APPLY_DEPRECATE moves to deprecated."""
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Old rule.|Old evidence.
"""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_DEPRECATE,
                    statement="Deprecated rule.",
                    target="Old rule.",
                    reason="No longer relevant.",
                ),
            )
        )
        result = apply_merge_plan(existing, plan)

        # Moved from global to deprecated
        assert len(result.global_entries) == 0
        assert len(result.deprecated_entries) == 1
        assert result.deprecated_entries[0].entry.statement == "Old rule."
        assert result.deprecated_entries[0].deprecation_reason == "No longer relevant."

    def test_duplicate_add_skipped(self) -> None:
        """Duplicate statement not added again."""
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Existing rule.|Evidence.
"""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="Existing rule.",  # Same statement
                    scope="G",
                ),
            )
        )
        result = apply_merge_plan(existing, plan)

        # Still only one entry (no duplicate)
        assert len(result.global_entries) == 1

    def test_multiple_entries_applied_in_order(self) -> None:
        """Multiple entries applied in order."""
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Original.|Evidence.
"""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="First addition.",
                    scope="G",
                    candidate_id="M1",
                ),
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="Second addition.",
                    scope="G",
                    candidate_id="M2",
                ),
            )
        )
        result = apply_merge_plan(existing, plan)

        assert len(result.global_entries) == 3

    def test_temporary_scope_entry(self) -> None:
        """Temporary scope entries handled correctly."""
        existing = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Global rule.|Evidence.
"""
        plan = MergePlan(
            entries=(
                make_plan_entry(
                    decision=MergeDecision.APPLY_ADD,
                    statement="Temp task.",
                    scope="T",
                    mem_type="TASK",
                ),
            )
        )
        result = apply_merge_plan(existing, plan)

        assert len(result.temporary_entries) == 1
        assert result.temporary_entries[0].statement == "Temp task."
