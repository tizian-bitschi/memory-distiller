"""Tests for run_log module and Results tab integration."""

from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from unittest.mock import MagicMock

from memory_distiller.ui.run_log import (
    RunLogEvent,
    append_run_log_event,
    build_run_log_json,
    build_run_log_markdown,
    clear_run_log,
)


class TestRunLogEventCreation:
    """Test RunLogEvent creation and dict shape."""

    def test_run_log_event_with_all_fields(self):
        """RunLogEvent can be created with all fields."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="extract",
            event_type="start",
            summary="Extraction started",
            details={"key": "value"},
        )
        assert event.timestamp_iso == "2026-05-29T10:00:00Z"
        assert event.step == "extract"
        assert event.event_type == "start"
        assert event.summary == "Extraction started"
        assert event.details == {"key": "value"}

    def test_run_log_event_details_defaults_to_none(self):
        """details defaults to None when not provided."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="extract",
            event_type="start",
            summary="Extraction started",
        )
        assert event.details is None

    def test_run_log_event_asdict(self):
        """RunLogEvent can be converted to dict with asdict."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="validate",
            event_type="complete",
            summary="Validation complete",
            details={"count": 5},
        )
        d = asdict(event)
        assert d["timestamp_iso"] == "2026-05-29T10:00:00Z"
        assert d["step"] == "validate"
        assert d["event_type"] == "complete"
        assert d["summary"] == "Validation complete"
        assert d["details"] == {"count": 5}


class TestAppendRunLogEvent:
    """Test append_run_log_event adds to session state."""

    def test_append_run_log_event_adds_to_session_state(self, monkeypatch):
        """append_run_log_event adds event to RUN_LOG_EVENTS list."""
        mock_state = {}

        # Need to handle both attribute access and dict-like access
        class MockSessionState:
            def get(self, key, default=None):
                return mock_state.get(key, default)

            def __contains__(self, key):
                return key in mock_state

            def __getitem__(self, key):
                return mock_state[key]

            def __setitem__(self, key, value):
                mock_state[key] = value

        mock_st = MagicMock()
        mock_st.session_state = MockSessionState()

        monkeypatch.setattr("memory_distiller.ui.run_log.st", mock_st)
        monkeypatch.setattr("memory_distiller.ui.state.st", mock_st)

        from memory_distiller.ui.state import RUN_LOG_EVENTS

        # Call the function
        append_run_log_event(
            step="extract",
            event_type="start",
            summary="Extraction started",
        )

        # Verify event was added
        assert RUN_LOG_EVENTS in mock_state
        events = mock_state[RUN_LOG_EVENTS]
        assert len(events) == 1
        event = events[0]
        assert event.step == "extract"
        assert event.event_type == "start"
        assert event.summary == "Extraction started"
        # Verify timestamp was auto-generated
        assert event.timestamp_iso is not None
        assert event.timestamp_iso != ""


class TestClearRunLog:
    """Test clear_run_log clears events."""

    def test_clear_run_log_clears_events(self, monkeypatch):
        """clear_run_log empties the RUN_LOG_EVENTS list."""
        from memory_distiller.ui.state import RUN_LOG_EVENTS

        # RUN_LOG_EVENTS is "run_log_events" in state.py
        mock_state = {"run_log_events": [MagicMock(), MagicMock()]}

        class MockSessionStateWithData:
            def __contains__(self, key):
                return key in mock_state

            def __getitem__(self, key):
                return mock_state[key]

            def __setitem__(self, key, value):
                mock_state[key] = value

        mock_st = MagicMock()
        mock_st.session_state = MockSessionStateWithData()

        monkeypatch.setattr("memory_distiller.ui.run_log.st", mock_st)
        monkeypatch.setattr("memory_distiller.ui.state.st", mock_st)

        clear_run_log()

        assert RUN_LOG_EVENTS in mock_state
        assert mock_state[RUN_LOG_EVENTS] == []


class TestBuildRunLogMarkdown:
    """Test build_run_log_markdown output."""

    def test_markdown_includes_title(self):
        """build_run_log_markdown includes '# Memory Distiller Debug Run' title."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            )
        ]
        md = build_run_log_markdown(events)
        assert "# Memory Distiller Debug Run" in md

    def test_markdown_includes_event_count(self):
        """build_run_log_markdown includes event count."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            ),
            RunLogEvent(
                timestamp_iso="2026-05-29T10:01:00Z",
                step="extract",
                event_type="complete",
                summary="Extraction complete",
            ),
        ]
        md = build_run_log_markdown(events)
        assert "Events: 2" in md

    def test_markdown_includes_step_name(self):
        """build_run_log_markdown includes step name for each event."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="validate",
            event_type="start",
            summary="Validation started",
        )
        md = build_run_log_markdown([event])
        assert "**Step:** validate" in md

    def test_markdown_includes_event_type(self):
        """build_run_log_markdown includes event type for each event."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="extract",
            event_type="start",
            summary="Extraction started",
        )
        md = build_run_log_markdown([event])
        assert "**Event Type:** start" in md

    def test_markdown_includes_rendered_prompt_details(self):
        """build_run_log_markdown renders prompt/response details when present."""
        event = RunLogEvent(
            timestamp_iso="2026-05-29T10:00:00Z",
            step="extract",
            event_type="complete",
            summary="Extraction complete",
            details={"rendered_prompt": "test prompt content"},
        )
        md = build_run_log_markdown([event])
        assert "test prompt content" in md
        assert "Details" in md


class TestBuildRunLogJson:
    """Test build_run_log_json output."""

    def test_json_is_valid_json(self):
        """build_run_log_json output can be parsed with json.loads."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            )
        ]
        json_str = build_run_log_json(events)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_json_has_schema_version(self):
        """JSON export has schema_version == 1."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            )
        ]
        json_str = build_run_log_json(events)
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == 1

    def test_json_has_events_list(self):
        """JSON export has events as a list."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            )
        ]
        json_str = build_run_log_json(events)
        parsed = json.loads(json_str)
        assert isinstance(parsed["events"], list)
        assert len(parsed["events"]) == 1

    def test_json_has_generated_at(self):
        """JSON export has generated_at timestamp."""
        events = [
            RunLogEvent(
                timestamp_iso="2026-05-29T10:00:00Z",
                step="extract",
                event_type="start",
                summary="Extraction started",
            )
        ]
        json_str = build_run_log_json(events)
        parsed = json.loads(json_str)
        assert "generated_at" in parsed
        assert parsed["generated_at"] != ""


