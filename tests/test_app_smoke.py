"""Smoke tests for memory_distiller package."""

from __future__ import annotations

import pytest


def test_import_memory_distiller() -> None:
    """Verify memory_distiller package imports."""
    import memory_distiller  # noqa: F401


def test_import_app() -> None:
    """Verify memory_distiller.app imports without Streamlit runtime."""
    from memory_distiller import app as app_module

    # streamlit is imported at module level, but st.set_page_config and
    # st.session_state access are only reached at runtime.
    # The module should import cleanly.
    assert hasattr(app_module, "initialize_session_state")


@pytest.fixture
def patch_streamlit_for_app(monkeypatch):
    """Patch streamlit module for testing without Streamlit runtime."""
    from unittest.mock import MagicMock

    mock_st = MagicMock()
    mock_st.session_state = {}
    monkeypatch.setattr("streamlit", mock_st)
    return mock_st
