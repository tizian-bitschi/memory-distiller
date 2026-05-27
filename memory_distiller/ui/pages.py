"""Page render functions for Streamlit MVP UI tabs."""

from __future__ import annotations

import streamlit as st

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.application.merge_service import MergeService
from memory_distiller.application.validation_service import ValidationService
from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.errors import ParseErrorCollection
from memory_distiller.domain.memory_entry import MemoryDocument
from memory_distiller.io.candidate_parser import parse_candidates, parse_validated_candidates
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.llm.config import LlmConfig
from memory_distiller.llm.deepseek_client import DeepSeekClient
from memory_distiller.llm.errors import MissingApiKeyError
from memory_distiller.ui.components import (
    estimate_tokens,
    render_candidate_table,
    render_error,
    render_memory_summary,
    render_validated_candidate_table,
)
from memory_distiller.ui.state import (
    CANDIDATES_RAW,
    CHAT_LOG,
    COMPRESSION_RESULT,
    EXISTING_MEMORY,
    EXTRACTION_RESULT,
    MEMORY_FULL_RAW,
    MEMORY_PROMPT_RAW,
    MERGE_RESULT,
    MODE,
    MODEL,
    NEXT_CONTEXT,
    REASONING_EFFORT,
    TEMPERATURE,
    THINKING_ENABLED,
    VALIDATED_CANDIDATES_RAW,
    VALIDATION_RESULT,
)


def render_input_tab() -> None:
    """Render the input tab with chat log, existing memory, and next context."""
    st.subheader("Chat Log")
    chat_log = st.text_area(
        "Paste your chat log here",
        value=st.session_state.get(CHAT_LOG, ""),
        height=300,
        placeholder="Enter chat log content...",
    )
    st.session_state[CHAT_LOG] = chat_log
    char_count_chat = len(chat_log)
    token_count_chat = estimate_tokens(chat_log)
    st.caption(f"Characters: {char_count_chat} | Estimated tokens: {token_count_chat}")

    st.subheader("Existing Memory")
    existing_memory = st.text_area(
        "Load existing memory (optional)",
        value=st.session_state.get(EXISTING_MEMORY, ""),
        height=200,
        placeholder="Enter existing memory content...",
    )
    st.session_state[EXISTING_MEMORY] = existing_memory
    char_count_memory = len(existing_memory)
    token_count_memory = estimate_tokens(existing_memory)
    st.caption(f"Characters: {char_count_memory} | Estimated tokens: {token_count_memory}")

    st.subheader("Next Context")
    next_context = st.text_area(
        "Next context hint (optional)",
        value=st.session_state.get(NEXT_CONTEXT, ""),
        height=100,
        placeholder="Enter next context...",
    )
    st.session_state[NEXT_CONTEXT] = next_context
    char_count_context = len(next_context)
    token_count_context = estimate_tokens(next_context)
    st.caption(f"Characters: {char_count_context} | Estimated tokens: {token_count_context}")


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
            config = LlmConfig(
                model=st.session_state.get(MODEL, "deepseek-v4-pro"),
                temperature=st.session_state.get(TEMPERATURE, 0.2),
                thinking_enabled=st.session_state.get(THINKING_ENABLED, True),
                reasoning_effort=st.session_state.get(REASONING_EFFORT, "high"),
            )
            client = DeepSeekClient(config)
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
        except Exception as e:  # noqa: BLE001
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
            config = LlmConfig(
                model=st.session_state.get(MODEL, "deepseek-v4-pro"),
                temperature=st.session_state.get(TEMPERATURE, 0.2),
                thinking_enabled=st.session_state.get(THINKING_ENABLED, True),
                reasoning_effort=st.session_state.get(REASONING_EFFORT, "high"),
            )
            client = DeepSeekClient(config)
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
        except Exception as e:  # noqa: BLE001
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

    if st.button("Parse Memory Document", key="merge_parse_btn"):
        if not llm_response:
            st.warning("Please paste an LLM response first.")
            return
        st.session_state[MEMORY_FULL_RAW] = llm_response
        try:
            memory_doc = parse_memory_document(llm_response)
            st.session_state[MERGE_RESULT] = memory_doc
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
            config = LlmConfig(
                model=st.session_state.get(MODEL, "deepseek-v4-pro"),
                temperature=st.session_state.get(TEMPERATURE, 0.2),
                thinking_enabled=st.session_state.get(THINKING_ENABLED, True),
                reasoning_effort=st.session_state.get(REASONING_EFFORT, "high"),
            )
            client = DeepSeekClient(config)
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
        except Exception as e:  # noqa: BLE001
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
            config = LlmConfig(
                model=st.session_state.get(MODEL, "deepseek-v4-pro"),
                temperature=st.session_state.get(TEMPERATURE, 0.2),
                thinking_enabled=st.session_state.get(THINKING_ENABLED, True),
                reasoning_effort=st.session_state.get(REASONING_EFFORT, "high"),
            )
            client = DeepSeekClient(config)
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
        except Exception as e:  # noqa: BLE001
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
            data=candidates_raw,
            file_name="candidates.txt",
            mime="text/plain",
            key="download_candidates",
        )

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
            data=validated_raw,
            file_name="validated_candidates.txt",
            mime="text/plain",
            key="download_validated",
        )

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
            data=memory_full_raw,
            file_name="memory_full.md",
            mime="text/markdown",
            key="download_memory_full",
        )

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
            data=memory_prompt_raw,
            file_name="memory_prompt.md",
            mime="text/markdown",
            key="download_memory_prompt",
        )
