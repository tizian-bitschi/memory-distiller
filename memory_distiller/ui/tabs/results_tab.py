"""Results tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.io.file_export import build_text_download_payload, safe_export_filename
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    VALIDATED_CANDIDATES_RAW,
)


def render_results_tab() -> None:
    """Render the results tab showing all raw outputs and download buttons."""
    candidates_raw = st.session_state.get(CANDIDATES_RAW, "")
    validated_raw = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    memory_full_raw = st.session_state.get(MEMORY_FULL_RAW, "")
    memory_prompt_raw = st.session_state.get(MEMORY_PROMPT_RAW, "")

    st.subheader("Candidates Raw")
    st.text_area(
        "candidates.txt",
        value=candidates_raw,
        height=200,
        key="results_candidates",
    )
    if candidates_raw:
        st.download_button(
            "Download candidates.txt",
            data=build_text_download_payload(candidates_raw),
            file_name=safe_export_filename("candidates.txt"),
            mime="text/plain",
            key="download_candidates",
        )
    else:
        st.caption("No content available for download.")

    st.subheader("Validated Candidates Raw")
    st.text_area(
        "validated_candidates.txt",
        value=validated_raw,
        height=200,
        key="results_validated",
    )
    if validated_raw:
        st.download_button(
            "Download validated_candidates.txt",
            data=build_text_download_payload(validated_raw),
            file_name=safe_export_filename("validated_candidates.txt"),
            mime="text/plain",
            key="download_validated",
        )
    else:
        st.caption("No content available for download.")

    st.subheader("Memory Full Raw")
    st.text_area(
        "memory_full.md",
        value=memory_full_raw,
        height=200,
        key="results_memory_full",
    )
    if memory_full_raw:
        st.download_button(
            "Download memory_full.md",
            data=build_text_download_payload(memory_full_raw),
            file_name=safe_export_filename("memory_full.md"),
            mime="text/markdown",
            key="download_memory_full",
        )
    else:
        st.caption("No content available for download.")

    st.subheader("Memory Prompt Raw")
    st.text_area(
        "memory_prompt.md",
        value=memory_prompt_raw,
        height=200,
        key="results_memory_prompt",
    )
    if memory_prompt_raw:
        st.download_button(
            "Download memory_prompt.md",
            data=build_text_download_payload(memory_prompt_raw),
            file_name=safe_export_filename("memory_prompt.md"),
            mime="text/markdown",
            key="download_memory_prompt",
        )
    else:
        st.caption("No content available for download.")

    st.caption("Downloads are generated in memory. Nothing is saved automatically.")
