"""Formula connective and method coverage."""

import fopy as fo
from fopy.formulas import And, Or


def test_implication_operators():
    x, y = fo.symbols("x y")
    a = fo.Atom("P", (x,))
    b = fo.Atom("Q", (y,))
    assert isinstance(a >> b, Or)
    assert isinstance(b << a, Or)


def test_xor_connective():
    x = fo.symbols("x")
    a = fo.Atom("P", (x,))
    b = fo.Atom("Q", (x,))
    assert isinstance(a ^ b, Or)


def test_and_or_hash():
    x = fo.symbols("x")
    a = fo.Atom("P", (x,))
    b = fo.Atom("Q", (x,))
    c = a & b
    assert hash(And(frozenset({a, b}))) == hash(c)
    assert hash(c) == hash(b & a)


def test_formula_bound_vars_method():
    x, y = fo.symbols("x y")
    f = fo.forall(x, fo.exists(y, fo.eq(x, y)))
    assert x in f.bound_vars()
    assert y in f.bound_vars()


def test_term_free_vars_constant():
    c = fo.Constant("a")
    assert c.free_vars() == set()
