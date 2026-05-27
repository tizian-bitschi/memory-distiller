"""Tests for domain enums."""

from memory_distiller.domain.enums import (
    CandidateAction,
    MemoryType,
    Priority,
    Stability,
    ValidationVerdict,
)


class TestMemoryType:
    """Tests for MemoryType enum."""

    def test_expected_values(self):
        """Enum has expected values."""
        assert MemoryType.RULE.value == "RULE"
        assert MemoryType.PREF.value == "PREF"
        assert MemoryType.FACT.value == "FACT"
        assert MemoryType.DECISION.value == "DECISION"
        assert MemoryType.AVOID.value == "AVOID"
        assert MemoryType.STYLE.value == "STYLE"
        assert MemoryType.SOURCE.value == "SOURCE"
        assert MemoryType.TERM.value == "TERM"
        assert MemoryType.TASK.value == "TASK"
        assert MemoryType.CONFLICT.value == "CONFLICT"

    def test_values_match_parsing(self):
        """Enum values match string representations used in parsing."""
        for member in MemoryType:
            # The enum value should be parseable back
            parsed = MemoryType(member.value)
            assert parsed == member


class TestPriority:
    """Tests for Priority enum."""

    def test_expected_values(self):
        """Enum has expected values."""
        assert Priority.H.value == "H"
        assert Priority.M.value == "M"
        assert Priority.L.value == "L"

    def test_values_match_parsing(self):
        """Enum values match string representations used in parsing."""
        for member in Priority:
            parsed = Priority(member.value)
            assert parsed == member


class TestStability:
    """Tests for Stability enum."""

    def test_expected_values(self):
        """Enum has expected values."""
        assert Stability.D.value == "D"
        assert Stability.M.value == "M"
        assert Stability.T.value == "T"

    def test_values_match_parsing(self):
        """Enum values match string representations used in parsing."""
        for member in Stability:
            parsed = Stability(member.value)
            assert parsed == member


class TestCandidateAction:
    """Tests for CandidateAction enum."""

    def test_expected_values(self):
        """Enum has expected values."""
        assert CandidateAction.ADD.value == "ADD"
        assert CandidateAction.UPDATE.value == "UPDATE"
        assert CandidateAction.DEPRECATE.value == "DEPRECATE"
        assert CandidateAction.IGNORE.value == "IGNORE"
        assert CandidateAction.CONFLICT.value == "CONFLICT"
        assert CandidateAction.ASK.value == "ASK"

    def test_values_match_parsing(self):
        """Enum values match string representations used in parsing."""
        for member in CandidateAction:
            parsed = CandidateAction(member.value)
            assert parsed == member


class TestValidationVerdict:
    """Tests for ValidationVerdict enum."""

    def test_expected_values(self):
        """Enum has expected values."""
        assert ValidationVerdict.KEEP.value == "KEEP"
        assert ValidationVerdict.EDIT.value == "EDIT"
        assert ValidationVerdict.DROP.value == "DROP"
        assert ValidationVerdict.ASK.value == "ASK"
        assert ValidationVerdict.CONFLICT.value == "CONFLICT"

    def test_values_match_parsing(self):
        """Enum values match string representations used in parsing."""
        for member in ValidationVerdict:
            parsed = ValidationVerdict(member.value)
            assert parsed == member
