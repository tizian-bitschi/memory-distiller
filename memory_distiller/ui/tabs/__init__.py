"""Tab render functions for Memory Distiller UI."""

from memory_distiller.ui.tabs.compress_tab import render_compress_tab
from memory_distiller.ui.tabs.extract_tab import render_extract_tab
from memory_distiller.ui.tabs.input_tab import render_input_tab
from memory_distiller.ui.tabs.merge_tab import render_merge_tab
from memory_distiller.ui.tabs.results_tab import render_results_tab
from memory_distiller.ui.tabs.validate_tab import render_validate_tab

__all__ = [
    "render_input_tab",
    "render_extract_tab",
    "render_validate_tab",
    "render_merge_tab",
    "render_compress_tab",
    "render_results_tab",
]