class TestSecretRedaction:
    """Test secret-looking keys and values are redacted."""

    def test_secret_keys_are_redacted(self, monkeypatch):
        """api_key, secret, token, password, auth, credential, env keys are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        sensitive_details = {
            "api_key": "sk-abc123",
            "secret": "my-secret",
            "token": " bearer-token",
            "password": "hunter2",
            "auth": "basic auth",
            "credential_pair": "user:pass",
            "env_vars": "FOO=bar",
        }
        result = _sanitize_details(sensitive_details)
        assert result["api_key"] == "[REDACTED]"
        assert result["secret"] == "[REDACTED]"
        assert result["token"] == "[REDACTED]"
        assert result["password"] == "[REDACTED]"
        assert result["auth"] == "[REDACTED]"
        assert result["credential_pair"] == "[REDACTED]"
        assert result["env_vars"] == "[REDACTED]"

    def test_env_var_assignment_pattern_is_redacted(self, monkeypatch):
        """DEEPSEEK_API_KEY=sk-abc123 style values are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {
            "env_var": "DEEPSEEK_API_KEY=sk-abc123",
        }
        result = _sanitize_details(details)
        assert result["env_var"] == "[REDACTED]"

    def test_known_secret_key_names_as_values_are_redacted(self, monkeypatch):
        """Known secret key names (DEEPSEEK_API_KEY, etc.) as values are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {
            "key_name": "DEEPSEEK_API_KEY",
        }
        result = _sanitize_details(details)
        assert result["key_name"] == "[REDACTED]"

        details2 = {"name": "OPENAI_API_KEY"}
        result2 = _sanitize_details(details2)
        assert result2["name"] == "[REDACTED]"

    def test_non_secret_details_preserved(self, monkeypatch):
        """Non-secret details are preserved without redaction."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {
            "step": "extract",
            "event_type": "start",
            "count": 42,
        }
        result = _sanitize_details(details)
        assert result["step"] == "extract"
        assert result["event_type"] == "start"
        assert result["count"] == 42

    def test_nested_dict_secret_key_redaction(self):
        """Nested dict api_key values are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {"outer": {"api_key": "sk-abc123"}}
        result = _sanitize_details(details)
        assert result["outer"]["api_key"] == "[REDACTED]"

    def test_list_secret_redaction(self):
        """List items with secret keys are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {"items": [{"password": "hunter2"}, "Authorization: Bearer abc123"]}
        result = _sanitize_details(details)
        assert result["items"][0]["password"] == "[REDACTED]"
        assert "[REDACTED]" in result["items"][1]
        assert "abc123" not in result["items"][1]

    def test_string_substring_redaction(self):
        """Secret-looking substrings inside longer strings are redacted."""
        from memory_distiller.ui.run_log import _sanitize_details

        details = {"rendered_prompt": "Please use DEEPSEEK_API_KEY=sk-abc123"}
        result = _sanitize_details(details)
        assert "sk-abc123" not in result["rendered_prompt"]
        assert "[REDACTED]" in result["rendered_prompt"]


