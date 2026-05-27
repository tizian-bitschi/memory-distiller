"""Validate tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.validation_service import ValidationService
from memory_distiller.domain.candidate import ValidatedCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.io.candidate_parser import parse_validated_candidates
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import render_error, render_validated_candidate_table
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    CHAT_LOG,
    EXISTING_MEMORY,
    MODE,
    VALIDATED_CANDIDATES_RAW,
    VALIDATION_RESULT,
)


def render_validate_tab() -> None:
    """Render the validation tab with prompt-only and API modes."""
    mode = st.session_state.get(MODE, "Prompt-only")

    if mode == "Prompt-only":
        _render_validate_prompt_only()
    else:
        _render_validate_api()


def _render_validate_prompt_only() -> None:
    """Render validation in prompt-only mode."""
    chat_log = st.session_state.get(CHAT_LOG, "")
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    candidates_raw = st.session_state.get(CANDIDATES_RAW, "")
    if not candidates_raw:
        st.info("📋 No candidates found. Please run extraction first.")
        return

    if not chat_log:
        st.info("📋 Chat log is required for validation.")
        return

    st.subheader("Validator Prompt")
    service = ValidationService()
    try:
        prompt = service.render_prompt(
            existing_memory=existing_memory,
            chat_log=chat_log,
            candidates=candidates_raw,
        )
    except ValueError as e:
        st.error(str(e))
        return

    st.text_area("Prompt", value=prompt, height=400, key="validate_prompt_display")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Paste the LLM response here",
        height=300,
        key="validate_llm_response",
    )

    if st.button("Parse Validated Candidates", key="validate_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[VALIDATED_CANDIDATES_RAW] = llm_response
        try:
            validated = parse_validated_candidates(llm_response)
            st.session_state[VALIDATION_RESULT] = validated
            st.success(f"✅ Parsed {len(validated)} validated candidates successfully.")
        except ParseErrorCollection as e:
            st.error(render_error(e))


def _render_validate_api() -> None:
    """Render validation in API mode."""
    chat_log = st.session_state.get(CHAT_LOG, "")
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    candidates_raw = st.session_state.get(CANDIDATES_RAW, "")
    if not candidates_raw:
        st.info("📋 No candidates found. Please run extraction first.")
        return

    if not chat_log:
        st.info("📋 Chat log is required for validation.")
        return

    st.subheader("Run Validation")

    if st.button("Run validation", key="validate_run_btn"):
        service = ValidationService()
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
                candidates=candidates_raw,
                llm_client=client,
            )
            st.session_state[VALIDATION_RESULT] = result.validated_candidates
            st.session_state[VALIDATED_CANDIDATES_RAW] = result.raw_response
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            return

    # Display results if available
    raw_response = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    validated: list[ValidatedCandidate] | None = st.session_state.get(VALIDATION_RESULT, None)

    if raw_response or validated:
        st.subheader("Rendered Prompt")
        service = ValidationService()
        try:
            prompt = service.render_prompt(
                existing_memory=existing_memory,
                chat_log=chat_log,
                candidates=candidates_raw,
            )
            st.text_area("Prompt", value=prompt, height=300, key="validate_api_prompt_display")
        except ValueError:
            pass

        if raw_response:
            st.subheader("Raw LLM Response")
            st.text_area("Raw Response", value=raw_response, height=200, key="validate_raw_display")

        if validated:
            st.subheader(f"Validated Candidates ({len(validated)})")
            table_data = render_validated_candidate_table(validated)
            if table_data:
                st.dataframe(table_data, use_container_width=True)
