"""Parse error types for memory-distiller."""

from __future__ import annotations


class ParseError(Exception):
    """Represents a single parsing error.

    Attributes:
        line_number: The line number where the error occurred.
        line: The original line content.
        message: Human-readable error message.
    """

    def __init__(self, line_number: int, line: str, message: str) -> None:
        self.line_number = line_number
        self.line = line
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with line number."""
        return f"Line {self.line_number}: {self.message}"

    def __str__(self) -> str:
        return self._format_message()


class ParseErrorCollection(Exception):  # noqa: N818
    """Collects multiple ParseError instances.

    Can be raised as a single exception containing all errors.

    Attributes:
        errors: List of ParseError instances.
    """

    def __init__(self, errors: list[ParseError] | None = None) -> None:
        self.errors = errors if errors is not None else []
        super().__init__(self._format_all())

    def add(self, error: ParseError) -> None:
        """Add a ParseError to the collection."""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self.errors) > 0

    def _format_all(self) -> str:
        """Format all error messages."""
        if not self.errors:
            return "No errors"
        return "\n".join(str(e) for e in self.errors)

    def __str__(self) -> str:
        return self._format_all()
