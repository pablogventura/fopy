"""Substitution and renaming — extensive cases."""

from __future__ import annotations

import pytest

import fopy as fo


def test_substitute_variable_to_term():
    x, y = fo.symbols("x y")
    f = fo.Atom("P", (x,))
    g = fo.substitute(f, {x: y})
    assert isinstance(g, fo.Atom)


def test_substitute_under_forall_no_capture():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.Atom("P", (x,)))
    g = fo.substitute(f, {x: z})
    assert isinstance(g, fo.ForAll)
    assert g.var != x


def test_substitute_mapping_bound_var_renames():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.eq(x, y))
    g = fo.substitute(f, {x: y})
    assert isinstance(g, fo.ForAll)


def test_subs_simplifies():
    x = fo.symbols("x")
    f = fo.eq(x, x)
    assert fo.subs(f, {x: x}) == fo.true_formula()


def test_rename_bound_forall():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.eq(x, z))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, fo.ForAll)
    assert g.var != x


def test_rename_bound_exists():
    x, y = fo.symbols("x y")
    f = fo.exists(x, fo.Atom("P", (x,)))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, fo.Exists)


def test_rename_bound_noop_on_formula():
    x, y = fo.symbols("x y")
    f = fo.eq(x, y)
    assert fo.rename_bound(f, x, y) == f


def test_free_vars_nested():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.exists(y, fo.eq(x, z)))
    assert z in fo.free_vars(f)
    assert x in fo.bound_vars(f)


def test_bound_vars_union():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    assert fo.bound_vars(f) == {x, y}


@pytest.mark.parametrize("depth", range(1, 5))
def test_nested_quantifier_substitute(depth: int):
    x = fo.symbols("x")
    f: fo.Formula = fo.Atom("P", (x,))
    for i in range(depth):
        v = fo.Variable(f"x{i}")
        f = fo.forall(v, f)
    g = fo.substitute(f, {x: fo.Constant("c")})
    assert g is not None
