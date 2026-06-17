"""Public API import and smoke tests."""

from __future__ import annotations

import importlib

import pytest


def test_import_fopy():
    import fopy as fo

    assert fo.__version__ == "0.1.0"


def test_all_exports_importable():
    import fopy as fo

    for name in fo.__all__:
        if name.startswith("_"):
            continue
        assert hasattr(fo, name), name


@pytest.mark.parametrize(
    "module",
    [
        "fopy.core",
        "fopy.builders",
        "fopy.finite",
        "fopy.parse",
        "fopy.printing",
        "fopy.bridge",
    ],
)
def test_submodules_import(module: str):
    importlib.import_module(module)


def test_draw_optional_import():
    import fopy as fo

    try:
        import fopy.draw  # noqa: F401

        assert fo.draw is not None
    except ImportError:
        assert fo.draw is None
