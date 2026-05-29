"""Merge tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.merge_applier import apply_merge_plan
from memory_distiller.application.merge_service import MergeService
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.io.memory_renderer import render_memory_document
from memory_distiller.io.merge_plan_parser import parse_merge_plan
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import (
    estimate_tokens,
    render_error,
    render_memory_summary,
    render_token_summary,
    render_usage_summary,
)
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.state import (
    EXISTING_MEMORY,
    MEMORY_FULL_RAW,
    MERGE_COST,
    MERGE_ESTIMATED_REQUEST_TOKENS,
    MERGE_MODEL,
    MERGE_PLAN_RAW,
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

    estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
    st.session_state[MERGE_ESTIMATED_REQUEST_TOKENS] = estimated_request
    render_token_summary(
        "Merge",
        system_prompt=MergeService.SYSTEM_PROMPT,
        rendered_prompt=prompt,
    )
    st.code(prompt, language="text")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Merge Plan Response",
        height=300,
        key="merge_llm_response",
    )

    if llm_response:
        render_token_summary(
            "Merge",
            system_prompt=MergeService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=llm_response,
        )

    if st.button("Apply Merge Plan", key="merge_apply_btn"):
        if not llm_response:
            st.warning("Please paste a merge plan response first.")
            return

        st.session_state[MERGE_PLAN_RAW] = llm_response

        try:
            plan = parse_merge_plan(llm_response)
            memory_doc = apply_merge_plan(existing_memory, plan)
            rendered = render_memory_document(memory_doc)
            parse_memory_document(rendered)
        except ParseErrorCollection as e:
            st.error(render_error(e))
            return
        except ValueError as e:
            st.error(str(e))
            return

        st.session_state[MEMORY_FULL_RAW] = rendered
        st.session_state[MERGE_RESULT] = memory_doc
        st.session_state.pop("merge_repair_changes", None)
        st.success("✅ Merge plan applied successfully.")

        st.subheader("Raw Merge Plan")
        st.text_area(
            "Raw Merge Plan",
            value=llm_response,
            height=200,
            key="merge_plan_raw_display",
        )

        st.subheader("Rendered MEMORY_FULL")
        st.code(rendered, language="markdown")

        st.subheader("Memory Document Summary")
        summary = render_memory_summary(memory_doc)
        st.json(summary)


def _render_merge_api() -> None:
    """Render merge in API mode."""
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    validated_raw = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    if not validated_raw:
        st.info("📋 No validated candidates found. Please run validation first.")
        return

    st.subheader("Run Merge")

    service = MergeService()
    try:
        prompt = service.render_prompt(
            existing_memory=existing_memory,
            validated_candidates=validated_raw,
        )
        estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
        st.session_state[MERGE_ESTIMATED_REQUEST_TOKENS] = estimated_request
        render_token_summary(
            "Merge",
            system_prompt=MergeService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
        )
    except ValueError as e:
        st.error(str(e))
        return

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
            st.session_state[MERGE_PLAN_RAW] = result.raw_response
            st.session_state[MEMORY_FULL_RAW] = result.memory_full_raw
            st.session_state[MERGE_RESULT] = result.memory_document
            st.session_state[MERGE_USAGE] = result.usage
            st.session_state[MERGE_COST] = result.cost_estimate
            st.session_state[MERGE_MODEL] = result.model
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            return

    merge_plan_raw = st.session_state.get(MERGE_PLAN_RAW, "")
    memory_full_raw = st.session_state.get(MEMORY_FULL_RAW, "")
    memory_doc: MemoryDocument | None = st.session_state.get(MERGE_RESULT, None)

    if merge_plan_raw or memory_doc:
        st.subheader("Rendered Prompt")
        service = MergeService()
        try:
            prompt = service.render_prompt(
                existing_memory=existing_memory,
                validated_candidates=validated_raw,
            )
            st.code(prompt, language="text")
        except ValueError:
            pass

        if merge_plan_raw:
            st.subheader("Raw Merge Plan")
            st.text_area(
                "Raw Merge Plan",
                value=merge_plan_raw,
                height=200,
                key="merge_plan_raw_display",
            )

        if memory_full_raw:
            st.subheader("Rendered MEMORY_FULL")
            st.code(memory_full_raw, language="markdown")

        if memory_doc:
            st.subheader("Memory Document Summary")
            summary = render_memory_summary(memory_doc)
            st.json(summary)

        usage = st.session_state.get(MERGE_USAGE)
        cost = st.session_state.get(MERGE_COST)
        model = st.session_state.get(MERGE_MODEL)
        render_token_summary(
            "Merge",
            system_prompt=MergeService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=merge_plan_raw if merge_plan_raw else None,
            provider_usage=usage,
        )
        if usage is not None or cost is not None:
            render_usage_summary("Merge", usage, cost, model)
