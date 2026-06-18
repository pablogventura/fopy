"""Notebook representation smoke tests."""

from __future__ import annotations

import pytest

from fopy.finite import explain_definability


@pytest.mark.finite
def test_repr_html(minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    html = report._repr_html_()
    assert "<div" in html and "T0" in html and "<details" in html


@pytest.mark.finite
def test_show_tables(minimal_model):
    text = minimal_model.show_tables()
    assert "universe" in text
