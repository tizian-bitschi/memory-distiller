"""Compress tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import render_error, render_usage_summary
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    COMPRESS_COST,
    COMPRESS_MODEL,
    COMPRESS_USAGE,
    COMPRESSION_RESULT,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    MODE,
    NEXT_CONTEXT,
)


def save_memory_prompt_to_state(state: dict[str, object], content: str) -> bool:
    """Save memory prompt content to session state.

    Args:
        state: Session state dictionary (typically st.session_state).
        content: Raw content from LLM response to save.

    Returns:
        True if content was saved successfully, False if empty.
    """
    cleaned = content.strip()
    if not cleaned:
        return False
    state[MEMORY_PROMPT_RAW] = cleaned
    state[COMPRESSION_RESULT] = cleaned
    return True


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

    st.code(prompt, language="text")

    st.divider()
    st.subheader("LLM Response / Memory Prompt")
    response_key = "compress_prompt_only_response"
    response_content = st.session_state.get(response_key, "")
    st.text_area(
        "Paste the LLM response containing # MEMORY_PROMPT block",
        value=response_content,
        height=200,
        key=response_key,
    )

    if st.button("Save Memory Prompt", key="compress_prompt_only_save_btn"):
        raw_content = st.session_state.get(response_key, "")
        if save_memory_prompt_to_state(st.session_state, raw_content):  # type: ignore[arg-type]
            st.success("Memory prompt saved. You can download it from Export / Results.")
        else:
            st.warning("Memory prompt cannot be empty.")


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
            st.session_state[COMPRESS_USAGE] = result.usage
            st.session_state[COMPRESS_COST] = result.cost_estimate
            st.session_state[COMPRESS_MODEL] = result.model
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
            st.code(prompt, language="text")
        except ValueError:
            pass

        st.subheader("Memory Prompt")
        st.text_area(
            "memory_prompt",
            value=memory_prompt,
            height=200,
            key="compress_result_display",
        )

        usage = st.session_state.get(COMPRESS_USAGE)
        cost = st.session_state.get(COMPRESS_COST)
        model = st.session_state.get(COMPRESS_MODEL)
        if usage is not None or cost is not None:
            render_usage_summary("Compression", usage, cost, model)
