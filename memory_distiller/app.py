"""Memory Distiller - Streamlit MVP application."""

from __future__ import annotations

import streamlit as st

from memory_distiller.ui.pages import (
    render_compress_tab,
    render_extract_tab,
    render_input_tab,
    render_merge_tab,
    render_results_tab,
    render_validate_tab,
)
from memory_distiller.ui.state import (
    DEFAULT_MODE,
    DEFAULT_MODEL,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_TEMPERATURE,
    DEFAULT_THINKING_ENABLED,
    MODE,
    MODEL,
    REASONING_EFFORT,
    TEMPERATURE,
    THINKING_ENABLED,
    initialize_session_state,
)

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Memory Distiller",
    page_icon="🧪",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

initialize_session_state()

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Settings")

    # Mode selector
    mode_options = ["Prompt-only", "API"]
    mode_index = mode_options.index(st.session_state.get(MODE, DEFAULT_MODE))
    mode = st.selectbox(
        "Mode",
        options=mode_options,
        index=mode_index,
        key=MODE,
    )

    st.divider()

    # Model selector (only relevant for API mode, but always visible)
    model_options = ["deepseek-v4-pro", "deepseek-v4-flash"]
    model_index = model_options.index(st.session_state.get(MODEL, DEFAULT_MODEL))
    model = st.selectbox(
        "Model",
        options=model_options,
        index=model_index,
        key=MODEL,
    )

    # Temperature
    temperature = st.number_input(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        step=0.1,
        value=st.session_state.get(TEMPERATURE, DEFAULT_TEMPERATURE),
        key=TEMPERATURE,
    )

    # Thinking enabled
    thinking_enabled = st.checkbox(
        "Thinking enabled",
        value=st.session_state.get(THINKING_ENABLED, DEFAULT_THINKING_ENABLED),
        key=THINKING_ENABLED,
    )

    # Reasoning effort
    reasoning_effort_options = ["low", "medium", "high"]
    reasoning_effort_index = reasoning_effort_options.index(
        st.session_state.get(REASONING_EFFORT, DEFAULT_REASONING_EFFORT)
    )
    reasoning_effort = st.selectbox(
        "Reasoning effort",
        options=reasoning_effort_options,
        index=reasoning_effort_index,
        key=REASONING_EFFORT,
    )

    st.divider()

    # Privacy warning for API mode
    if mode == "API":
        st.warning(
            "Im API-Modus werden Chatverlauf, bestehender Memory und "
            "Zwischenergebnisse an den konfigurierten LLM-Anbieter gesendet."
        )

    st.caption("API key wird aus der Umgebungsvariable DEEPSEEK_API_KEY gelesen.")


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("Memory Distiller")
st.markdown(
    "Extrahiere wiederverwendbares LLM-Memory aus Chatverläufen. "
    "Füge deinen Chat-Log ein, durchlaufe den Pipeline (Extract → Validate → "
    "Merge → Compress) und exportiere kompakte Memory-Dateien für neue Chats."
)

# Tab layout matching pipeline order
tabs = st.tabs(
    [
        "Input",
        "Extract",
        "Validate",
        "Merge",
        "Compress",
        "Export / Results",
    ]
)

with tabs[0]:
    render_input_tab()

with tabs[1]:
    render_extract_tab()

with tabs[2]:
    render_validate_tab()

with tabs[3]:
    render_merge_tab()

with tabs[4]:
    render_compress_tab()

with tabs[5]:
    render_results_tab()
