"""Tests for enum alias suggestions and normalization."""

from memory_distiller.io.enum_aliases import (
    normalize_candidate_lines,
    normalize_memory_document,
    suggest_priority_alias,
    suggest_scope_alias,
    suggest_stability_alias,
    suggest_type_alias,
)


class TestSuggestTypeAlias:
    """Tests for suggest_type_alias function."""

    def test_suggest_type_alias_preference(self):
        """PREFERENCE maps to PREF."""
        assert suggest_type_alias("PREFERENCE") == "PREF"

    def test_suggest_type_alias_prefs(self):
        """PREFS maps to PREF."""
        assert suggest_type_alias("PREFS") == "PREF"

    def test_suggest_type_alias_case_insensitive(self):
        """Case-insensitive: 'preference' -> PREF."""
        assert suggest_type_alias("preference") == "PREF"

    def test_suggest_type_alias_unknown(self):
        """Unknown type returns None."""
        assert suggest_type_alias("BANANA") is None


class TestSuggestScopeAlias:
    """Tests for suggest_scope_alias function."""

    def test_suggest_scope_alias_global(self):
        """GLOBAL maps to G."""
        assert suggest_scope_alias("GLOBAL") == "G"

    def test_suggest_scope_alias_project(self):
        """PROJECT:RecipeBot maps to P:RecipeBot."""
        assert suggest_scope_alias("PROJECT:RecipeBot") == "P:RecipeBot"

    def test_suggest_scope_alias_repo(self):
        """REPO:memory-distiller maps to R:memory-distiller."""
        assert suggest_scope_alias("REPO:memory-distiller") == "R:memory-distiller"

    def test_suggest_scope_alias_repository(self):
        """REPOSITORY:x maps to R:x."""
        assert suggest_scope_alias("REPOSITORY:x") == "R:x"

    def test_suggest_scope_alias_temporary(self):
        """TEMPORARY maps to T."""
        assert suggest_scope_alias("TEMPORARY") == "T"

    def test_suggest_scope_alias_unknown(self):
        """Unknown scope returns None."""
        assert suggest_scope_alias("RANDOM_SCOPE") is None


class TestSuggestPriorityAlias:
    """Tests for suggest_priority_alias function."""

    def test_suggest_priority_alias_high(self):
        """HIGH maps to H."""
        assert suggest_priority_alias("HIGH") == "H"

    def test_suggest_priority_alias_medium(self):
        """MEDIUM maps to M."""
        assert suggest_priority_alias("MEDIUM") == "M"

    def test_suggest_priority_alias_low(self):
        """LOW maps to L."""
        assert suggest_priority_alias("LOW") == "L"

    def test_suggest_priority_alias_unknown(self):
        """Unknown priority returns None."""
        assert suggest_priority_alias("IMPORTANT") is None


class TestSuggestStabilityAlias:
    """Tests for suggest_stability_alias function."""

    def test_suggest_stability_alias_stable(self):
        """STABLE maps to D."""
        assert suggest_stability_alias("STABLE") == "D"

    def test_suggest_stability_alias_durable(self):
        """DURABLE maps to D."""
        assert suggest_stability_alias("DURABLE") == "D"

    def test_suggest_stability_alias_medium_term(self):
        """MEDIUM_TERM maps to M."""
        assert suggest_stability_alias("MEDIUM_TERM") == "M"

    def test_suggest_stability_alias_temporary(self):
        """TEMPORARY maps to T."""
        assert suggest_stability_alias("TEMPORARY") == "T"

    def test_suggest_stability_alias_unknown(self):
        """Unknown stability returns None."""
        assert suggest_stability_alias("ALWAYS") is None


