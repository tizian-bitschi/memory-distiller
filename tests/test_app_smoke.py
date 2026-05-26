"""Smoke tests for memory_distiller package."""


def test_import_memory_distiller() -> None:
    """Verify memory_distiller package imports."""
    import memory_distiller  # noqa: F401


def test_import_app() -> None:
    """Verify memory_distiller.app imports."""
    from memory_distiller import app  # noqa: F401
