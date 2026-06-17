"""Transform module extended coverage."""

import fopy as fo


def test_rename_bound_exists():
    x, y = fo.symbols("x y")
    f = fo.exists(x, fo.eq(x, y))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, fo.Exists)


def test_rename_bound_nested():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.exists(y, fo.eq(x, z)))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, fo.ForAll)


def test_substitute_atom():
    x, y = fo.symbols("x y")
    f = fo.Atom("R", (x,))
    g = fo.substitute(f, {x: y})
    assert isinstance(g, fo.Atom)


def test_free_vars_implication():
    x, y = fo.symbols("x y")
    f = fo.Atom("P", (x,)) >> fo.Atom("Q", (y,))
    assert x in fo.free_vars(f)
    assert y in fo.free_vars(f)
