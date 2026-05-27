"""Compress tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import render_error
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    COMPRESSION_RESULT,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    MODE,
    NEXT_CONTEXT,
)


def render_compress_tab() -> None:
    """Render the compression tab with prompt-only and API modes."""
    mode = st.session_state.get(MODE, "Prompt-only")

    if mode == "Prompt-only":
        _render_compress_prompt_only()
    else:
        _render_compress_api()


def _render_compress_prompt_only() -> None:
    """Render compression in prompt-only mode."""
    memory_full_raw = st.session_state.get(MEMORY_FULL_RAW, "")

    if not memory_full_raw:
        st.info("📋 No memory_full found. Please run merge first.")
        return

    st.subheader("Compressor Prompt")
    service = CompressionService()
    next_context = st.session_state.get(NEXT_CONTEXT, "")
    try:
        prompt = service.render_prompt(memory_full=memory_full_raw, next_context=next_context)
    except ValueError as e:
        st.error(str(e))
        return

    st.text_area("Prompt", value=prompt, height=400, key="compress_prompt_display")


def _render_compress_api() -> None:
    """Render compression in API mode."""
    memory_full_raw = st.session_state.get(MEMORY_FULL_RAW, "")

    if not memory_full_raw:
        st.info("📋 No memory_full found. Please run merge first.")
        return

    st.subheader("Run Compression")

    if st.button("Run compression", key="compress_run_btn"):
        service = CompressionService()
        try:
            client = create_deepseek_client_from_session_state()
        except MissingApiKeyError:
            st.error("API key not found. Please ensure DEEPSEEK_API_KEY is set in environment.")
            return
        except ValueError as e:
            st.error(str(e))
            return

        next_context = st.session_state.get(NEXT_CONTEXT, "")
        try:
            result = service.run(
                memory_full=memory_full_raw,
                next_context=next_context,
                llm_client=client,
            )
            st.session_state[COMPRESSION_RESULT] = result.memory_prompt
            st.session_state[MEMORY_PROMPT_RAW] = result.raw_response
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            return

    # Display results if available
    memory_prompt = st.session_state.get(MEMORY_PROMPT_RAW, "")

    if memory_prompt:
        st.subheader("Rendered Prompt")
        service = CompressionService()
        next_context = st.session_state.get(NEXT_CONTEXT, "")
        try:
            prompt = service.render_prompt(memory_full=memory_full_raw, next_context=next_context)
            st.text_area("Prompt", value=prompt, height=300, key="compress_api_prompt_display")
        except ValueError:
            pass

        st.subheader("Memory Prompt")
        st.text_area(
            "memory_prompt",
            value=memory_prompt,
            height=200,
            key="compress_result_display",
        )
