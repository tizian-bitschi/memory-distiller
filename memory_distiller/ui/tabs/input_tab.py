"""Input tab render function."""

from __future__ import annotations

import streamlit as st

from memory_distiller.io.file_import import (
    decode_uploaded_text,
    read_chat_log,
    validate_chat_log_extension,
    validate_text_file_extension,
)
from memory_distiller.io.html_chat_import import HtmlChatImportError
from memory_distiller.ui.components import estimate_tokens
from memory_distiller.ui.state import (
    CHAT_LOG,
    EXISTING_MEMORY,
    LAST_CHAT_LOG_UPLOAD_NAME,
    LAST_EXISTING_MEMORY_UPLOAD_NAME,
    NEXT_CONTEXT,
)


def render_input_tab() -> None:
    """Render the input tab with chat log, existing memory, and next context."""
    st.subheader("Chat Log")
    chat_log_file = st.file_uploader(
        "Upload chat log (optional)",
        type=["txt", "md", "markdown", "html", "htm"],
        key="chat_log_upload",
    )
    if chat_log_file is not None:
        last = st.session_state.get(LAST_CHAT_LOG_UPLOAD_NAME, "")
        if chat_log_file.name != last:
            if not validate_chat_log_extension(chat_log_file.name):
                st.error(
                    f"Invalid file extension for {chat_log_file.name!r}. "
                    "Allowed: .txt, .md, .markdown, .html, .htm"
                )
                st.session_state[LAST_CHAT_LOG_UPLOAD_NAME] = chat_log_file.name
            else:
                try:
                    text = read_chat_log(chat_log_file.read(), filename=chat_log_file.name)
                    st.session_state[CHAT_LOG] = text
                    st.session_state[LAST_CHAT_LOG_UPLOAD_NAME] = chat_log_file.name
                    st.rerun()
                except (ValueError, HtmlChatImportError) as e:
                    st.error(str(e))
                    st.session_state[LAST_CHAT_LOG_UPLOAD_NAME] = chat_log_file.name
    st.caption("Uploaded files are read into the current session only and are not written to disk.")
    st.text_area(
        "Paste your chat log here",
        height=300,
        placeholder="Enter chat log content...",
        key=CHAT_LOG,
    )
    chat_log_value = st.session_state.get(CHAT_LOG, "")
    char_count_chat = len(chat_log_value)
    token_count_chat = estimate_tokens(chat_log_value)
    st.caption(f"Characters: {char_count_chat} | Estimated tokens: {token_count_chat}")

    st.subheader("Existing Memory")
    existing_memory_file = st.file_uploader(
        "Upload existing memory (optional)",
        type=["txt", "md", "markdown"],
        key="existing_memory_upload",
    )
    if existing_memory_file is not None:
        last = st.session_state.get(LAST_EXISTING_MEMORY_UPLOAD_NAME, "")
        if existing_memory_file.name != last:
            if not validate_text_file_extension(existing_memory_file.name):
                st.error(
                    f"Invalid file extension for {existing_memory_file.name!r}. "
                    "Allowed: .txt, .md, .markdown"
                )
                st.session_state[LAST_EXISTING_MEMORY_UPLOAD_NAME] = existing_memory_file.name
            else:
                try:
                    text = decode_uploaded_text(
                        existing_memory_file.read(), filename=existing_memory_file.name
                    )
                    st.session_state[EXISTING_MEMORY] = text
                    st.session_state[LAST_EXISTING_MEMORY_UPLOAD_NAME] = existing_memory_file.name
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                    st.session_state[LAST_EXISTING_MEMORY_UPLOAD_NAME] = existing_memory_file.name
    st.caption("Uploaded files are read into the current session only and are not written to disk.")
    st.text_area(
        "Load existing memory (optional)",
        height=200,
        placeholder="Enter existing memory content...",
        key=EXISTING_MEMORY,
    )
    existing_memory_value = st.session_state.get(EXISTING_MEMORY, "")
    char_count_memory = len(existing_memory_value)
    token_count_memory = estimate_tokens(existing_memory_value)
    st.caption(f"Characters: {char_count_memory} | Estimated tokens: {token_count_memory}")

    st.subheader("Next Context")
    st.text_area(
        "Next context hint (optional)",
        height=100,
        placeholder="Enter next context...",
        key=NEXT_CONTEXT,
    )
    next_context_value = st.session_state.get(NEXT_CONTEXT, "")
    char_count_context = len(next_context_value)
    token_count_context = estimate_tokens(next_context_value)
    st.caption(f"Characters: {char_count_context} | Estimated tokens: {token_count_context}")
