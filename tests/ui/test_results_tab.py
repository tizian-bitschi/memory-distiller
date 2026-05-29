"""Tests for results_tab module - Issue #27 fix verification."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock

from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    VALIDATED_CANDIDATES_RAW,
)
from memory_distiller.ui.tabs.results_tab import render_results_tab


class TestResultsSectionPreviewAndDownload:
    """Verify st.code and st.download_button are called correctly for content."""

    def test_results_section_shows_preview_and_download_for_content(self, monkeypatch):
        """st.code called with exact content, download_button with payload."""
        # Arrange
        calls = {"code": [], "download_button": [], "subheader": [], "caption": []}

        def mock_subheader(msg):
            calls["subheader"].append(msg)

        def mock_code(content, language=None):
            calls["code"].append({"content": content, "language": language})

        def mock_download_button(label, data=None, file_name=None, mime=None, key=None):
            calls["download_button"].append(
                {
                    "label": label,
                    "data": data,
                    "file_name": file_name,
                    "mime": mime,
                    "key": key,
                }
            )

        def mock_caption(msg):
            calls["caption"].append(msg)

        mock_st = MagicMock()
        mock_st.subheader = mock_subheader
        mock_st.code = mock_code
        mock_st.download_button = mock_download_button
        mock_st.caption = mock_caption
        mock_st.session_state.get = MagicMock(
            side_effect=lambda key, default="": {
                CANDIDATES_RAW: "candidates content",
                VALIDATED_CANDIDATES_RAW: "validated content",
                MEMORY_FULL_RAW: "memory full content",
                MEMORY_PROMPT_RAW: "memory prompt content",
            }.get(key, default)
        )

        # Import build_text_download_payload to verify payload generation
        from memory_distiller.io.file_export import build_text_download_payload

        monkeypatch.setattr("memory_distiller.ui.tabs.results_tab.st", mock_st)

        # Act
        render_results_tab()

        # Assert - Candidates Raw section
        assert "Candidates Raw" in calls["subheader"]
        assert any(
            c["content"] == "candidates content" and c["language"] == "text" for c in calls["code"]
        )
        assert any(
            d["label"] == "Download candidates.txt"
            and d["data"] == build_text_download_payload("candidates content")
            for d in calls["download_button"]
        )

        # Assert - Validated Candidates Raw section
        assert "Validated Candidates Raw" in calls["subheader"]
        assert any(
            c["content"] == "validated content" and c["language"] == "text" for c in calls["code"]
        )
        assert any(
            d["label"] == "Download validated_candidates.txt"
            and d["data"] == build_text_download_payload("validated content")
            for d in calls["download_button"]
        )

        # Assert - Memory Full Raw section
        assert "Memory Full Raw" in calls["subheader"]
        assert any(
            c["content"] == "memory full content" and c["language"] == "markdown"
            for c in calls["code"]
        )
        assert any(
            d["label"] == "Download memory_full.md"
            and d["data"] == build_text_download_payload("memory full content")
            for d in calls["download_button"]
        )

        # Assert - Memory Prompt Raw section
        assert "Memory Prompt Raw" in calls["subheader"]
        assert any(
            c["content"] == "memory prompt content" and c["language"] == "markdown"
            for c in calls["code"]
        )
        assert any(
            d["label"] == "Download memory_prompt.md"
            and d["data"] == build_text_download_payload("memory prompt content")
            for d in calls["download_button"]
        )

        # Verify no "no content" captions shown (all content is present)
        assert "No content available for download." not in calls["caption"]

    def test_results_section_shows_no_content_caption_when_empty(self, monkeypatch):
        """When content is empty, st.caption called and download_button NOT called."""
        # Arrange
        calls = {"code": [], "download_button": [], "subheader": [], "caption": []}

        def mock_subheader(msg):
            calls["subheader"].append(msg)

        def mock_code(content, language=None):
            calls["code"].append({"content": content, "language": language})

        def mock_download_button(label, data=None, file_name=None, mime=None, key=None):
            calls["download_button"].append(
                {
                    "label": label,
                    "data": data,
                    "file_name": file_name,
                    "mime": mime,
                    "key": key,
                }
            )

        def mock_caption(msg):
            calls["caption"].append(msg)

        mock_st = MagicMock()
        mock_st.subheader = mock_subheader
        mock_st.code = mock_code
        mock_st.download_button = mock_download_button
        mock_st.caption = mock_caption
        mock_st.session_state.get = MagicMock(
            side_effect=lambda key, default="": {
                CANDIDATES_RAW: "",
                VALIDATED_CANDIDATES_RAW: "",
                MEMORY_FULL_RAW: "",
                MEMORY_PROMPT_RAW: "",
            }.get(key, default)
        )

        monkeypatch.setattr("memory_distiller.ui.tabs.results_tab.st", mock_st)

        # Act
        render_results_tab()

        # Assert - all 4 sections show caption when empty
        assert calls["caption"].count("No content available for download.") == 4

        # Assert - no code blocks shown
        assert len(calls["code"]) == 0

        # Assert - no download buttons for empty content
        assert len(calls["download_button"]) == 0

    def test_results_tab_does_not_use_text_area_for_output_previews(self):
        """Verify no st.text_area calls in render_results_tab - Issue #27 fix."""
        source = inspect.getsource(render_results_tab)
        msg = "render_results_tab should use st.code, not st.text_area"
        assert "st.text_area" not in source, msg


class TestResultsTabPromptSizeSummary:
    """Tests for Issue #38 - Prompt Size Summary in results_tab."""

    def test_source_contains_prompt_size_summary_header(self):
        """Results tab source contains 'Prompt Size Summary' header."""
        source = inspect.getsource(render_results_tab)
        assert "Prompt Size Summary" in source

    def test_source_imports_format_token_count(self):
        """Results tab imports format_token_count from components."""
        source = inspect.getsource(render_results_tab)
        assert "format_token_count" in source

    def test_source_references_all_estimated_request_tokens_keys(self):
        """Results tab references all *_ESTIMATED_REQUEST_TOKENS state keys."""
        source = inspect.getsource(render_results_tab)
        assert "EXTRACT_ESTIMATED_REQUEST_TOKENS" in source
        assert "VALIDATE_ESTIMATED_REQUEST_TOKENS" in source
        assert "MERGE_ESTIMATED_REQUEST_TOKENS" in source
        assert "COMPRESS_ESTIMATED_REQUEST_TOKENS" in source

    def test_prompt_size_summary_uses_st_metric(self):
        """Prompt size summary uses st.metric for display."""
        source = inspect.getsource(render_results_tab)
        metric_idx = source.find("Prompt Size Summary")
        assert metric_idx != -1
        metric_section = source[metric_idx:]
        assert "st.metric" in metric_section

    def test_prompt_size_summary_checks_session_state_values(self):
        """Prompt size summary reads from session state for each step."""
        source = inspect.getsource(render_results_tab)
        assert "st.session_state.get(EXTRACT_ESTIMATED_REQUEST_TOKENS)" in source
        assert "st.session_state.get(VALIDATE_ESTIMATED_REQUEST_TOKENS)" in source
        assert "st.session_state.get(MERGE_ESTIMATED_REQUEST_TOKENS)" in source
        assert "st.session_state.get(COMPRESS_ESTIMATED_REQUEST_TOKENS)" in source
