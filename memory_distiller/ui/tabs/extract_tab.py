"""Extract tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.domain.candidate import MemoryCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.io.candidate_parser import parse_candidates
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import render_candidate_table, render_error
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    CHAT_LOG,
    EXISTING_MEMORY,
    EXTRACTION_RESULT,
    MODE,
)


def render_extract_tab() -> None:
    """Render the extraction tab with prompt-only and API modes."""
    mode = st.session_state.get(MODE, "Prompt-only")

    if mode == "Prompt-only":
        _render_extract_prompt_only()
    else:
        _render_extract_api()


def _render_extract_prompt_only() -> None:
    """Render extraction in prompt-only mode."""
    chat_log = st.session_state.get(CHAT_LOG, "")
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    if not chat_log:
        st.info("📋 Please fill in the chat log in the Input tab first.")
        return

    st.subheader("Extractor Prompt")
    service = ExtractionService()
    try:
        prompt = service.render_prompt(existing_memory=existing_memory, chat_log=chat_log)
    except ValueError as e:
        st.error(str(e))
        return

    st.text_area("Prompt", value=prompt, height=400, key="extract_prompt_display")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Paste the LLM response here",
        height=300,
        key="extract_llm_response",
    )

    if st.button("Parse Candidates", key="extract_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[CANDIDATES_RAW] = llm_response
        try:
            candidates = parse_candidates(llm_response)
            st.session_state[EXTRACTION_RESULT] = candidates
            st.success(f"✅ Parsed {len(candidates)} candidates successfully.")
        except ParseErrorCollection as e:
            st.error(render_error(e))


def _render_extract_api() -> None:
    """Render extraction in API mode."""
    chat_log = st.session_state.get(CHAT_LOG, "")
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    if not chat_log:
        st.info("📋 Please fill in the chat log in the Input tab first.")
        return

    st.subheader("Run Extraction")

    if st.button("Run extraction", key="extract_run_btn"):
        service = ExtractionService()
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
                chat_log=chat_log,
                llm_client=client,
            )
            st.session_state[EXTRACTION_RESULT] = result.candidates
            st.session_state[CANDIDATES_RAW] = result.raw_response
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            return

    # Display results if available
    raw_response = st.session_state.get(CANDIDATES_RAW, "")
    candidates: list[MemoryCandidate] | None = st.session_state.get(EXTRACTION_RESULT, None)

    if raw_response or candidates:
        st.subheader("Rendered Prompt")
        service = ExtractionService()
        try:
            prompt = service.render_prompt(existing_memory=existing_memory, chat_log=chat_log)
            st.text_area("Prompt", value=prompt, height=300, key="extract_api_prompt_display")
        except ValueError:
            pass

        if raw_response:
            st.subheader("Raw LLM Response")
            st.text_area("Raw Response", value=raw_response, height=200, key="extract_raw_display")

        if candidates:
            st.subheader(f"Parsed Candidates ({len(candidates)})")
            table_data = render_candidate_table(candidates)
            if table_data:
                st.dataframe(table_data, use_container_width=True)
