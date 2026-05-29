"""Extract tab render function."""

from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.domain.candidate import MemoryCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.io.candidate_parser import parse_candidates
from memory_distiller.io.enum_aliases import normalize_candidate_lines
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import (
    estimate_tokens,
    render_candidate_table,
    render_error,
    render_token_summary,
    render_usage_summary,
)
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.run_log import append_run_log_event
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    CHAT_LOG,
    EXISTING_MEMORY,
    EXTRACT_COST,
    EXTRACT_ESTIMATED_REQUEST_TOKENS,
    EXTRACT_MODEL,
    EXTRACT_USAGE,
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

    estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
    st.session_state[EXTRACT_ESTIMATED_REQUEST_TOKENS] = estimated_request
    render_token_summary(
        "Extraction",
        system_prompt=service.SYSTEM_PROMPT,
        rendered_prompt=prompt,
    )
    st.code(prompt, language="text")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Paste the LLM response here",
        height=300,
        key="extract_llm_response",
    )

    if llm_response:
        render_token_summary(
            "Extraction",
            system_prompt=ExtractionService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=llm_response,
        )

    if st.button("Repair common enum aliases", key="extract_repair_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
        else:
            repaired, changes = normalize_candidate_lines(llm_response)
            st.session_state["extract_llm_response"] = repaired
            st.session_state["extract_repair_changes"] = changes
            append_run_log_event(
                step="extract",
                event_type="repair",
                summary=f"Repaired {len(changes)} enum aliases",
                details={
                    "mode": "Prompt-only",
                    "repair_count": len(changes),
                    "changes": changes,
                },
            )
            st.rerun()

    changes = st.session_state.get("extract_repair_changes", [])
    if changes:
        st.subheader("Repairs Applied")
        for change in changes:
            st.write(f"- {change}")
    elif "extract_repair_changes" in st.session_state:
        st.info("No changes needed.")

    if st.button("Parse Candidates", key="extract_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[CANDIDATES_RAW] = llm_response
        try:
            candidates = parse_candidates(llm_response)
            st.session_state[EXTRACTION_RESULT] = candidates
            st.session_state.pop("extract_repair_changes", None)
            st.success(f"✅ Parsed {len(candidates)} candidates successfully.")
            append_run_log_event(
                step="extract",
                event_type="parse_candidates",
                summary=f"Parsed {len(candidates)} candidates",
                details={
                    "mode": "Prompt-only",
                    "parse_status": "success",
                    "candidate_count": len(candidates),
                    "rendered_prompt": prompt,
                    "raw_llm_response": llm_response,
                },
            )
        except ParseErrorCollection as e:
            st.error(render_error(e))
            append_run_log_event(
                step="extract",
                event_type="parse_candidates",
                summary="Parse Candidates failed",
                details={
                    "mode": "Prompt-only",
                    "parse_status": "failure",
                    "rendered_prompt": prompt,
                    "raw_llm_response": llm_response,
                    "parser_errors": render_error(e),
                },
            )


def _render_extract_api() -> None:
    """Render extraction in API mode."""
    chat_log = st.session_state.get(CHAT_LOG, "")
    existing_memory = st.session_state.get(EXISTING_MEMORY, "")

    if not chat_log:
        st.info("📋 Please fill in the chat log in the Input tab first.")
        return

    st.subheader("Run Extraction")

    service = ExtractionService()
    try:
        prompt = service.render_prompt(existing_memory=existing_memory, chat_log=chat_log)
        estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
        st.session_state[EXTRACT_ESTIMATED_REQUEST_TOKENS] = estimated_request
        render_token_summary(
            "Extraction",
            system_prompt=service.SYSTEM_PROMPT,
            rendered_prompt=prompt,
        )
    except ValueError as e:
        st.error(str(e))
        return

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
            st.session_state[EXTRACT_USAGE] = result.usage
            st.session_state[EXTRACT_COST] = result.cost_estimate
            st.session_state[EXTRACT_MODEL] = result.model
            append_run_log_event(
                step="extract",
                event_type="api_response",
                summary=f"Extracted {len(result.candidates)} candidates via API",
                details={
                    "mode": "API",
                    "model": result.model,
                    "temperature": st.session_state.get("temperature"),
                    "thinking_enabled": st.session_state.get("thinking_enabled"),
                    "reasoning_effort": st.session_state.get("reasoning_effort"),
                    "rendered_prompt": result.prompt,
                    "raw_llm_response": result.raw_response,
                    "parse_status": "success",
                    "candidate_count": len(result.candidates),
                    "usage": asdict(result.usage) if result.usage else None,
                    "cost_estimate": str(result.cost_estimate.total_cost)
                    if result.cost_estimate
                    else None,
                    "estimated_request_tokens": st.session_state.get(
                        EXTRACT_ESTIMATED_REQUEST_TOKENS
                    ),
                },
            )
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            append_run_log_event(
                step="extract",
                event_type="api_response",
                summary="Extract API call failed",
                details={
                    "mode": "API",
                    "rendered_prompt": prompt,
                    "parse_status": "failure",
                    "error": str(e),
                },
            )
            return

    # Display results if available
    raw_response = st.session_state.get(CANDIDATES_RAW, "")
    candidates: list[MemoryCandidate] | None = st.session_state.get(EXTRACTION_RESULT, None)

    if raw_response or candidates:
        st.subheader("Rendered Prompt")
        service = ExtractionService()
        display_prompt: str | None = None
        try:
            display_prompt = service.render_prompt(
                existing_memory=existing_memory, chat_log=chat_log
            )
            st.code(display_prompt, language="text")
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

        usage = st.session_state.get(EXTRACT_USAGE)
        cost = st.session_state.get(EXTRACT_COST)
        model = st.session_state.get(EXTRACT_MODEL)
        render_token_summary(
            "Extraction",
            system_prompt=ExtractionService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=raw_response if raw_response else None,
            provider_usage=usage,
        )
        if usage is not None or cost is not None:
            render_usage_summary("Extraction", usage, cost, model)
