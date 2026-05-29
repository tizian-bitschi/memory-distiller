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

    # Pattern to match env var assignments like DEEPSEEK_API_KEY=value
    env_var_pattern = re.compile(r"^[A-Z_]+=.+")

    # Known secret key names to redact if they appear as values
    known_secret_values = {
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
    }

    result: dict[str, Any] = {}

    for key, value in details.items():
        # Check if key looks like a secret
        key_lower = key.lower()
        is_secret_key = any(pattern in key_lower for pattern in secret_key_patterns)

        if is_secret_key:
            result[key] = "[REDACTED]"
            continue

        # Check if value is a known secret key name
        if isinstance(value, str) and value in known_secret_values:
            result[key] = "[REDACTED]"
            continue

        # Check if value looks like an env var assignment
        if isinstance(value, str) and env_var_pattern.match(value):
            result[key] = "[REDACTED]"
            continue

        # Otherwise keep original value
        result[key] = value

    return result


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
