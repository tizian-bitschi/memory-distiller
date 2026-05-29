"""Pipeline run log for debugging and auditing."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from memory_distiller.ui.state import RUN_LOG_EVENTS


@dataclass(frozen=True)
class RunLogEvent:
    """A single event in the pipeline run log."""

    timestamp_iso: str
    step: str
    event_type: str
    summary: str
    details: dict[str, Any] | None = None


def _sanitize_details(details: dict[str, Any] | None) -> dict[str, Any] | None:
    """Redact secret-looking keys and values from details dict.

    Args:
        details: Dictionary to sanitize.

    Returns:
        New dictionary with secrets redacted, or None if input was None.
    """
    if details is None:
        return None

    # Keys that suggest secrets (case-insensitive)
    secret_key_patterns = (
        "api_key",
        "apikey",
        "secret",
        "token",
        "password",
        "auth",
        "credential",
        "env",
    )

    # Patterns for finding secrets in string values
    _value_patterns = (
        # API_KEY assignments: DEEPSEEK_API_KEY=sk-abc123
        re.compile(r"\b[A-Z_]+_API_KEY\s*=\s*[^\s]+"),
        # API_KEY as standalone word
        re.compile(r"\b[A-Z_]+_API_KEY\b"),
        # Authorization header: Authorization: Bearer abc123
        re.compile(r"Authorization:\s*Bearer\s+[^\s]+"),
        # Generic secret patterns: api_key: sk-abc123, password=x, token=abc
        re.compile(r"\b(api_key|apikey|secret|token|password|auth|credential|env)\s*[:=]\s*[^\s]+"),
    )

    def _is_secret_key(key: str) -> bool:
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in secret_key_patterns)

    def _sanitize_value(value: Any) -> Any:
        # Recurse into dicts
        if isinstance(value, dict):
            return _sanitize_dict(value)
        # Recurse into lists
        if isinstance(value, list):
            return [_sanitize_value(item) for item in value]
        # Recurse into tuples (convert to list, sanitize, back to tuple)
        if isinstance(value, tuple):
            return tuple(_sanitize_value(item) for item in value)
        # Sanitize strings
        if isinstance(value, str):
            sanitized = value
            for pattern in _value_patterns:
                sanitized = pattern.sub("[REDACTED]", sanitized)
            return sanitized
        # Pass through primitives unchanged
        return value

    def _sanitize_dict(d: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in d.items():
            if _is_secret_key(key):
                result[key] = "[REDACTED]"
            else:
                result[key] = _sanitize_value(value)
        return result

    return _sanitize_dict(details)


def append_run_log_event(
    step: str,
    event_type: str,
    summary: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Add an event to the pipeline run log.

    Args:
        step: Pipeline step name (e.g., 'extract', 'validate').
        event_type: Type of event (e.g., 'start', 'complete', 'error').
        summary: Human-readable summary of the event.
        details: Optional dictionary with additional event details.
    """
    if RUN_LOG_EVENTS not in st.session_state:
        st.session_state[RUN_LOG_EVENTS] = []

    sanitized_details = _sanitize_details(details)

    event = RunLogEvent(
        timestamp_iso=datetime.now(timezone.utc).isoformat(),
        step=step,
        event_type=event_type,
        summary=summary,
        details=sanitized_details,
    )

    st.session_state[RUN_LOG_EVENTS].append(event)


def clear_run_log() -> None:
    """Clear all events from the pipeline run log."""
    if RUN_LOG_EVENTS in st.session_state:
        st.session_state[RUN_LOG_EVENTS] = []


def build_run_log_markdown(events: list[RunLogEvent]) -> str:
    """Build a human-readable markdown string from run log events.

    Args:
        events: List of RunLogEvent instances.

    Returns:
        Markdown string with title, generated timestamp, event count,
        and per-event sections.
    """
    generated_at = datetime.now(timezone.utc).isoformat()
    event_count = len(events)

    lines = [
        "# Memory Distiller Debug Run",
        "",
        f"Generated: {generated_at}",
        f"Events: {event_count}",
        "",
    ]

    for i, event in enumerate(events, 1):
        lines.append(f"## Event {i}")
        lines.append(f"**Timestamp:** {event.timestamp_iso}")
        lines.append(f"**Step:** {event.step}")
        lines.append(f"**Event Type:** {event.event_type}")
        lines.append(f"**Summary:** {event.summary}")

        if event.details is not None:
            details_str = json.dumps(event.details, indent=2)
            lines.append("**Details:**")
            lines.append("```")
            lines.append(details_str)
            lines.append("```")

        lines.append("")

    return "\n".join(lines)


def build_run_log_json(events: list[RunLogEvent]) -> str:
    """Build a JSON string from run log events.

    Args:
        events: List of RunLogEvent instances.

    Returns:
        JSON string with schema_version=1, generated_at, and events array.
    """
    output: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "events": [asdict(event) for event in events],
    }

    return json.dumps(output, indent=2)
