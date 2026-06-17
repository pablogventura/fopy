"""Printing tests."""

import fopy as fo


def test_sstr_quantifier():
    x = fo.symbols("x")
    f = fo.forall(x, fo.Atom("P", (x,)))
    assert fo.sstr(f).startswith("forall")


def test_latex_quantifier():
    x = fo.symbols("x")
    f = fo.forall(x, fo.Atom("P", (x,)))
    tex = fo.latex(f)
    assert "\\forall" in tex


def test_pprint_short():
    x, y = fo.symbols("x y")
    text = fo.pprint(fo.eq(x, y))
    assert "x" in text


def test_subscript_latex():
    v = fo.Variable.from_index(2)
    assert "x_{" in fo.latex(v) or "x" in fo.latex(v)