class TestNormalizeCandidateLines:
    """Tests for normalize_candidate_lines function."""

    def test_normalize_candidate_basic(self):
        """Basic candidate normalization."""
        raw = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY"
            "|STATEMENT|EVIDENCE|REASON\n"
            "M1|ADD|-|PROJECT:Proj|PREFERENCE|HIGH|STABLE"
            "|Use units.|User said.|Project pref."
        )
        expected = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY"
            "|STATEMENT|EVIDENCE|REASON\n"
            "M1|ADD|-|P:Proj|PREF|H|D"
            "|Use units.|User said.|Project pref."
        )
        result, changes = normalize_candidate_lines(raw)
        assert result == expected
        assert len(changes) == 4

    def test_normalize_validated_candidate(self):
        """Validated candidate normalization."""
        raw = (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY"
            "|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "M1|KEEP|ADD|-|PROJECT:Proj|PREFERENCE|HIGH|STABLE"
            "|Use units.|User said.|Project pref."
        )
        expected = (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIORITY"
            "|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "M1|KEEP|ADD|-|P:Proj|PREF|H|D"
            "|Use units.|User said.|Project pref."
        )
        result, changes = normalize_candidate_lines(raw)
        assert result == expected
        assert len(changes) == 4

    def test_normalize_candidate_no_changes(self):
        """Already canonical candidate - no changes."""
        raw = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "M1|ADD|-|G|RULE|H|D|Use metric units.|User said so.|Project preference."
        )
        result, changes = normalize_candidate_lines(raw)
        assert result == raw
        assert len(changes) == 0

    def test_normalize_candidate_free_text_preserved(self):
        """Free text containing alias words is not modified."""
        raw = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "M1|ADD|-|G|RULE|H|D|Do not use PREFERENCE in docs.|User said so.|GLOBAL reason."
        )
        result, changes = normalize_candidate_lines(raw)
        assert result == raw
        assert len(changes) == 0

    def test_normalize_candidate_unknown_values_unchanged(self):
        """Unknown type not changed, but known aliases still repaired."""
        raw = (
            "ID|ACTION|TARGET|SCOPE|TYPE|PRIORITY|STABILITY|STATEMENT|EVIDENCE|REASON\n"
            "M1|ADD|-|P:Proj|BANANA|H|D|Use metric units.|User said so.|Project preference."
        )
        result, changes = normalize_candidate_lines(raw)
        # Type BANANA should be unchanged
        assert "BANANA" in result
        # But scope and priority/stability should still be normalized
        assert "P:Proj" in result
        assert "H" in result
        assert "D" in result


class TestNormalizeMemoryDocument:
    """Tests for normalize_memory_document function."""

    def test_normalize_memory_document_basic(self):
        """Basic memory document normalization."""
        raw = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
GLOBAL|RULE|HIGH|STABLE|Global rule.|Evidence.

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
PROJECT:RecipeBot|PREFERENCE|MEDIUM|DURABLE|Project pref.|Evidence.
"""
        result, changes = normalize_memory_document(raw)
        assert "G" in result  # GLOBAL -> G
        assert "P:RecipeBot" in result  # PROJECT:RecipeBot -> P:RecipeBot
        assert "PREF" in result  # PREFERENCE -> PREF
        assert "H" in result  # HIGH -> H
        assert "D" in result  # STABLE/DURABLE -> D
        assert "M" in result  # MEDIUM -> M

    def test_normalize_memory_document_free_text_preserved(self):
        """Free text containing alias words is not modified."""
        raw = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Do not use PREFERENCE in docs.|Evidence.
"""
        result, changes = normalize_memory_document(raw)
        # Result may have trailing newline stripped
        assert "PREFERENCE" in result
        assert len(changes) == 0

    def test_normalize_memory_document_no_changes(self):
        """Already canonical document - no changes."""
        raw = """# MEMORY_FULL
## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Global rule.|Evidence.

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:RecipeBot|PREF|M|D|Project pref.|Evidence.
"""
        result, changes = normalize_memory_document(raw)
        # Result may have trailing newline stripped
        assert "G|RULE|H|D|Global rule.|Evidence." in result
        assert "P:RecipeBot|PREF|M|D|Project pref.|Evidence." in result
        assert len(changes) == 0
