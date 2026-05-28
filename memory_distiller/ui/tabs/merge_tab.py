"""Merge tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.merge_service import MergeService
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.io.enum_aliases import normalize_memory_document
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import render_error, render_memory_summary, render_usage_summary
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    EXISTING_MEMORY,
    MEMORY_FULL_RAW,
    MERGE_COST,
    MERGE_MODEL,
    MERGE_RESULT,
    MERGE_USAGE,
    MODE,
    VALIDATED_CANDIDATES_RAW,
)


def render_merge_tab() -> None:
    """Render the merge tab with prompt-only and API modes."""
    mode = st.session_state.get(MODE, "Prompt-only")

    if mode == "Prompt-only":
        _render_merge_prompt_only()
    else:
        _render_merge_api()


def _render_merge_prompt_only() -> None:
    """Render merge in prompt-only mode."""
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    validated_raw = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    if not validated_raw:
        st.info("📋 No validated candidates found. Please run validation first.")
        return

    st.subheader("Merger Prompt")
    service = MergeService()
    try:
        prompt = service.render_prompt(
            existing_memory=existing_memory,
            validated_candidates=validated_raw,
        )
    except ValueError as e:
        st.error(str(e))
        return

    st.text_area("Prompt", value=prompt, height=400, key="merge_prompt_display")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Paste the LLM response here",
        height=300,
        key="merge_llm_response",
    )

    if st.button("Repair common enum aliases", key="merge_repair_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
        else:
            repaired, changes = normalize_memory_document(llm_response)
            st.session_state["merge_llm_response"] = repaired
            st.session_state["merge_repair_changes"] = changes
            st.rerun()

    changes = st.session_state.get("merge_repair_changes", [])
    if changes:
        st.subheader("Repairs Applied")
        for change in changes:
            st.write(f"- {change}")
    elif "merge_repair_changes" in st.session_state:
        st.info("No changes needed.")

    if st.button("Parse Memory Document", key="merge_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[MEMORY_FULL_RAW] = llm_response
        try:
            memory_doc = parse_memory_document(llm_response)
            st.session_state[MERGE_RESULT] = memory_doc
            st.session_state.pop("merge_repair_changes", None)
            st.success("✅ Parsed memory document successfully.")
            summary = render_memory_summary(memory_doc)
            st.json(summary)
        except ParseErrorCollection as e:
            st.error(render_error(e))


def _render_merge_api() -> None:
    """Render merge in API mode."""
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    validated_raw = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    if not validated_raw:
        st.info("📋 No validated candidates found. Please run validation first.")
        return

    st.subheader("Run Merge")

    if st.button("Run merge", key="merge_run_btn"):
        service = MergeService()
        try:
            client = create_deepseek_client_from_session_state()
        except MissingApiKeyError:
            st.error("API key not found. Please ensure DEEPSEEK_API_KEY is set in environment.")
            return
        except ValueError as e:
            st.error(str(e))
            return

        try:
            result = service.run(
                existing_memory=existing_memory,
                validated_candidates=validated_raw,
                llm_client=client,
            )
            st.session_state[MERGE_RESULT] = result.memory_document
            st.session_state[MEMORY_FULL_RAW] = result.raw_response
            st.session_state[MERGE_USAGE] = result.usage
            st.session_state[MERGE_COST] = result.cost_estimate
            st.session_state[MERGE_MODEL] = result.model
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            return

    # Display results if available
    raw_response = st.session_state.get(MEMORY_FULL_RAW, "")
    memory_doc: MemoryDocument | None = st.session_state.get(MERGE_RESULT, None)

    if raw_response or memory_doc:
        st.subheader("Rendered Prompt")
        service = MergeService()
        try:
            prompt = service.render_prompt(
                existing_memory=existing_memory,
                validated_candidates=validated_raw,
            )
            st.text_area("Prompt", value=prompt, height=300, key="merge_api_prompt_display")
        except ValueError:
            pass

        if raw_response:
            st.subheader("Raw LLM Response")
            st.text_area("Raw Response", value=raw_response, height=200, key="merge_raw_display")

        if memory_doc:
            st.subheader("Memory Document Summary")
            summary = render_memory_summary(memory_doc)
            st.json(summary)

        usage = st.session_state.get(MERGE_USAGE)
        cost = st.session_state.get(MERGE_COST)
        model = st.session_state.get(MERGE_MODEL)
        if usage is not None or cost is not None:
            render_usage_summary("Merge", usage, cost, model)
