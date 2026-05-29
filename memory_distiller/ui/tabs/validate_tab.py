"""Validate tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.validation_service import ValidationService
from memory_distiller.domain.candidate import ValidatedCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.io.candidate_parser import parse_validated_candidates
from memory_distiller.io.enum_aliases import normalize_candidate_lines
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import (
    estimate_tokens,
    render_error,
    render_token_summary,
    render_usage_summary,
    render_validated_candidate_table,
)
from memory_distiller.ui.llm_factory import create_deepseek_client_from_session_state
from memory_distiller.ui.run_log import append_run_log_event
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    CHAT_LOG,
    EXISTING_MEMORY,
    MODE,
    VALIDATE_COST,
    VALIDATE_ESTIMATED_REQUEST_TOKENS,
    VALIDATE_MODEL,
    VALIDATE_USAGE,
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

    estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
    st.session_state[VALIDATE_ESTIMATED_REQUEST_TOKENS] = estimated_request
    render_token_summary(
        "Validation",
        system_prompt=service.SYSTEM_PROMPT,
        rendered_prompt=prompt,
    )
    st.code(prompt, language="text")

    st.subheader("LLM Response")
    llm_response = st.text_area(
        "Paste the LLM response here",
        height=300,
        key="validate_llm_response",
    )

    if llm_response:
        render_token_summary(
            "Validation",
            system_prompt=ValidationService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=llm_response,
        )

    if st.button("Repair common enum aliases", key="validate_repair_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
        else:
            repaired, changes = normalize_candidate_lines(llm_response)
            st.session_state["validate_llm_response"] = repaired
            st.session_state["validate_repair_changes"] = changes
            append_run_log_event(
                step="validate",
                event_type="repair",
                summary=f"Repaired {len(changes)} enum aliases",
                details={
                    "mode": "Prompt-only",
                    "repair_count": len(changes),
                    "changes": changes,
                },
            )
            st.rerun()

    changes = st.session_state.get("validate_repair_changes", [])
    if changes:
        st.subheader("Repairs Applied")
        for change in changes:
            st.write(f"- {change}")
    elif "validate_repair_changes" in st.session_state:
        st.info("No changes needed.")

    if st.button("Parse Validated Candidates", key="validate_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[VALIDATED_CANDIDATES_RAW] = llm_response
        try:
            validated = parse_validated_candidates(llm_response)
            st.session_state[VALIDATION_RESULT] = validated
            st.session_state.pop("validate_repair_changes", None)
            st.success(f"✅ Parsed {len(validated)} validated candidates successfully.")
            append_run_log_event(
                step="validate",
                event_type="parse_validated",
                summary=f"Parsed {len(validated)} validated candidates",
                details={
                    "mode": "Prompt-only",
                    "parse_status": "success",
                    "validated_candidate_count": len(validated),
                    "rendered_prompt": prompt if "prompt" in dir() else None,
                    "raw_llm_response": llm_response,
                },
            )
        except ParseErrorCollection as e:
            st.error(render_error(e))
            append_run_log_event(
                step="validate",
                event_type="parse_validated",
                summary="Parse failed",
                details={
                    "mode": "Prompt-only",
                    "parse_status": "failure",
                    "parser_errors": render_error(e),
                },
            )


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

    service = ValidationService()
    try:
        prompt = service.render_prompt(
            existing_memory=existing_memory,
            chat_log=chat_log,
            candidates=candidates_raw,
        )
        estimated_request = estimate_tokens(service.SYSTEM_PROMPT) + estimate_tokens(prompt)
        st.session_state[VALIDATE_ESTIMATED_REQUEST_TOKENS] = estimated_request
        render_token_summary(
            "Validation",
            system_prompt=service.SYSTEM_PROMPT,
            rendered_prompt=prompt,
        )
    except ValueError as e:
        st.error(str(e))
        return

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
            st.session_state[VALIDATE_USAGE] = result.usage
            st.session_state[VALIDATE_COST] = result.cost_estimate
            st.session_state[VALIDATE_MODEL] = result.model
            append_run_log_event(
                step="validate",
                event_type="api_response",
                summary=f"Validated {len(result.validated_candidates)} candidates via API",
                details={
                    "mode": "API",
                    "model": result.model,
                    "temperature": st.session_state.get("temperature"),
                    "thinking_enabled": st.session_state.get("thinking_enabled"),
                    "reasoning_effort": st.session_state.get("reasoning_effort"),
                    "rendered_prompt": result.prompt,
                    "raw_llm_response": result.raw_response,
                    "parse_status": "success",
                    "validated_candidate_count": len(result.validated_candidates),
                    "usage": result.usage.__dict__ if result.usage else None,
                    "cost_estimate": str(result.cost_estimate.total_cost)
                    if result.cost_estimate
                    else None,
                    "estimated_request_tokens": st.session_state.get(
                        VALIDATE_ESTIMATED_REQUEST_TOKENS
                    ),
                },
            )
        except Exception as e:  # Broad catch at UI boundary to prevent app crash
            st.error(render_error(e))
            append_run_log_event(
                step="validate",
                event_type="api_response",
                summary="Validation failed",
                details={
                    "mode": "API",
                    "parse_status": "failure",
                    "error": str(e),
                },
            )
            return

    # Display results if available
    raw_response = st.session_state.get(VALIDATED_CANDIDATES_RAW, "")
    validated: list[ValidatedCandidate] | None = st.session_state.get(VALIDATION_RESULT, None)

    if raw_response or validated:
        st.subheader("Rendered Prompt")
        service = ValidationService()
        display_prompt: str | None = None
        try:
            display_prompt = service.render_prompt(
                existing_memory=existing_memory,
                chat_log=chat_log,
                candidates=candidates_raw,
            )
            st.code(display_prompt, language="text")
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

        usage = st.session_state.get(VALIDATE_USAGE)
        cost = st.session_state.get(VALIDATE_COST)
        model = st.session_state.get(VALIDATE_MODEL)
        render_token_summary(
            "Validation",
            system_prompt=ValidationService.SYSTEM_PROMPT,
            rendered_prompt=prompt,
            raw_response=raw_response if raw_response else None,
            provider_usage=usage,
        )
        if usage is not None or cost is not None:
            render_usage_summary("Validation", usage, cost, model)
