"""Misc coverage bump."""

import fopy as fo
from fopy.parse import parse_formula


def test_parse_nested_parens():
    f = parse_formula("(P(x) & Q(x)) | R(x)", rels={"P": 1, "Q": 1, "R": 1})
    assert f is not None


def test_signature_relation_constant():
    sig = fo.Signature(functions={"c": 0}, relations={"R": 1})
    assert sig.constant("c") == "c"
    assert sig.relation("R") == "R"


def test_domain_getattr():
    d = fo.builders.Domain("a", "b")
    assert d.a == "a"


def test_draw_render_without_save(chain5_structure):
    import pytest

    pytest.importorskip("matplotlib")
    layout = fo.draw.layout_lattice(
        chain5_structure.universe,
        leq=lambda a, b: chain5_structure.call_relation("leq", (a, b)),
    )
    ax = fo.draw.render.draw_diagram(layout.elements, layout.positions_2d, layout.covers)
    assert ax is not None
