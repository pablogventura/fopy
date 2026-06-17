"""Integration tests across parser, printer, semantics, builders."""

import pytest

import fopy as fo
from fopy.parse import parse_formula


def test_parse_print_roundtrip():
    s = "forall x exists y R(x,y) -> P(y)"
    f = parse_formula(s, rels={"R": 2, "P": 1})
    text = fo.sstr(f)
    assert "forall" in text


def test_builder_draw_chain(chain5_structure, tmp_path):
    pytest.importorskip("matplotlib")
    path = tmp_path / "chain.png"
    fo.draw.draw_structure(chain5_structure, filename=path)
    assert path.exists()
    assert path.stat().st_size > 100


def test_theory_enumeration():
    x, y = fo.symbols("x y")
    sig = fo.Signature(relations={"leq": 2})
    refl = fo.forall(x, fo.RelSymbol("leq", 2)(x, x))
    T = fo.Theory(sig, axioms=[refl])
    models = list(T.models_of_cardinality(2))
    assert len(models) >= 1


def test_structure_satisfies_method(b2_structure):
    x = fo.symbols("x")
    leq = fo.RelSymbol("leq", 2)
    assert b2_structure.satisfies(fo.forall(x, leq(x, x)))
