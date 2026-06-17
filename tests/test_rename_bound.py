"""rename_bound and subs method tests."""

import fopy as fo


def test_rename_bound_quantifier():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.eq(x, y))
    g = fo.rename_bound(f, x, y)
    assert isinstance(g, fo.ForAll)
    assert g.var != x


def test_formula_subs_method():
    x = fo.symbols("x")
    f = fo.eq(x, x)
    g = f.subs({x: fo.symbols("y")})
    assert fo.simplify(g) == fo.true_formula()


def test_formula_satisfy_method():
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    assert leq(x, y).satisfy(s, {x: 0, y: 1})
