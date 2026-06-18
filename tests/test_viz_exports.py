"""Smoke tests for draw export formats (mermaid, tikz, html)."""

from __future__ import annotations

import pytest


def test_mermaid_export_chain():
    from fopy.draw.mermaid_export import hasse_to_mermaid

    text = hasse_to_mermaid([0, 1, 2], [(0, 1), (1, 2)])
    assert "graph" in text.lower() or "-->" in text


def test_tikz_export_chain():
    from fopy.draw.tikz_export import hasse_to_tikz

    text = hasse_to_tikz([0, 1], [(0, 1)])
    assert "tikzpicture" in text or "draw" in text


@pytest.mark.viz
def test_html_export_chain():
    from fopy.draw.html_export import hasse_to_html

    html = hasse_to_html([0, 1], [(0, 1)])
    assert "<" in html
