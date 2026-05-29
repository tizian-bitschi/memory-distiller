"""Results tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.io.file_export import build_text_download_payload, safe_export_filename
from memory_distiller.llm.models import LlmCostEstimate, LlmUsage
from memory_distiller.ui.components import (
    aggregate_cost,
    aggregate_usage,
    format_cost,
    format_token_count,
    render_usage_summary,
)
from memory_distiller.ui.run_log import build_run_log_json, build_run_log_markdown, clear_run_log
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    COMPRESS_COST,
    COMPRESS_ESTIMATED_REQUEST_TOKENS,
    COMPRESS_USAGE,
    EXTRACT_COST,
    EXTRACT_ESTIMATED_REQUEST_TOKENS,
    EXTRACT_USAGE,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    MERGE_COST,
    MERGE_ESTIMATED_REQUEST_TOKENS,
    MERGE_USAGE,
    RUN_LOG_EVENTS,
    VALIDATE_COST,
    VALIDATE_ESTIMATED_REQUEST_TOKENS,
    VALIDATE_USAGE,
    VALIDATED_CANDIDATES_RAW,
)


def render_results_tab() -> None:
    """Render the results tab showing all raw outputs and download buttons."""
    candidates_raw = st.session_state.get(CANDIDATES_RAW, "")
    validated_raw = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    memory_full_raw = st.session_state.get(MEMORY_FULL_RAW, "")
    memory_prompt_raw = st.session_state.get(MEMORY_PROMPT_RAW, "")

    st.subheader("Candidates Raw")
    if candidates_raw:
        st.code(candidates_raw, language="text")
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
    if validated_raw:
        st.code(validated_raw, language="text")
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
    if memory_full_raw:
        st.code(memory_full_raw, language="markdown")
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
    if memory_prompt_raw:
        st.code(memory_prompt_raw, language="markdown")
        st.download_button(
            "Download memory_prompt.md",
            data=build_text_download_payload(memory_prompt_raw),
            file_name=safe_export_filename("memory_prompt.md"),
            mime="text/markdown",
            key="download_memory_prompt",
        )
    else:
        st.caption("No content available for download.")

    # Prompt size summary
    extract_tokens = st.session_state.get(EXTRACT_ESTIMATED_REQUEST_TOKENS)
    validate_tokens = st.session_state.get(VALIDATE_ESTIMATED_REQUEST_TOKENS)
    merge_tokens = st.session_state.get(MERGE_ESTIMATED_REQUEST_TOKENS)
    compress_tokens = st.session_state.get(COMPRESS_ESTIMATED_REQUEST_TOKENS)

    if (
        extract_tokens is not None
        or validate_tokens is not None
        or merge_tokens is not None
        or compress_tokens is not None
    ):
        st.subheader("Prompt Size Summary")
        cols = st.columns(4)
        with cols[0]:
            st.metric("Extract", format_token_count(extract_tokens))
        with cols[1]:
            st.metric("Validate", format_token_count(validate_tokens))
        with cols[2]:
            st.metric("Merge", format_token_count(merge_tokens))
        with cols[3]:
            st.metric("Compress", format_token_count(compress_tokens))
    else:
        st.caption("No prompt size estimates available. Run pipeline steps to see estimates.")

    # Usage and cost summary
    usages: list[LlmUsage] = []
    costs: list[LlmCostEstimate] = []
    for key in [EXTRACT_USAGE, VALIDATE_USAGE, MERGE_USAGE, COMPRESS_USAGE]:
        usage = st.session_state.get(key)
        if isinstance(usage, LlmUsage):
            usages.append(usage)
    for key in [EXTRACT_COST, VALIDATE_COST, MERGE_COST, COMPRESS_COST]:
        cost = st.session_state.get(key)
        if isinstance(cost, LlmCostEstimate):
            costs.append(cost)

    if usages or costs:
        st.subheader("Run Usage & Cost Summary")
        aggregated = aggregate_usage(usages)
        render_usage_summary("Total Run", aggregated, None, None)
        total_cost = aggregate_cost(costs)
        if total_cost is not None:
            st.write(f"**Total estimated cost:** {format_cost(total_cost)}")
        st.caption("Costs are estimates based on configured pricing.")

    st.divider()
    st.subheader("Debug Run Log")

    events = st.session_state.get(RUN_LOG_EVENTS, [])
    st.write(f"Events recorded: {len(events)}")
    st.caption(
        "Privacy notice: Exported logs may contain private chat content, "
        "prompts, and LLM responses. No API keys or secrets are included intentionally."
    )

    if events:
        markdown_data = build_run_log_markdown(events)
        json_data = build_run_log_json(events)

        st.download_button(
            "Download debug_run.md",
            data=markdown_data,
            file_name="debug_run.md",
            mime="text/markdown",
            key="download_debug_run_md",
        )
        st.download_button(
            "Download debug_run.json",
            data=json_data,
            file_name="debug_run.json",
            mime="application/json",
            key="download_debug_run_json",
        )
    else:
        st.caption("No events recorded yet. Run pipeline steps to generate a debug log.")

    if st.button("Clear current run log", key="clear_run_log_btn"):
        clear_run_log()
        st.rerun()

    st.caption("Downloads are generated in memory. Nothing is saved automatically.")
