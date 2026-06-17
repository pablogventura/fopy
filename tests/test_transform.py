"""Substitution and variable analysis."""

import fopy as fo


def test_substitute_capture_avoidance():
    x, y = fo.symbols("x y")
    body = fo.exists(y, fo.eq(x, y))
    f = fo.forall(x, body)
    g = fo.substitute(f, {x: y})
    assert isinstance(g, fo.ForAll)
    assert g.var != y


def test_free_bound_vars():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    assert x in fo.bound_vars(f)
    assert y in fo.bound_vars(f)
    assert fo.free_vars(f) == set()