class TestResultsTabDebugRunLog:
    """Test Results tab Debug Run Log integration."""

    def test_results_tab_contains_debug_run_log_section(self):
        """Source inspection: 'Debug Run Log' appears in render_results_tab source."""
        from memory_distiller.ui.tabs.results_tab import render_results_tab

        source = inspect.getsource(render_results_tab)
        assert "Debug Run Log" in source

    def test_results_tab_offers_debug_run_md_download(self):
        """Source inspection: 'Download debug_run.md' appears in source."""
        from memory_distiller.ui.tabs.results_tab import render_results_tab

        source = inspect.getsource(render_results_tab)
        assert "Download debug_run.md" in source

    def test_results_tab_offers_debug_run_json_download(self):
        """Source inspection: 'Download debug_run.json' appears in source."""
        from memory_distiller.ui.tabs.results_tab import render_results_tab

        source = inspect.getsource(render_results_tab)
        assert "Download debug_run.json" in source

    def test_results_tab_includes_privacy_warning(self):
        """Source inspection: 'Privacy notice' or 'private chat content' appears in source."""
        from memory_distiller.ui.tabs.results_tab import render_results_tab

        source = inspect.getsource(render_results_tab)
        assert "Privacy notice" in source or "private chat content" in source


class TestLoggingHelperInTabs:
    """Test append_run_log_event is called in each tab."""

    def test_extract_tab_calls_append_run_log_event(self):
        """Source inspection: append_run_log_event appears in extract_tab source."""
        from memory_distiller.ui.tabs import extract_tab

        source = inspect.getsource(extract_tab)
        assert "append_run_log_event" in source

    def test_validate_tab_calls_append_run_log_event(self):
        """Source inspection: append_run_log_event appears in validate_tab source."""
        from memory_distiller.ui.tabs import validate_tab

        source = inspect.getsource(validate_tab)
        assert "append_run_log_event" in source

    def test_merge_tab_calls_append_run_log_event(self):
        """Source inspection: append_run_log_event appears in merge_tab source."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        assert "append_run_log_event" in source

    def test_compress_tab_calls_append_run_log_event(self):
        """Source inspection: append_run_log_event appears in compress_tab source."""
        from memory_distiller.ui.tabs import compress_tab

        source = inspect.getsource(compress_tab)
        assert "append_run_log_event" in source


class TestMergeTabTerminology:
    """Test Merge tab logging uses merge plan terminology."""

    def test_merge_tab_uses_merge_plan_terminology(self):
        """Source inspection: 'merge_plan' or 'Merge plan' in merge_tab source."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        # Look for merge_plan in logging calls
        assert "merge_plan" in source or "Merge plan" in source

    def test_merge_tab_logging_does_not_use_old_terminology(self):
        """Append_run_log_event calls in merge_tab do not use old
        'MEMORY_FULL-as-LLM-response' terminology."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        # Find all append_run_log_event calls
        assert "append_run_log_event" in source
        # The old terminology should NOT appear as a detail value in log calls
        assert "MEMORY_FULL-as-LLM-response" not in source


class TestMergeTabMergePlanEntryCount:
    """Test merge_tab includes merge_plan_entry_count in success logs."""

    def test_merge_tab_merge_plan_entry_counts_from_plan_entries(self):
        """merge_plan_entry_count comes from len(plan.entries), not MemoryDocument."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        # Should reference plan.entries or parse_merge_plan for entry count
        assert "plan.entries" in source or "parse_merge_plan" in source

    def test_prompt_only_merge_success_includes_merge_plan_entry_count(self):
        """Prompt-only merge success log includes merge_plan_entry_count."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        # Find the apply_merge_plan success block and check for merge_plan_entry_count
        apply_idx = source.find('event_type="apply_merge_plan"')
        success_idx = source.find('parse_status": "success"', apply_idx)
        assert success_idx != -1
        section = source[apply_idx : success_idx + 200]
        assert "merge_plan_entry_count" in section

    def test_api_merge_success_includes_merge_plan_entry_count(self):
        """API merge success log includes merge_plan_entry_count."""
        from memory_distiller.ui.tabs import merge_tab

        source = inspect.getsource(merge_tab)
        # Find the API success block
        api_idx = source.find('event_type="api_response"')
        success_idx = source.find("parse_status", api_idx)
        assert success_idx != -1
        section = source[api_idx : success_idx + 300]
        assert "merge_plan_entry_count" in section
