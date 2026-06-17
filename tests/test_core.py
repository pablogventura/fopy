"""Tests for core API and public imports."""

import fopy as fo


def test_version():
    assert fo.__version__ == "0.1.0"


def test_symbols_and_quantifiers():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    assert isinstance(f, fo.ForAll)
    assert x in fo.bound_vars(f)
    assert fo.free_vars(f) == set()


def test_boolean_simplification():
    x = fo.symbols("x")
    a = fo.eq(x, x)
    b = ~a | fo.eq(x, x)
    assert fo.simplify(b) == fo.true_formula()


def test_latex_and_sstr():
    x, y = fo.symbols("x y")
    f = fo.eq(x, y)
    assert "x" in fo.sstr(f)
    assert "x" in fo.latex(f)
